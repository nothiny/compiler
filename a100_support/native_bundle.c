#include "native_bundle.h"
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

static int bounds(size_t n,uint64_t off,uint64_t len) {return off<=n && len<=n-off;}
static uint64_t u64(const void *p) {uint64_t v;memcpy(&v,p,8);return v;}
static uint32_t u32(const void *p) {uint32_t v;memcpy(&v,p,4);return v;}
static int itemsize(uint32_t dtype) {
  const int sizes[]={0,1,1,1,2,2,4,4,8,8,2,2,4,8};
  return dtype<sizeof(sizes)/sizeof(sizes[0])?sizes[dtype]:0;
}
int a100_bundle_open(struct a100_bundle *b,const char *path) {
  uint32_t patched=0;
  memset(b,0,sizeof(*b));b->fd=-1;
  struct stat st;
  b->fd=open(path,O_RDWR);
  if(b->fd<0 || fstat(b->fd,&st) || st.st_size<32) goto fail;
  b->size=(size_t)st.st_size;
  b->mapping=mmap(0,b->size,PROT_READ|PROT_WRITE,MAP_SHARED,b->fd,0);
  if(b->mapping==MAP_FAILED) {b->mapping=0;goto fail;}
  unsigned char *p=b->mapping;
  if(memcmp(p,"A100IO01",8) || u32(p+8)!=1 || u32(p+28)!=0) goto fail;
  uint32_t nstorage=u32(p+12);
  b->nviews=u32(p+16);b->nscalars=u32(p+20);b->nrelocations=u32(p+24);
  if(!bounds(b->size,32,(uint64_t)nstorage*16)) goto fail;
  unsigned char *storages=p+32;
  size_t cursor=32+(size_t)nstorage*16;
  for(uint32_t i=0;i<nstorage;i++)
    if(!bounds(b->size,u64(storages+16*i),u64(storages+16*i+8))) goto fail;
  if(b->nviews>b->size/24 || b->nscalars>b->size/16 || b->nrelocations>b->size/24) goto fail;
  b->views=calloc(b->nviews?b->nviews:1,sizeof(*b->views));
  b->original_addresses=calloc(b->nrelocations?b->nrelocations:1,8);
  if(!b->views || !b->original_addresses) goto fail;
  for(uint32_t i=0;i<b->nviews;i++) {
    if(!bounds(b->size,cursor,24)) goto fail;
    unsigned char *v=p+cursor;
    uint32_t storage=u32(v),dtype=u32(v+4),ndim=u32(v+8);
    if(storage>=nstorage || !itemsize(dtype) || !bounds(b->size,cursor+24,(uint64_t)ndim*16)) goto fail;
    int64_t offset=(int64_t)u64(v+16);
    struct a100_view *view=&b->views[i];
    uint64_t data=u64(storages+16*storage),size=u64(storages+16*storage+8);
    if(offset<0 || (uint64_t)offset>size) goto fail;
    view->storage=p+data;view->storage_size=size;view->data=p+data+offset;
    view->dtype=dtype;view->ndim=ndim;view->flags=u32(v+12);
    view->shape=(int64_t *)(v+24);view->strides=(int64_t *)(v+24+ndim*8);
    __int128 low=offset,high=offset;int empty=0;
    for(uint32_t axis=0;axis<ndim;axis++) {
      int64_t dim=view->shape[axis];
      if(dim<0) goto fail;
      if(!dim) empty=1;
      __int128 extent=(__int128)(dim?dim-1:0)*view->strides[axis];
      if(extent<0) low+=extent;else high+=extent;
    }
    if(!empty && (low<0 || high+itemsize(dtype)>size)) goto fail;
    cursor+=24+(size_t)ndim*16;
  }
  if(!bounds(b->size,cursor,(uint64_t)b->nscalars*16)) goto fail;
  b->scalars=(struct a100_scalar *)(p+cursor);cursor+=(size_t)b->nscalars*16;
  for(uint32_t i=0;i<b->nscalars;i++)
    if((uint32_t)itemsize(b->scalars[i].dtype)!=b->scalars[i].size) goto fail;
  if(!bounds(b->size,cursor,(uint64_t)b->nrelocations*24)) goto fail;
  b->relocations=(uint64_t *)(p+cursor);
  for(uint32_t i=0;i<nstorage;i++)
    if(u64(storages+16*i)<cursor+(uint64_t)b->nrelocations*24) goto fail;
  for(uint32_t i=0;i<b->nrelocations;i++) {
    unsigned char *r=p+cursor+i*24;
    uint32_t table=u32(r),target=u32(r+4);
    uint64_t entry=u64(r+8);int64_t off=(int64_t)u64(r+16);
    if(table>=b->nviews || target>=b->nviews || off<0) goto fail;
    struct a100_view *t=&b->views[table],*dst=&b->views[target];
    if((t->dtype!=8 && t->dtype!=9) || (t->flags&1) || entry>UINT64_MAX/8) goto fail;
    uint64_t tableoff=(uint64_t)(t->data-t->storage);
    if(entry>(UINT64_MAX-tableoff)/8 || !bounds(t->storage_size,tableoff+entry*8,8) || (uint64_t)off>dst->storage_size-(dst->data-dst->storage)) goto fail;
    uint64_t pointer=(uintptr_t)(dst->data+off);
    b->original_addresses[i]=u64(t->data+entry*8);
    memcpy(t->data+entry*8,&pointer,8);
    patched++;
  }
  return 0;
fail:
  /* Inputs rejected before execution never count as a successful operator. */
  for(uint32_t i=0;i<patched;i++) {
    unsigned char *r=(unsigned char *)b->relocations+i*24;
    memcpy(b->views[u32(r)].data+u64(r+8)*8,&b->original_addresses[i],8);
  }
  if(b->mapping) munmap(b->mapping,b->size);
  if(b->fd>=0) close(b->fd);
  free(b->views);free(b->original_addresses);memset(b,0,sizeof(*b));b->fd=-1;
  return -1;
}
int a100_bundle_close(struct a100_bundle *b) {
  for(uint32_t i=0;i<b->nrelocations;i++) {
    unsigned char *r=(unsigned char *)b->relocations+i*24;
    uint32_t table=u32(r);uint64_t entry=u64(r+8);
    memcpy(b->views[table].data+entry*8,&b->original_addresses[i],8);
  }
  int status=msync(b->mapping,b->size,MS_SYNC);
  munmap(b->mapping,b->size);close(b->fd);free(b->views);free(b->original_addresses);
  memset(b,0,sizeof(*b));b->fd=-1;return status;
}
