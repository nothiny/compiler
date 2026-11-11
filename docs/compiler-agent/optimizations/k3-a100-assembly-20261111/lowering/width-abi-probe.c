#include "a100rt.h"
#include <stdio.h>
__attribute__((noinline,noclone,noipa))
unsigned choose_width(const struct a100rt_view *views) {
  const unsigned char *a = views[0].storage;
  const unsigned char *b = views[1].storage;
  return a == b ? 32u : 128u;
}
int main(void) {
  unsigned char shared[512], other[512];
  struct a100rt_view views[2] = {{0}};
  views[0].data=shared; views[0].storage=shared;
  views[1].data=other; views[1].storage=other;
  unsigned distinct=choose_width(views);
  views[1].data=shared+4; views[1].storage=shared;
  unsigned shifted=choose_width(views);
  views[1].data=shared; views[1].storage=shared;
  unsigned same=choose_width(views);
  printf("distinct=%u shifted=%u same=%u storage_offset=%zu view_size=%zu\n",distinct,shifted,same,offsetof(struct a100rt_view,storage),sizeof(struct a100rt_view));
  return !(distinct==128 && shifted==32 && same==32);
}
