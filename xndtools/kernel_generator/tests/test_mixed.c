long test_mixed_matrices(long n, long* a, long* b)
{
  /* a[0,n-1] - C layout
     a[n-1,0] - F layout 
     b[n-1,0] - C layout
     b[0,n-1] - F layout
   */
  return a[n-1] + b[(n-1)*n];
}
