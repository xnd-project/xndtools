#include <math.h>

//void vsNothing(const int n, const float a[], float r[]);
//void vdNothing(const int n, const double a[], double r[]);
#define vsNothing(n,a,r) (void)n; (void)a; (void)r;
#define vdNothing(n,a,r) (void)n; (void)a; (void)r;

#define vsCopy(n,a,r) memcpy(r, a, n*sizeof(float));
#define vdCopy(n,a,r) memcpy(r, a, n*sizeof(double));

#define vsMyCopy(n,a,r) for (int i=0; i<n; i++) r[i] = a[i];
#define vdMyCopy(n,a,r) for (int i=0; i<n; i++) r[i] = a[i];

#define vsMyExp(n,a,r) for (int i=0; i<n; i++) r[i] = expf(a[i]);
#define vdMyExp(n,a,r) for (int i=0; i<n; i++) r[i] = exp(a[i]);
