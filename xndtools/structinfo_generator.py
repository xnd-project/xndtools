import os
from . import c_utils


def flatten_unions(items):
    for item in items:
        if item[0] == 'union':
            for i in flatten_unions(item[1]):
                yield i
        elif item[0] == 'struct':
            yield (item[0], list(flatten_unions(item[1])), item[2])
        else:
            yield item


def flatten_structs(items):
    for item in items:
        if item[0] == 'struct':
            members, name = item[1:]
            for (typespec, names) in flatten_structs(members):
                yield typespec, (name,)+names
        else:
            typespec, name, size = item
            if size is not None:
                yield typespec+'*', (name,)
            else:
                yield typespec, (name,)


pyc_noarg_template = 'static PyObject *pyc_{fname}(PyObject *self, PyObject *args) {{ return PyLong_FromLong((long)({fname}())); }}'
pyc_noarg_doc_template = '"{fname}() -> int"'
pyc_arg_doc_template = '"{fname}(< pointer to {typename} >) -> < pointer to {typename}->{memberattrs} >"'
pyc_method_template = '{{"{fname}", (PyCFunction)pyc_{fname}, METH_VARARGS, {fdoc}}},'

pyc_module_template = '''
#ifdef PYTHON_MODULE
#include "Python.h"

{functions}

static PyObject *pyc_capsule_to_int32(PyObject *self, PyObject *args) {{
  PyObject* ptr=NULL;
  if (!PyArg_UnpackTuple(args, "capsule", 1, 1, &ptr))
    return NULL;
  if (PyCapsule_CheckExact(ptr)) {{
    const char* name = PyCapsule_GetName(ptr);
    int32_t value = *((int32_t*)PyCapsule_GetPointer(ptr, name));
    return PyLong_FromLong((long)value);
  }}
  PyErr_SetString(PyExc_TypeError, "expected capsule instance");
  return NULL;
}}

static PyObject *pyc_capsule_to_int64(PyObject *self, PyObject *args) {{
  PyObject* ptr=NULL;
  if (!PyArg_UnpackTuple(args, "capsule", 1, 1, &ptr))
    return NULL;
  if (PyCapsule_CheckExact(ptr)) {{
    const char* name = PyCapsule_GetName(ptr);
    int64_t value = *((int64_t*)PyCapsule_GetPointer(ptr, name));
    return PyLong_FromLong((long)value);
  }}
  PyErr_SetString(PyExc_TypeError, "expected capsule instance");
  return NULL;
}}

static PyObject *pyc_capsule_to_bytes(PyObject *self, PyObject *args) {{
  PyObject* ptr=NULL;
  PyObject* size=NULL;
  if (!PyArg_UnpackTuple(args, "capsule", 1, 2, &ptr, &size))
    return NULL;
  if (PyCapsule_CheckExact(ptr)) {{
    const char* name = PyCapsule_GetName(ptr);
    const char* value = ((const char*)PyCapsule_GetPointer(ptr, name));
    if (size==NULL)
      return PyBytes_FromString(value); // DANGER: if ptr does not contain 0 terminated string, the result is unpredictable
    Py_ssize_t sz = PyLong_AsLong(size);
    if (sz < 0)
      return NULL;
    return PyBytes_FromStringAndSize(value, sz);
  }}
  PyErr_SetString(PyExc_TypeError, "expected capsule instance");
  return NULL;
}}

static PyMethodDef {modulename}_methods[] = {{
  {methods}
  {{"value_int32", (PyCFunction)pyc_capsule_to_int32, METH_VARARGS, "(capsule) -> <capsule int32 value>"}},
  {{"value_int64", (PyCFunction)pyc_capsule_to_int64, METH_VARARGS, "(capsule) -> <capsule int64 value>"}},
  {{"value_bytes", (PyCFunction)pyc_capsule_to_bytes, METH_VARARGS, "(capsule[, size]) -> <capsule content as bytes>"}},
  {{NULL, NULL, 0, NULL}}   /* sentinel */
}};

static struct PyModuleDef {modulename}module = {{
  PyModuleDef_HEAD_INIT,
  "{modulename}",   /* name of module */
  NULL,             /* module documentation */
  -1,
  {modulename}_methods
}};

PyMODINIT_FUNC
PyInit_{modulename}(void) {{
  {PyInit_source}
  return PyModule_Create(&{modulename}module);
}}
#endif
'''


