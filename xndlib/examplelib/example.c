/*

  Argument types:
    scalar, scalar_ptr, 1d-array, 2d-c-array, 2d-f-array, 1d-refs-to-1d-arrays
  
  Argument intents:
    hide, input, inplace, output, input-output, inplace-output 

  Function return types:
    void, scalar

 */
  

#include <stdio.h>
#include "example.h"

/*
   void
 */

int no_input(void) {
  return 2018;
}

void no_output(int* a) {
  *a = 2019;
}

/* 
   scalar intent(input)
*/

int int_intent_in(int a)
{ return a + 1; }
double double_intent_in(double a)
{ return a + 1.0; }

int int_p_intent_in(int* a)
{ return (*a) + 1; }
double double_p_intent_in(double* a)
{ return (*a) + 1.0; }

int intarr_intent_in(int* a, int n)
{ return a[0] + a[n-1]; }
double doublearr_intent_in(double* a, int n)
{ return a[0] + a[n-1]; }

/* 
   array intent(input)
*/

double doublearr_2d_c_intent_in(double* a, int m, int n)
{ return a[0] + a[n-1]; }

double doublearr_2d_f_intent_in(double* a, int m, int n)
{ return a[0] + a[n*m-m]; }

double doublearr_1d1d_c_intent_in(double** a, int m, int n) // TODO
{ return a[0][0] + a[0][n-1]; }

double doublearr_1d1d_f_intent_in(double** a, int m, int n) // TODO
{ return a[0][0] + a[n-1][0]; }


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
