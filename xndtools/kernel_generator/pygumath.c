
#ifdef _MSC_VER
  #ifndef UNUSED
    #define UNUSED
  #endif
#else
  #if defined(__GNUC__) && !defined(__INTEL_COMPILER)
    #define UNUSED __attribute__((unused))
  #else
    #define UNUSED
  #endif
#endif


/****************************************************************************/
/*                               Error handling                             */
/****************************************************************************/

static PyObject *
seterr(ndt_context_t *ctx)
{
    return Ndt_SetError(ctx);
}


/****************************************************************************/
/*                              Function object                             */
/****************************************************************************/

typedef struct {
    PyObject_HEAD
    char *name;
} GufuncObject;

static PyTypeObject Gufunc_Type;

static PyObject *
gufunc_new(const char *name)
{
    NDT_STATIC_CONTEXT(ctx);
    GufuncObject *self;

    self = PyObject_New(GufuncObject, &Gufunc_Type);
    if (self == NULL) {
        return NULL;
    }

    self->name = ndt_strdup(name, &ctx);
    if (self->name == NULL) {
        return seterr(&ctx);
    }

    return (PyObject *)self;
}

static void
gufunc_dealloc(GufuncObject *self)
{
    ndt_free(self->name);
    PyObject_Del(self);
}

/****************************************************************************/
/*                              Function calls                              */
/****************************************************************************/

static void
clear_objects(PyObject **a, Py_ssize_t len)
{
    Py_ssize_t i;

    for (i = 0; i < len; i++) {
        Py_CLEAR(a[i]);
    }
}

static PyObject *
gufunc_call(GufuncObject *self, PyObject *args, PyObject *kwds)
{
    NDT_STATIC_CONTEXT(ctx);
    const Py_ssize_t nin = PyTuple_GET_SIZE(args);
    PyObject **a = &PyTuple_GET_ITEM(args, 0);
    PyObject *result[NDT_MAX_ARGS];
    ndt_apply_spec_t spec = ndt_apply_spec_empty;
    const ndt_t *in_types[NDT_MAX_ARGS];
    xnd_t stack[NDT_MAX_ARGS];
    gm_kernel_t kernel;
    int i, k;

    if (kwds) {
        PyErr_SetString(PyExc_TypeError,
            "gufunc calls do not support keywords");
        return NULL;
    }

    if (nin > NDT_MAX_ARGS) {
        PyErr_SetString(PyExc_TypeError,
            "invalid number of arguments");
        return NULL;
    }

    for (i = 0; i < nin; i++) {
        if (!Xnd_Check(a[i])) {
            PyErr_SetString(PyExc_TypeError, "arguments must be xnd");
            return NULL;
        }
        stack[i] = *CONST_XND(a[i]);
        in_types[i] = stack[i].type;
    }

    kernel = gm_select(&spec, self->name, in_types, nin, stack, &ctx);
    if (kernel.set == NULL) {
        return seterr(&ctx);
    }

    if (spec.nbroadcast > 0) {
        for (i = 0; i < nin; i++) {
            stack[i].type = spec.broadcast[i];
        }
    }

    for (i = 0; i < spec.nout; i++) {
        if (ndt_is_concrete(spec.out[i])) {
            PyObject *x = Xnd_EmptyFromType(Py_TYPE(a[i]), spec.out[i]);
            if (x == NULL) {
                clear_objects(result, i);
                ndt_apply_spec_clear(&spec);
                return NULL;
            }
            result[i] = x;
            stack[nin+i] = *CONST_XND(x);
         }
         else {
            result[i] = NULL;
            stack[nin+i] = xnd_error;
         }
    }

    if (gm_apply(&kernel, stack, spec.outer_dims, &ctx) < 0) {
        clear_objects(result, spec.nout);
        return seterr(&ctx);
    }

    for (i = 0; i < spec.nout; i++) {
        if (ndt_is_abstract(spec.out[i])) {
            ndt_del(spec.out[i]);
            PyObject *x = Xnd_FromXnd(Py_TYPE(a[i]), &stack[nin+i]);
            stack[nin+i] = xnd_error;
            if (x == NULL) {
                clear_objects(result, i);
                for (k = i+1; k < spec.nout; k++) {
                    if (ndt_is_abstract(spec.out[k])) {
                        xnd_del_buffer(&stack[nin+k], XND_OWN_ALL);
                    }
                }
            }
            result[i] = x;
        }
    }

    if (spec.nbroadcast > 0) {
        for (i = 0; i < nin; i++) {
            ndt_del(spec.broadcast[i]);
        }
    }
    switch (spec.nout) {
    case 0: Py_RETURN_NONE;
    case 1: return result[0];
    default: {
        PyObject *tuple = PyTuple_New(spec.nout);
        if (tuple == NULL) {
            clear_objects(result, spec.nout);
            return NULL;
        }
        for (i = 0; i < spec.nout; i++) {
            PyTuple_SET_ITEM(tuple, i, result[i]);
        }
        return tuple;
      }
    }
}

static PyObject *
gufunc_kernels(GufuncObject *self, PyObject *args UNUSED)
{
    NDT_STATIC_CONTEXT(ctx);
    PyObject *list, *tmp;
    const gm_func_t *f;
    char *s;
    int i;

    f = gm_tbl_find(self->name, &ctx);
    if (f == NULL) {
        return seterr(&ctx);
    }

    list = PyList_New(f->nkernels);
    if (list == NULL) {
        return NULL;
    }

    for (i = 0; i < f->nkernels; i++) {
        s = ndt_as_string(f->kernels[i].sig, &ctx);
        if (s == NULL) {
            Py_DECREF(list);
            return seterr(&ctx);
        }

        tmp = PyUnicode_FromString(s);
        ndt_free(s);
        if (tmp == NULL) {
            Py_DECREF(list);
            return NULL;
        }

        PyList_SET_ITEM(list, i, tmp);
    }

    return list;
}