def generate(args):
    include_dirs = args.include_dir or []
    include = args.include[0]
    target = args.output
    if target is None:
        target = os.path.basename(include).replace('.', '_') + '_structinfo.c'
        orig_include = include
    modulename = args.modulename
    if not modulename:
        modulename = os.path.splitext(os.path.basename(target))[0]

    source = []
    for include in args.include:
        include = c_utils.find_include(include, include_dirs)
        source.append('#include "{}"'.format(include))
    source = '\n'.join(source)
    source = c_utils.preprocess(source, include_dirs=include_dirs)
    print(source)
    structs = c_utils.get_structs(source)
    lines = ['/* This file is generated using structinfo_generator from the xndtools project */']
    for include in args.include:
        lines.append('#include "{}"'.format(include))

    lines.append(args.c_source)

    ext_functions = [args.capi_source]
    ext_methods = [args.PyMethodDef_items]
    for typename, items in structs.items():
        if isinstance(items, str):
            print('SKIPPING:', typename, items)
            continue

        if items and items[0] == 'PyObject_HEAD':
            items = items[1:]
            fname = f'capsulate_{typename}'
            fdoc = 'NULL'
            implementation = dict(
                NdtObject=dict(check='Ndt_CheckExact'),
                XndObject=dict(check='Ndt_Check'),
            ).get(typename)
            if implementation is not None:
                pyc_func = f'''\
static PyObject *pyc_{fname}(PyObject *self, PyObject *args) {{
  PyObject* obj=NULL;
  if (!PyArg_UnpackTuple(args, "{typename}_instance", 0, 1, &obj))
    return NULL;
  if ({implementation['check']}(obj)) {{
    Py_INCREF(obj);
    return PyCapsule_New(obj, "{typename}*", NULL);
  }}
  PyErr_SetString(PyExc_TypeError, "expected {typename} instance");
  return NULL;
}}'''
                ext_functions.append(pyc_func)
                ext_methods.append(pyc_method_template.format_map(locals()))
            else:
                print(f'capsulating {typename} not implemented')

        fname = f'sizeof_{typename}'
        # fmember = fname
        fdoc = pyc_noarg_doc_template.format_map(locals())
        lines.append(f'extern size_t {fname}(void){{ return sizeof({typename}); }}')
        ext_functions.append(pyc_noarg_template.format_map(locals()))
        ext_methods.append(pyc_method_template.format_map(locals()))

        for typespec, names in flatten_structs(flatten_unions(items)):
            # loose C type declaration would be `<typespec> <names[-1]>`
            membernames = '_'.join(names)
            memberattrs = '.'.join(names)

            fname = f'get_{typename}_{membernames}'

            lines.append(f'extern /* pointer to `{typespec}` */ void * {fname}(void* ptr){{ return &((({typename}*)ptr)->{memberattrs}); }}')
            fdoc = f'"{fname}(< capsule({typename}) >) -> < capsule( &{typename}->{memberattrs} ) >"'

            pyc_func = f'''\
static PyObject *pyc_{fname}(PyObject *self, PyObject *args) {{
  PyObject* ptr=NULL;
  if (!PyArg_UnpackTuple(args, "{typename}", 0, 1, &ptr))
    return NULL;
  if (PyCapsule_CheckExact(ptr)) {{
    return PyCapsule_New( {fname}(PyCapsule_GetPointer(ptr, "{typename}*")), "{typespec}", NULL);
  }}
  PyErr_SetString(PyExc_TypeError, "expected capsuleted {typename}");
  return NULL;
}}'''

            ext_functions.append(pyc_func)
            ext_methods.append(pyc_method_template.format_map(locals()))

            fname = f'offsetof_{typename}_{membernames}'
            fmember = fname
            fdoc = pyc_noarg_doc_template.format_map(locals())
            lines.append(f'extern size_t {fname}(void)'
                         f'{{ return offsetof({typename}, {memberattrs}); }}')
            ext_functions.append(pyc_noarg_template.format_map(locals()))
            ext_methods.append(pyc_method_template.format_map(locals()))
    methods = '\n  '.join(ext_methods)
    functions = '\n'.join(ext_functions)

    PyInit_source = args.PyInit_source
    ext_module = pyc_module_template.format_map(locals())
    f = open(target, 'w')
    f.write('\n'.join(lines))
    f.write(ext_module)
    f.close()
    print('Created {}'.format(target))
