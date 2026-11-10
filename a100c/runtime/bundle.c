/* bundle.c -- a100-native-io/v1 bundle reader for the native runtime.
 *
 * Implements the declared argument layout both sides derive from (F046/F047):
 * views with dtype/shape/strides/offset over storage payloads, typed scalars,
 * and pointer-table relocations patched on open and restored on close.  The
 * whole image is validated before the first byte is written, so a bundle that
 * violates the format is rejected before execution and the file is left
 * untouched (recorded refusal, never a wrong result).
 *
 * Image layout (little-endian; produced by a100_support/native_io.pack_case):
 *   32   : header  magic[8] "A100IO01", u32 version=1, u32 nstorage, u32
 *          nviews, u32 nscalars, u32 nrelocations, u32 reserved=0
 *   +16*nstorage : storage rows (u64 file offset, u64 size)
 *   per view     : u32 storage, u32 dtype, u32 ndim, u32 flags(bit0=output),
 *          i64 offset, then ndim*i64 shape, then ndim*i64 strides
 *   per scalar   : u32 dtype, u32 size, u64 bits
 *   per reloc    : u32 table view index, u32 target view index, u64 entry,
 *          i64 byte_offset
 * Storage payloads follow the metadata, 64-byte aligned.
 */
#include "a100rt.h"

#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

/* Rejection reason codes; a100rt_reject_reason() maps them to names. */
enum {
  A100RT_R_OPEN = 1,
  A100RT_R_SIZE,
  A100RT_R_MAGIC,
  A100RT_R_VERSION,
  A100RT_R_RESERVED,
  A100RT_R_MAP,
  A100RT_R_STORAGE_BOUNDS,
  A100RT_R_COUNT_BOUNDS,
  A100RT_R_ALLOC,
  A100RT_R_VIEW_TRUNCATED,
  A100RT_R_VIEW_STORAGE,
  A100RT_R_VIEW_DTYPE,
  A100RT_R_VIEW_OFFSET,
  A100RT_R_VIEW_DIM,
  A100RT_R_VIEW_REACH,
  A100RT_R_VIEW_FLAGS,
  A100RT_R_SCALAR_TRUNCATED,
  A100RT_R_SCALAR_WIDTH,
  A100RT_R_RELOC_TRUNCATED,
  A100RT_R_RELOC_VIEW,
  A100RT_R_RELOC_TABLE_WIDTH,
  A100RT_R_RELOC_TABLE_OUTPUT,
  A100RT_R_RELOC_ENTRY,
  A100RT_R_RELOC_OFFSET,
  A100RT_R_STORAGE_OVERLAPS_METADATA,
};

const char *a100rt_reject_reason(int code) {
  switch (code) {
  case A100RT_R_OPEN: return "open";
  case A100RT_R_SIZE: return "size";
  case A100RT_R_MAGIC: return "magic";
  case A100RT_R_VERSION: return "version";
  case A100RT_R_RESERVED: return "reserved";
  case A100RT_R_MAP: return "map";
  case A100RT_R_STORAGE_BOUNDS: return "storage-bounds";
  case A100RT_R_COUNT_BOUNDS: return "count-bounds";
  case A100RT_R_ALLOC: return "alloc";
  case A100RT_R_VIEW_TRUNCATED: return "view-truncated";
  case A100RT_R_VIEW_STORAGE: return "view-storage";
  case A100RT_R_VIEW_DTYPE: return "view-dtype";
  case A100RT_R_VIEW_OFFSET: return "view-offset";
  case A100RT_R_VIEW_DIM: return "view-dim";
  case A100RT_R_VIEW_REACH: return "view-reach";
  case A100RT_R_VIEW_FLAGS: return "view-flags";
  case A100RT_R_SCALAR_TRUNCATED: return "scalar-truncated";
  case A100RT_R_SCALAR_WIDTH: return "scalar-width";
  case A100RT_R_RELOC_TRUNCATED: return "reloc-truncated";
  case A100RT_R_RELOC_VIEW: return "reloc-view";
  case A100RT_R_RELOC_TABLE_WIDTH: return "reloc-table-width";
  case A100RT_R_RELOC_TABLE_OUTPUT: return "reloc-table-output";
  case A100RT_R_RELOC_ENTRY: return "reloc-entry";
  case A100RT_R_RELOC_OFFSET: return "reloc-offset";
  case A100RT_R_STORAGE_OVERLAPS_METADATA: return "storage-overlaps-metadata";
  default: return "unknown";
  }
}

