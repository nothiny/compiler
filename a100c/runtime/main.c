/* main.c -- process entry for the native single-operator executable.
 *
 * The runtime owns main (F043: the generated program provides operator_entry,
 * not a process shell).  Flow: parse --bundle/--threads/--repeats, open and
 * validate the bundle (reject before execution on any format violation),
 * snapshot the mapped image, create the persistent pool once, run the operator
 * --repeats times (restoring the snapshot before each repeat so every repeat
 * is an independent execution of the same case), then observe the pool,
 * close the bundle (restoring relocated pointer words and syncing outputs) and
 * print one status JSON line for the host.
 *
 * Exit codes: 0 ok, 2 usage, 3 bundle rejected, 4 resource, 5 repeat
 * mismatch, 6 sync failure (a100rt.h).
 */
#define _GNU_SOURCE
#include "a100rt.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Workspace defaults; an operator program defines its own to override. */
__attribute__((weak)) uint64_t operator_workspace_private(void) { return 4096; }
__attribute__((weak)) uint64_t operator_workspace_shared(void) { return 1u << 16; }

static int usage(void) {
  fprintf(stderr, "usage: operator_exec --bundle <path> --threads <n> [--repeats <k>]\n"
                  "  --threads  1, 2, 4 or 8 compute workers\n"
                  "  --repeats  k independent executions of the same case (default 1)\n");
  return A100RT_EXIT_USAGE;
}

static int parse_u32(const char *text, uint32_t *out) {
  char *end = 0;
  unsigned long value;
  if (!text[0])
    return -1;
  value = strtoul(text, &end, 10);
  if (!end || *end || value > 0xFFFFFFFFul)
    return -1;
  *out = (uint32_t)value;
  return 0;
}

static void print_rejected(int reason) {
  printf("{\"runtime\":\"a100rt/v1\",\"status\":\"rejected\",\"reason\":\"%s\"}\n",
         a100rt_reject_reason(reason));
}

int main(int argc, char **argv) {
  const char *bundle_path = 0;
  uint32_t threads = 0, repeats = 1;
  int have_threads = 0;

  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--bundle") && i + 1 < argc && !bundle_path) {
      bundle_path = argv[++i];
    } else if (!strcmp(argv[i], "--threads") && i + 1 < argc && !have_threads) {
      if (parse_u32(argv[++i], &threads))
        return usage();
      have_threads = 1;
    } else if (!strcmp(argv[i], "--repeats") && i + 1 < argc) {
      if (parse_u32(argv[++i], &repeats))
        return usage();
    } else {
      return usage();
    }
  }
  if (!bundle_path || !have_threads)
    return usage();
  if (!(threads == 1 || threads == 2 || threads == 4 || threads == 8))
    return usage();
  if (repeats < 1)
    return usage();

  struct a100rt_bundle bundle;
  int reason = 0;
  if (a100rt_bundle_open(&bundle, bundle_path, &reason)) {
    print_rejected(reason);
    return A100RT_EXIT_REJECTED;
  }
  uint64_t bundle_bytes = bundle.size;

  /* Input snapshot: taken after open (pointer tables already patched), restored
   * before every later repeat so each repeat is an independent execution. */
  unsigned char *snapshot = malloc(bundle.size);
  unsigned char *first_result = malloc(bundle.size);
  if (!snapshot || !first_result) {
    printf("{\"runtime\":\"a100rt/v1\",\"status\":\"resource\",\"reason\":\"snapshot\"}\n");
    return A100RT_EXIT_RESOURCE;
  }
  memcpy(snapshot, bundle.mapping, bundle.size);

  struct a100rt_pool *pool = 0;
  if (a100rt_pool_create(&pool, (int)threads, &bundle, operator_workspace_private(),
                         operator_workspace_shared())) {
    printf("{\"runtime\":\"a100rt/v1\",\"status\":\"resource\",\"reason\":\"pool\"}\n");
    return A100RT_EXIT_RESOURCE;
  }

  /* The repeat loop's restore/compare runs over the WRITABLE span only
   * (the metadata and the patched pointer slots never change after
   * open; the operator writes only its views and its separate
   * workspace), word-wide with a byte-exact tail: the whole-image
   * byte-wise loops were the small cases' per-call floor (a [4]-element
   * instance spent ~97% of its per-call instructions copying and
   * comparing bytes that never change).  The storages are 64-byte
   * aligned and mmap/malloc bases are word-aligned, so the word loops
   * read aligned. */
  uint64_t ws = 0, we = 0;
  a100rt_bundle_writable(&bundle, &ws, &we);
  uint64_t wlen = we > ws ? we - ws : 0;
  unsigned char *wbase = bundle.mapping + ws;
  unsigned char *wsnap = snapshot + ws;
  unsigned char *wfirst = first_result + ws;
  int repeats_equal = 1;
  for (uint32_t r = 0; r < repeats; r++) {
    if (r && wlen) {
      uint64_t words = wlen >> 3, i = wlen & ~(uint64_t)7;
      uint64_t *d = (uint64_t *)wbase;
      const uint64_t *src = (const uint64_t *)wsnap;
      while (words--)
        *d++ = *src++;
      for (; i < wlen; i++)
        wbase[i] = wsnap[i];
    }
    a100rt_pool_call(pool);
    if (!r) {
      uint64_t words = wlen >> 3, i = wlen & ~(uint64_t)7;
      uint64_t *d = (uint64_t *)wfirst;
      const uint64_t *src = (const uint64_t *)wbase;
      while (words--)
        *d++ = *src++;
      for (; i < wlen; i++)
        wfirst[i] = wbase[i];
    } else {
      uint64_t words = wlen >> 3, i = wlen & ~(uint64_t)7;
      const uint64_t *a = (const uint64_t *)wbase;
      const uint64_t *b = (const uint64_t *)wfirst;
      while (words--)
        if (*a++ != *b++) {
          repeats_equal = 0;
          break;
        }
      if (repeats_equal)
        for (; i < wlen; i++)
          if (wbase[i] != wfirst[i]) {
            repeats_equal = 0;
            break;
          }
    }
  }

  uint64_t tids[A100RT_MAX_WORKERS], items[A100RT_MAX_WORKERS];
  a100rt_pool_observe(pool, tids, items);
  uint64_t pool_inits = a100rt_pool_initializations();
  a100rt_pool_destroy(pool);
  free(snapshot);
  free(first_result);

  int close_status = a100rt_bundle_close(&bundle);
  const char *status = close_status ? "sync-failed" : (repeats_equal ? "ok" : "repeat-mismatch");
  printf("{\"runtime\":\"a100rt/v1\",\"status\":\"%s\",\"threads\":%u,\"repeats\":%u,"
         "\"pool_initializations\":%llu,\"repeats_all_equal\":%s,\"workers\":[",
         status, (unsigned)threads, (unsigned)repeats, (unsigned long long)pool_inits,
         repeats_equal ? "true" : "false");
  for (uint32_t w = 0; w < threads; w++)
    printf("%s{\"id\":%u,\"guest_tid\":%llu,\"items\":%llu}", w ? "," : "", (unsigned)w,
           (unsigned long long)tids[w], (unsigned long long)items[w]);
  printf("],\"bundle_bytes\":%llu}\n", (unsigned long long)bundle_bytes);

  if (close_status)
    return A100RT_EXIT_SYNC;
  if (!repeats_equal)
    return A100RT_EXIT_REPEAT_MISMATCH;
  return A100RT_EXIT_OK;
}
