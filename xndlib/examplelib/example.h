
extern int no_input(void);
extern void no_output(int* a);
extern int int_intent_in(int a);
extern double double_intent_in(double a);
extern int int_p_intent_in(int* a);
extern double double_p_intent_in(double* a);
extern int intarr_intent_in(int* a, int n);
extern double doublearr_intent_in(double* a, int n);

extern double doublearr_2d_c_intent_in(double* a, int m, int n);
extern double doublearr_2d_f_intent_in(double* a, int m, int n);

extern double doublearr_1d1d_c_intent_in(double** a, int m, int n);
extern double doublearr_1d1d_f_intent_in(double** a, int m, int n);

extern void doublearr_intent_out(int n, double *a);

extern void i_add_one(int x, int* r);
extern void l_add_one(long x, long* r);
extern void d_add_one(double x, double* r);
extern void s_add_one(float x, float* r);

extern void d_example_sum(long n, double* x, double* r);
extern void s_example_sum(long n, float* x, float* r);
extern void i_example_sum(long n, int* x, int* r);

