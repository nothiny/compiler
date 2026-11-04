/* pool.c -- persistent pthread worker pool for the native runtime.
 *
 * One pool per process, created once and reused across every operator call
 * (F018/F019/F053): 1/2/4/8 compute workers, distinct guest threads, observed
 * once per process.  Workers park between calls; each call releases them
 * through the "go" barrier and collects them at "done".  Cross-worker stage
 * synchronization inside one call uses the "stage" barrier plus C11 atomics
 * (F054/A006: explicit synchronization, no assumed coherence).
 *
 * Workspace: one shared region and one padded, 64-byte-aligned thread-private
 * region per worker, allocated once and zeroed by the runtime before every
 * call (buffers are re-initialized between repeated calls in one process).
 */
#define _GNU_SOURCE
#include "a100rt.h"

#include <pthread.h>
#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>
#include <sys/syscall.h>
#include <unistd.h>

struct a100rt_pool {
  pthread_t threads[A100RT_MAX_WORKERS];
  pthread_barrier_t go;   /* workers + main: release one call */
  pthread_barrier_t done; /* workers + main: collect one call */
  pthread_barrier_t stage; /* workers only: operator stage sync */
  pthread_mutex_t startup_mutex;
  pthread_cond_t startup_cond;
  int startup_ready;
  _Atomic int stop;
  int workers;
  uint64_t tids[A100RT_MAX_WORKERS];
  struct a100rt_launch launches[A100RT_MAX_WORKERS];
  _Alignas(64) struct a100rt_stats stats[A100RT_MAX_WORKERS];
  unsigned char *private_base;
  uint64_t private_bytes;
  void *shared;
  uint64_t shared_bytes;
};

static _Atomic int pool_initializations;

static uint64_t round_up_64(uint64_t n) { return (n + 63) & ~(uint64_t)63; }

static void *a100rt_worker_main(void *opaque) {
  struct a100rt_launch *launch = opaque;
  struct a100rt_pool *pool = launch->runtime;
  uint32_t id = launch->worker_id;
  pool->tids[id] = (uint64_t)syscall(SYS_gettid);
  /* Park until every worker exists: barrier counts are fixed at init, so no
   * worker may touch them before the pool is complete. */
  pthread_mutex_lock(&pool->startup_mutex);
  while (!pool->startup_ready)
    pthread_cond_wait(&pool->startup_cond, &pool->startup_mutex);
  pthread_mutex_unlock(&pool->startup_mutex);
  for (;;) {
    pthread_barrier_wait(&pool->go);
    if (atomic_load(&pool->stop))
      break;
    operator_entry(launch);
    pthread_barrier_wait(&pool->done);
  }
  return NULL;
}

