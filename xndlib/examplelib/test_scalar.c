/*
  Unittests for scalars.

  Created: June 2018
  Author: Pearu Peterson
 */

#include "test_scalar.h"

void test_scalar(long a)
{
  (void) a;
  /* do nothing */
}

void test_scalar_ptr(long* a)
{
  *a = *a + 10;
}

long test_scalar_return(long a)
{
  return a + 20;
}

long test_scalar_ptr_return(long* a)
{
  *a = *a + 10; // inplace change
  return *a + 20;
}
