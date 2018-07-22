/*
  Unittests for arrays.

  Created: July 2018
  Author: Pearu Peterson
*/

#include "test_array.h"

long test_array_range(long n, long*x)
{
  int i;
  long s = 0;
  for (i=0; i<n; i++) {
    s += x[i]; // to verify expected input
    x[i] = i;
  }
  return s;
}
