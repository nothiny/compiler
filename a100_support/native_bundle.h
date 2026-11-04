/* Shared native input loader ABI. No Python headers or runtime dependency. */
#ifndef A100_NATIVE_BUNDLE_H
#define A100_NATIVE_BUNDLE_H
#include <stddef.h>
#include <stdint.h>
struct a100_view {
  unsigned char *data;
  uint32_t dtype,ndim,flags;
  int64_t *shape,*strides;
  unsigned char *storage;
  uint64_t storage_size;
};
struct a100_scalar {uint32_t dtype,size;uint64_t bits;};
struct a100_bundle {
  int fd;
  size_t size;
  unsigned char *mapping;
  uint32_t nviews,nscalars,nrelocations;
  struct a100_view *views;
  struct a100_scalar *scalars;
  uint64_t *relocations,*original_addresses;
};
int a100_bundle_open(struct a100_bundle *,const char *path);
int a100_bundle_close(struct a100_bundle *);
#endif