static int bounds(size_t n, uint64_t off, uint64_t len) {
  return off <= (uint64_t)n && len <= (uint64_t)n - off;
}

static uint64_t rd_u64(const unsigned char *p) {
  uint64_t v;
  memcpy(&v, p, 8);
  return v;
}

static uint32_t rd_u32(const unsigned char *p) {
  uint32_t v;
  memcpy(&v, p, 4);
  return v;
}

static int dtype_itemsize(uint32_t dtype) {
  static const int sizes[] = {0, 1, 1, 1, 2, 2, 4, 4, 8, 8, 2, 2, 4, 8};
  return dtype < sizeof(sizes) / sizeof(sizes[0]) ? sizes[dtype] : 0;
}

int a100rt_bundle_open(struct a100rt_bundle *b, const char *path, int *reason) {
  int failure = 0;
  struct stat st;

  memset(b, 0, sizeof *b);
  b->fd = -1;
  *reason = 0;

  b->fd = open(path, O_RDWR);
  if (b->fd < 0 || fstat(b->fd, &st)) {
    failure = A100RT_R_OPEN;
    goto fail;
  }
  if (st.st_size < 32) {
    failure = A100RT_R_SIZE;
    goto fail;
  }
  b->size = (uint64_t)st.st_size;
  b->mapping = mmap(0, (size_t)b->size, PROT_READ | PROT_WRITE, MAP_SHARED, b->fd, 0);
  if (b->mapping == MAP_FAILED) {
    b->mapping = 0;
    failure = A100RT_R_MAP;
    goto fail;
  }

  unsigned char *p = b->mapping;
  if (memcmp(p, "A100IO01", 8)) {
    failure = A100RT_R_MAGIC;
    goto fail;
  }
  if (rd_u32(p + 8) != 1) {
    failure = A100RT_R_VERSION;
    goto fail;
  }
  if (rd_u32(p + 28) != 0) {
    failure = A100RT_R_RESERVED;
    goto fail;
  }
  uint32_t nstorage = rd_u32(p + 12);
  b->nviews = rd_u32(p + 16);
  b->nscalars = rd_u32(p + 20);
  b->nrelocations = rd_u32(p + 24);

  if (!bounds(b->size, 32, (uint64_t)nstorage * 16)) {
    failure = A100RT_R_STORAGE_BOUNDS;
    goto fail;
  }
  const unsigned char *storages = p + 32;
  for (uint32_t i = 0; i < nstorage; i++)
    if (!bounds(b->size, rd_u64(storages + 16 * i), rd_u64(storages + 16 * i + 8))) {
      failure = A100RT_R_STORAGE_BOUNDS;
      goto fail;
    }
  if ((uint64_t)b->nviews > b->size / 24 || (uint64_t)b->nscalars > b->size / 16 ||
      (uint64_t)b->nrelocations > b->size / 24) {
    failure = A100RT_R_COUNT_BOUNDS;
    goto fail;
  }
  b->views = calloc(b->nviews ? b->nviews : 1, sizeof *b->views);
  b->originals = calloc(b->nrelocations ? b->nrelocations : 1, sizeof *b->originals);
  if (!b->views || !b->originals) {
    failure = A100RT_R_ALLOC;
    goto fail;
  }

  uint64_t cursor = 32 + (uint64_t)nstorage * 16;
  for (uint32_t i = 0; i < b->nviews; i++) {
    if (!bounds(b->size, cursor, 24)) {
      failure = A100RT_R_VIEW_TRUNCATED;
      goto fail;
    }
    const unsigned char *v = p + cursor;
    uint32_t storage = rd_u32(v), dtype = rd_u32(v + 4), ndim = rd_u32(v + 8), flags = rd_u32(v + 12);
    int64_t offset = (int64_t)rd_u64(v + 16);
    if (storage >= nstorage) {
      failure = A100RT_R_VIEW_STORAGE;
      goto fail;
    }
    if (!dtype_itemsize(dtype)) {
      failure = A100RT_R_VIEW_DTYPE;
      goto fail;
    }
    if (flags & ~A100RT_VIEW_OUTPUT) {
      failure = A100RT_R_VIEW_FLAGS;
      goto fail;
    }
    if (!bounds(b->size, cursor + 24, (uint64_t)ndim * 16)) {
      failure = A100RT_R_VIEW_TRUNCATED;
      goto fail;
    }
    uint64_t data = rd_u64(storages + 16 * storage), ssize = rd_u64(storages + 16 * storage + 8);
    if (offset < 0 || (uint64_t)offset > ssize) {
      failure = A100RT_R_VIEW_OFFSET;
      goto fail;
    }
    struct a100rt_view *view = &b->views[i];
    view->storage = p + data;
    view->storage_size = ssize;
    view->data = p + data + offset;
    view->dtype = dtype;
    view->ndim = ndim;
    view->flags = flags;
    view->shape = (int64_t *)(v + 24);
    view->strides = (int64_t *)(v + 24 + (size_t)ndim * 8);
    __int128 low = offset, high = offset;
    int empty = 0;
    for (uint32_t axis = 0; axis < ndim; axis++) {
      int64_t dim = view->shape[axis];
      if (dim < 0) {
        failure = A100RT_R_VIEW_DIM;
        goto fail;
      }
      if (!dim)
        empty = 1;
      __int128 extent = (__int128)(dim ? dim - 1 : 0) * view->strides[axis];
      if (extent < 0)
        low += extent;
      else
        high += extent;
    }
    if (!empty && (low < 0 || high + dtype_itemsize(dtype) > (__int128)ssize)) {
      failure = A100RT_R_VIEW_REACH;
      goto fail;
    }
    cursor += 24 + (uint64_t)ndim * 16;
  }

  if (!bounds(b->size, cursor, (uint64_t)b->nscalars * 16)) {
    failure = A100RT_R_SCALAR_TRUNCATED;
    goto fail;
  }
  b->scalars = (struct a100rt_scalar *)(p + cursor);
  cursor += (uint64_t)b->nscalars * 16;
  for (uint32_t i = 0; i < b->nscalars; i++)
    if (!dtype_itemsize(b->scalars[i].dtype) ||
        (uint32_t)dtype_itemsize(b->scalars[i].dtype) != b->scalars[i].size) {
      failure = A100RT_R_SCALAR_WIDTH;
      goto fail;
    }

  if (!bounds(b->size, cursor, (uint64_t)b->nrelocations * 24)) {
    failure = A100RT_R_RELOC_TRUNCATED;
    goto fail;
  }
  b->relocations = p + cursor;
  uint64_t metadata_end = cursor + (uint64_t)b->nrelocations * 24;
  for (uint32_t i = 0; i < nstorage; i++)
    if (rd_u64(storages + 16 * i) < metadata_end) {
      failure = A100RT_R_STORAGE_OVERLAPS_METADATA;
      goto fail;
    }

  /* The writable span: the union of the storage payloads.  The metadata
   * and the relocation records never change after the one-time open
   * patch (the patched pointer slots live INSIDE the storages) and the
   * operator writes only its views plus its separate workspace -- so
   * the repeat loop's snapshot restore and equality check only need
   * this span, never the whole image (the byte-wise loops over the
   * full bundle were the small cases' per-call floor). */
  b->writable_start = 0;
  b->writable_end = 0;
  for (uint32_t i = 0; i < nstorage; i++) {
    uint64_t off = rd_u64(storages + 16 * i);
    uint64_t sz = rd_u64(storages + 16 * i + 8);
    if (!b->writable_end || off + sz > b->writable_end)
      b->writable_end = off + sz;
    if (!b->writable_start || off < b->writable_start)
      b->writable_start = off;
  }

  /* Validate every relocation record before patching anything. */
  for (uint32_t i = 0; i < b->nrelocations; i++) {
    const unsigned char *r = b->relocations + (size_t)i * 24;
    uint32_t table = rd_u32(r), target = rd_u32(r + 4);
    uint64_t entry = rd_u64(r + 8);
    int64_t off = (int64_t)rd_u64(r + 16);
    if (table >= b->nviews || target >= b->nviews) {
      failure = A100RT_R_RELOC_VIEW;
      goto fail;
    }
    const struct a100rt_view *t = &b->views[table], *dst = &b->views[target];
    if (t->dtype != A100RT_DTYPE_INT64 && t->dtype != A100RT_DTYPE_UINT64) {
      failure = A100RT_R_RELOC_TABLE_WIDTH;
      goto fail;
    }
    if (t->flags & A100RT_VIEW_OUTPUT) {
      /* Pointer tables are process-local inputs, not address outputs. */
      failure = A100RT_R_RELOC_TABLE_OUTPUT;
      goto fail;
    }
    uint64_t tableoff = (uint64_t)(t->data - t->storage);
    if (entry > UINT64_MAX / 8 || !bounds(t->storage_size, tableoff + entry * 8, 8)) {
      failure = A100RT_R_RELOC_ENTRY;
      goto fail;
    }
    if (off < 0 || (uint64_t)off > dst->storage_size - (uint64_t)(dst->data - dst->storage)) {
      failure = A100RT_R_RELOC_OFFSET;
      goto fail;
    }
  }

  /* All records validated: patch the pointer tables now (and only now). */
  for (uint32_t i = 0; i < b->nrelocations; i++) {
    const unsigned char *r = b->relocations + (size_t)i * 24;
    uint32_t table = rd_u32(r), target = rd_u32(r + 4);
    uint64_t entry = rd_u64(r + 8);
    int64_t off = (int64_t)rd_u64(r + 16);
    struct a100rt_view *t = &b->views[table], *dst = &b->views[target];
    uint64_t pointer = (uint64_t)(uintptr_t)(dst->data + off);
    unsigned char *slot = t->data + entry * 8;
    memcpy(&b->originals[i], slot, 8);
    memcpy(slot, &pointer, 8);
  }
  return 0;

fail:
  /* A rejected bundle was never written: patching happens only after every
   * record validated.  Unmap and leave the file exactly as it was. */
  if (b->mapping)
    munmap(b->mapping, (size_t)b->size);
  if (b->fd >= 0)
    close(b->fd);
  free(b->views);
  free(b->originals);
  memset(b, 0, sizeof *b);
  b->fd = -1;
  *reason = failure;
  return -1;
}

void a100rt_bundle_writable(const struct a100rt_bundle *b, uint64_t *start,
                             uint64_t *end) {
  /* The storage-union span (empty when the bundle has no storages). */
  *start = b->writable_start;
  *end = b->writable_end;
}

int a100rt_bundle_close(struct a100rt_bundle *b) {
  if (!b->mapping)
    return -1;
  for (uint32_t i = 0; i < b->nrelocations; i++) {
    const unsigned char *r = b->relocations + (size_t)i * 24;
    uint32_t table = rd_u32(r);
    uint64_t entry = rd_u64(r + 8);
    memcpy(b->views[table].data + entry * 8, &b->originals[i], 8);
  }
  int status = msync(b->mapping, (size_t)b->size, MS_SYNC);
  munmap(b->mapping, (size_t)b->size);
  close(b->fd);
  free(b->views);
  free(b->originals);
  memset(b, 0, sizeof *b);
  b->fd = -1;
  return status ? -1 : 0;
}
