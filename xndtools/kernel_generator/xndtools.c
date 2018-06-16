/*
  Author: Pearu Peterson
  Created: May 2018
*/

#include <stdio.h>
#include <string.h>
#include <malloc.h>

#include "xndtools.h"

#define GET_ITEM_REF(x, i) ((x)->ptr + ((x)->index + (i) * ((x)->type->Concrete.FixedDim.step)) * (x)->type->Concrete.FixedDim.itemsize)

/*
  Return number of bytes in fixed dims stack.
 */
static int64_t get_fixed_nbytes(const xnd_t* stack_ptr) {
  int64_t items = 1;
  int64_t itemsize = stack_ptr->type->Concrete.FixedDim.itemsize;
  int ndim = xnd_ndim(stack_ptr);
  for (int64_t i=0; i< ndim; i++)
    items *= xnd_fixed_shape_at(stack_ptr, i);
  return items * itemsize;
 }

/*
  Copy fixed dims stack (possibly sliced) to a C contiguous destination.
  Return number of bytes copied.
 */
static int make_copy(char* dest, const xnd_t* stack_ptr) {
  int ndim = xnd_ndim(stack_ptr);
  int64_t itemsize = stack_ptr->type->Concrete.FixedDim.itemsize;
  char* ptr0 = stack_ptr->ptr + stack_ptr->index * itemsize;
  //printf("make_copy: ndim=%d, c_contiguous=%d\n", ndim, ndt_is_c_contiguous(stack_ptr->type));
  if (ndim==0) {
    memcpy(dest, ptr0, itemsize); // avoid broadcasting scalar to 1d array   
    return itemsize;
  } else if (ndt_is_c_contiguous(stack_ptr->type)) {
    int64_t nbytes = get_fixed_nbytes(stack_ptr);
    memcpy(dest, ptr0, nbytes);
    return nbytes;
  } else if (ndim>1) {
    int64_t N = xnd_fixed_shape_at(stack_ptr, 0);
    int64_t N1 = 1;
    for (int64_t i=0; i<N; i++) {
      xnd_t row = xnd_fixed_dim_next(stack_ptr, i);
      N1 = make_copy(dest + N1*i, &row);
      assert(N1>=1);
    }
    return N * N1;
  } else if (ndim==1) {
    int64_t N = xnd_fixed_shape_at(stack_ptr, 0);
    int64_t step = stack_ptr->type->Concrete.FixedDim.step * itemsize;
    switch (itemsize) { // todo: check if assignment is faster than memcpy or not
    case 1:
      {
	int8_t* out = (int8_t*)dest;
	for (int64_t i=0; i< N; i++)
	  out[i] = *(const int8_t*)(ptr0+i*step);
	break;
      }
    case 2:
      {
	int16_t* out = (int16_t*)dest;
	for (int64_t i=0; i< N; i++)
	  out[i] = *(const int16_t*)(ptr0+i*step);
	break;
      }
    case 4:
      {
	int32_t* out = (int32_t*)dest;
	for (int64_t i=0; i< N; i++)
	  out[i] = *(const int32_t*)(ptr0+i*step);
	break;
      }
    case 8:
      {
	int64_t* out = (int64_t*)dest;
	for (int64_t i=0; i< N; i++)
	  out[i] = *(const int64_t*)(ptr0+i*step);
	break;
      }
    default:
      {
	for (int64_t i=0; i< N; i++)
	  memcpy(dest+i*itemsize, ptr0+i*step, itemsize);
      }
    }
    return N*itemsize;
  }
  return -1;
}

/*
  Return a C contiguous copy of fixed dims stack. Caller is
  responsible for deallocating the returned array.
 */

char* xndtools_copy(const xnd_t* stack_ptr, ndt_context_t *ctx) {
  char* target = NULL;
  int64_t nbytes = get_fixed_nbytes(stack_ptr);
  target = (char*)malloc(nbytes);
  if (target==NULL) {
    ndt_err_format(ctx, NDT_MemoryError,
		   "xndtools_copy: failed to allocate memory");
    return NULL;
  }
  int64_t tbytes = make_copy(target, stack_ptr);
  if (tbytes!=nbytes) {
    ndt_err_format(ctx, NDT_RuntimeError,
		   "xndtools_copy: mismatch of allocated and copied memory");
    free(target);
    target = NULL;
  }
  return target;
}