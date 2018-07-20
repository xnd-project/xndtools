
#include "xnd.h"
extern int xndtools_cpy(char* dest, const xnd_t* stack_ptr, bool fortran);
extern char* xndtools_copy(const xnd_t* stack_ptr, ndt_context_t *ctx);
extern char* xndtools_fcopy(const xnd_t* stack_ptr, ndt_context_t *ctx);

extern int xndtools_invcpy(const char* src, const xnd_t* stack_ptr, bool fortran);
