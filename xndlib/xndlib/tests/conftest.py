# Importing gumath prior xndtools generated extension modules avoids
# the following exception:
#   ImportError: libgumath.so.0: cannot open shared object file: ...

import gumath  # noqa: F401
