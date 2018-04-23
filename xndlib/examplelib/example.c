#include <stdio.h>
#include "example.h"

void d_example_sum(long n, double* x, double* r) {
  long i;
  double s = 0.0;
  for (i=0;i<n;i++)
    s += x[i];
  printf("d_example_sum: n = %d, s = %f\n", n, s);
  *r = s;
}

void s_example_sum(long n, float* x, float* r) {
  long i;
  float s = 0.0;
  for (i=0;i<n;i++)
    s += x[i];
  *r = s;
}

void i_example_sum(long n, int* x, int* r) {
  long i;
  int s = 0.0;
  for (i=0;i<n;i++)
    s += x[i];
  *r = s;
}
