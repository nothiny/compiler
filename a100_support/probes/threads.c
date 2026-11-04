#define _GNU_SOURCE
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <sys/syscall.h>

#define N 32771
#define MAX_WORKERS 8
extern void probe_rvv_add(int32_t *,const int32_t *,const int32_t *,size_t);
extern uint64_t probe_vlenb(void);
static int32_t a[N],b[N],out[N];
struct slot { int64_t sum; uint64_t begin,phase1_end,phase2_begin,end,guest_tid; char pad[80]; };
static struct slot partial[MAX_WORKERS] __attribute__((aligned(128)));
static pthread_barrier_t start,stages,done;
static _Atomic int stop;
static int workers;
static int64_t total;
static uint64_t ns(void) {
  struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
  return (uint64_t)t.tv_sec*1000000000ULL+t.tv_nsec;
}
static void *worker(void *opaque) {
  size_t id=(uintptr_t)opaque,begin=N*id/workers,end=N*(id+1)/workers;
  partial[id].guest_tid=(uint64_t)syscall(SYS_gettid);
  for (;;) {
    pthread_barrier_wait(&start);
    if (atomic_load(&stop)) break;
    partial[id].begin=ns();
    probe_rvv_add(out+begin,a+begin,b+begin,end-begin);
    int64_t sum=0;
    for (size_t i=begin;i<end;i++) sum+=out[i];
    partial[id].sum=sum;
    partial[id].phase1_end=ns();
    pthread_barrier_wait(&stages);
    if (!id) {
      total=0;for(int j=0;j<workers;j++) total+=partial[j].sum;
    }
    pthread_barrier_wait(&stages);
    partial[id].phase2_begin=ns();
    for (size_t i=begin;i<end;i++) out[i]+=(int32_t)total;
    partial[id].end=ns();
    pthread_barrier_wait(&done);
  }
  return 0;
}
int main(int argc,char **argv) {
  workers=argc>1?atoi(argv[1]):1;
  if (!(workers==1||workers==2||workers==4||workers==8)||probe_vlenb()!=128) return 2;
  int64_t expected_sum=0;
  for (int i=0;i<N;i++) {a[i]=i%7-3;b[i]=i%5-2;expected_sum+=a[i]+b[i];}
  pthread_barrier_init(&start,0,workers+1);
  pthread_barrier_init(&done,0,workers+1);
  pthread_barrier_init(&stages,0,workers);
  pthread_t threads[MAX_WORKERS];
  for (uintptr_t i=0;i<(size_t)workers;i++)
    if(pthread_create(&threads[i],0,worker,(void*)i)) return 2;
  uint64_t elapsed[6];
  for (int repeat=0;repeat<6;repeat++) {
    uint64_t begin=ns();
    pthread_barrier_wait(&start);pthread_barrier_wait(&done);
    elapsed[repeat]=ns()-begin;
    if(total!=expected_sum) return 1;
    for(int i=0;i<N;i++) if(out[i]!=a[i]+b[i]+expected_sum) return 1;
  }
  atomic_store(&stop,1);pthread_barrier_wait(&start);
  for(int i=0;i<workers;i++) pthread_join(threads[i],0);
  printf("{\"probe\":\"persistent_pool_two_stages\",\"environment\":\"qemu-functional\",\"passed\":true,\"threads\":%d,\"pool_initializations\":1,\"warmups\":1,\"samples_ns\":[",workers);
  for(int i=1;i<6;i++) printf("%s%llu",i>1?",":"",(unsigned long long)elapsed[i]);
  printf("],\"ranges\":[");
  for(int i=0;i<workers;i++) printf("%s[%d,%d]",i?",":"",N*i/workers,N*(i+1)/workers);
  printf("],\"worker_units\":\"guest threads, not physical A100 cores\",\"workers\":[");
  for(int i=0;i<workers;i++) printf("%s{\"id\":%d,\"guest_tid\":%llu,\"items\":%d,\"phase1_interval_ns\":[%llu,%llu],\"phase2_interval_ns\":[%llu,%llu]}",
    i?",":"",i,(unsigned long long)partial[i].guest_tid,N*(i+1)/workers-N*i/workers,
    (unsigned long long)partial[i].begin,(unsigned long long)partial[i].phase1_end,
    (unsigned long long)partial[i].phase2_begin,(unsigned long long)partial[i].end);
  puts("]}");return 0;
}
