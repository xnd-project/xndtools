
#include "xnd.h"
extern int64_t xndtools_fixed_nbytes(const xnd_t* stack_ptr);
extern int xndtools_cpy(char* dest, const xnd_t* stack_ptr, bool fortran);
extern char* xndtools_copy(const xnd_t* stack_ptr, ndt_context_t *ctx);
extern char* xndtools_fcopy(const xnd_t* stack_ptr, ndt_context_t *ctx);

extern int xndtools_invcpy(const char* src, const xnd_t* stack_ptr, bool fortran);
inline int xndtools_inv_copy(const char* src, const xnd_t* stack_ptr) {
  return xndtools_invcpy(src, stack_ptr, false);
}
inline int xndtools_inv_fcopy(const char* src, const xnd_t* stack_ptr) {
  return xndtools_invcpy(src, stack_ptr, true);
}
