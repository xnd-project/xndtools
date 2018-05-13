#include <stdio.h>
#include "example.h"

void i_add_one(int x, int* r) { *r = x + 1; }
void l_add_one(long x, long* r) { *r = x + 1; }
void d_add_one(double x, double* r) { *r = x + 1.0; }
void s_add_one(float x, float* r) { *r = x + 1.0; }

void d_example_sum(long n, double* x, double* r) {
  long i;
  double s = 0.0;
  for (i=0;i<n;i++)
    s += x[i];
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
