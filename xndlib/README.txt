
Creating gumath kernels and language modules for C libraries
------------------------------------------------------------

0. We'll use examplelib for illustration.

1. Generate initial kernel configuration file `example-kernels.cfg`:

  xnd_tools config examplelib/example.h

2. Open `example-kernels.cfg` with a text editor and modify according
to the instructions (given in the header of the kernel configuration
file). For instance, in the case of example_sum, male the following
changes:

2.1 Rename `[FUNCTION __example__um]` section to `[FUNCTION example_sum]`

2.2 Move `i_example_sum` prototype under the section `[FUNCTION example_sum]`

2.3 Specify the dimension of `x` argument.
2.4 Make argument `n` hidden and initialize it.
2.5 Make argument `r` hidden and to be returned as output.
2.6 Make `x` an input argument.
2.7 Remove `skip = ` line to enable the function for kernel generation.

In summarym we'll have:

  dimension = x(n)
  input_arguments = x
  inplace_arguments = 
  output_arguments = r
  hide_arguments = n = len(x), r

3. Generate kernel functions C source file `example-kernels.c`:

  xnd_tools kernel example-kernels.cfg
  
4. Generate Python wrapper module source file `example-python.c`:

  xnd_tools module example-kernels.cfg

5. Build an extension module `example` with your favorite tool. To
complete this example, we'll use `setup.py` approach where the kernel
and module generations are integrated. So, run

  python setup.py develop

6. Test in python:

  python test_example.py