int a100rt_pool_create(struct a100rt_pool **out, int workers,
                       const struct a100rt_bundle *bundle,
                       uint64_t private_bytes, uint64_t shared_bytes) {
  if (!out || !bundle)
    return -1;
  if (!(workers == 1 || workers == 2 || workers == 4 || workers == 8))
    return -1;
  int have_go = 0, have_done = 0, have_stage = 0, have_mutex = 0, have_cond = 0;
  struct a100rt_pool *pool = aligned_alloc(64, round_up_64(sizeof *pool));
  if (!pool)
    return -1;
  memset(pool, 0, sizeof *pool);
  pool->workers = workers;
  pool->private_bytes = round_up_64(private_bytes ? private_bytes : 64);
  pool->shared_bytes = round_up_64(shared_bytes ? shared_bytes : 64);
  pool->shared = aligned_alloc(64, pool->shared_bytes);
  pool->private_base = aligned_alloc(64, pool->private_bytes * (uint64_t)workers);
  if (!pool->shared || !pool->private_base)
    goto fail;
  memset(pool->shared, 0, pool->shared_bytes);
  memset(pool->private_base, 0, pool->private_bytes * (uint64_t)workers);
  if (pthread_barrier_init(&pool->go, 0, (unsigned)workers + 1))
    goto fail;
  have_go = 1;
  if (pthread_barrier_init(&pool->done, 0, (unsigned)workers + 1))
    goto fail;
  have_done = 1;
  if (pthread_barrier_init(&pool->stage, 0, (unsigned)workers))
    goto fail;
  have_stage = 1;
  if (pthread_mutex_init(&pool->startup_mutex, 0))
    goto fail;
  have_mutex = 1;
  if (pthread_cond_init(&pool->startup_cond, 0))
    goto fail;
  have_cond = 1;
  atomic_store(&pool->stop, 0);
  for (int w = 0; w < workers; w++) {
    struct a100rt_launch *launch = &pool->launches[w];
    launch->bundle = bundle;
    launch->workspace_shared = pool->shared;
    launch->workspace_private = pool->private_base + pool->private_bytes * (uint64_t)w;
    launch->stats = &pool->stats[w];
    launch->runtime = pool;
    launch->worker_id = (uint32_t)w;
    launch->worker_count = (uint32_t)workers;
  }
  for (int w = 0; w < workers; w++)
    if (pthread_create(&pool->threads[w], 0, a100rt_worker_main, &pool->launches[w])) {
      /* Workers created so far are parked on the startup condvar, never on a
       * barrier: release them with stop set and join them. */
      atomic_store(&pool->stop, 1);
      pthread_mutex_lock(&pool->startup_mutex);
      pool->startup_ready = 1;
      pthread_cond_broadcast(&pool->startup_cond);
      pthread_mutex_unlock(&pool->startup_mutex);
      for (int j = 0; j < w; j++)
        pthread_join(pool->threads[j], 0);
      goto fail;
    }
  pthread_mutex_lock(&pool->startup_mutex);
  pool->startup_ready = 1;
  pthread_cond_broadcast(&pool->startup_cond);
  pthread_mutex_unlock(&pool->startup_mutex);
  atomic_fetch_add(&pool_initializations, 1);
  *out = pool;
  return 0;

fail:
  if (have_cond)
    pthread_cond_destroy(&pool->startup_cond);
  if (have_mutex)
    pthread_mutex_destroy(&pool->startup_mutex);
  if (have_stage)
    pthread_barrier_destroy(&pool->stage);
  if (have_done)
    pthread_barrier_destroy(&pool->done);
  if (have_go)
    pthread_barrier_destroy(&pool->go);
  free(pool->shared);
  free(pool->private_base);
  free(pool);
  return -1;
}

/* One operator call across all workers.  Workspace and stats are zeroed before
 * the release: every call starts from re-initialized buffers. */
void a100rt_pool_call(struct a100rt_pool *pool) {
  memset(pool->shared, 0, pool->shared_bytes);
  memset(pool->private_base, 0, pool->private_bytes * (uint64_t)pool->workers);
  memset(pool->stats, 0, sizeof pool->stats);
  pthread_barrier_wait(&pool->go);
  pthread_barrier_wait(&pool->done);
}

void a100rt_pool_observe(const struct a100rt_pool *pool, uint64_t *tids, uint64_t *items) {
  for (int w = 0; w < pool->workers; w++) {
    tids[w] = pool->tids[w];
    items[w] = pool->stats[w].items;
  }
}

void a100rt_pool_destroy(struct a100rt_pool *pool) {
  if (!pool)
    return;
  atomic_store(&pool->stop, 1);
  pthread_barrier_wait(&pool->go);
  for (int w = 0; w < pool->workers; w++)
    pthread_join(pool->threads[w], 0);
  pthread_cond_destroy(&pool->startup_cond);
  pthread_mutex_destroy(&pool->startup_mutex);
  pthread_barrier_destroy(&pool->stage);
  pthread_barrier_destroy(&pool->done);
  pthread_barrier_destroy(&pool->go);
  free(pool->shared);
  free(pool->private_base);
  free(pool);
}

void a100rt_stage_barrier(const struct a100rt_launch *launch) {
  struct a100rt_pool *pool = launch->runtime;
  pthread_barrier_wait(&pool->stage);
}

uint64_t a100rt_pool_initializations(void) {
  return (uint64_t)atomic_load(&pool_initializations);
}
