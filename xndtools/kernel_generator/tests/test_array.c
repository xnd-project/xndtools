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

long test_array_ranges(long n, long*x)
{
  int i, j;
  long s = 0;
  for (i=0; i<n; i++) {
    for (j=0; j<n; j++) {
      s += x[i*n+j]; // to verify expected input
      x[i*n+j] = i*10+j;
    }
  }
  return s;
}
