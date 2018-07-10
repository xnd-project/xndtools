import os
from . import c_utils

def flatten_unions(items):
    for item in items:
        if item[0]=='union':
            for i in flatten_unions(item[1]):
                yield i
        elif item[0]=='struct':            
            yield (item[0], list(flatten_unions(item[1])), item[2])
        else:
            yield item

def flatten_structs(items):
    for item in items:
        if item[0]=='struct':
            members, name = item[1:]
            for (typedef, names) in flatten_structs(members):
                yield typedef, (name,)+names
        else:
            typedef, name, size = item
            if size is not None:
                yield typedef+'*', (name,)
            else:
                yield typedef, (name,)

pyc_noarg_template = 'static PyObject *pyc_{fname}(PyObject *self, PyObject *args) {{ return PyLong_FromLong((long)({fname}())); }}'
pyc_noarg_doc_template = '"{fname}() -> int"'
pyc_arg_template = '''static PyObject *pyc_{fname}(PyObject *self, PyObject *args) {{
  PyObject* ptr=NULL;
  if (!PyArg_UnpackTuple(args, "{typename}", 0, 1, &ptr))
    return NULL;
  if (PyCapsule_CheckExact(ptr))
    return PyCapsule_New({fname}(PyCapsule_GetPointer(ptr, "{typename}")), "{fname}", NULL);
  return NULL;
}}'''
pyc_arg_doc_template = '"{fname}(< pointer to {typename} >) -> < pointer to {typename}->{memberattrs} >"'
pyc_method_template = '{{"{fname}", (PyCFunction)pyc_{fname}, METH_VARARGS, {fdoc}}},'

pyc_module_template = '''
#ifdef PYTHON_MODULE
#include "Python.h"

{functions}

static PyMethodDef {modulename}_methods[] = {{
  {methods}
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
PyInit_{modulename}(void) {{ return PyModule_Create(&{modulename}module); }}
#endif
'''

def generate(args):
    include_dirs = args.include_dir or []
    include = args.include
    target = args.output
    if target is None:
        target = os.path.basename(include).replace('.','_') + '_structinfo.c'
        orig_include = include
    modulename = os.path.splitext(os.path.basename(target))[0]
        
    include = c_utils.find_include(include, include_dirs)
    source = open(include).read()
    source = c_utils.resolve_includes(source, include_dirs=include_dirs)
    structs = c_utils.get_structs(source)
    lines = [
        '/* This file is generated using structinfo_generator from the xndtools project */',
        '#include "{}"'.format(args.include)]
    ext_functions = []
    ext_methods = []
    for typename, items in structs.items():
        if isinstance(items, str):
            print('SKIPPING:', typename, items)
            continue
        fname = 'sizeof_{typename}'.format_map(locals())
        fdoc = pyc_noarg_doc_template.format_map(locals())
        lines.append('extern size_t {fname}(void){{ return sizeof({typename}); }}'.format_map(locals()))
        ext_functions.append(pyc_noarg_template.format_map(locals()))
        ext_methods.append(pyc_method_template.format_map(locals()))
        
        for typedef,names in flatten_structs(flatten_unions(items)):
            membernames = '_'.join(names)
            memberattrs = '.'.join(names)
            
            fname = 'get_{typename}_{membernames}'.format_map(locals())
            fdoc = pyc_arg_doc_template.format_map(locals())
            lines.append('extern /* {typedef} */ void * {fname}(void* ptr){{ return &((({typename}*)ptr)->{memberattrs}); }}'.format_map(locals()))
            ext_functions.append(pyc_arg_template.format_map(locals()))
            ext_methods.append(pyc_method_template.format_map(locals()))

            fname = 'offsetof_{typename}_{membernames}'.format_map(locals())
            fdoc = pyc_noarg_doc_template.format_map(locals())
            lines.append('extern size_t {fname}(void){{ return offsetof({typename}, {memberattrs}); }}'.format_map(locals()))
            ext_functions.append(pyc_noarg_template.format_map(locals()))
            ext_methods.append(pyc_method_template.format_map(locals()))
            
    methods = '\n  '.join(ext_methods)
    functions = '\n'.join(ext_functions)
    ext_module = pyc_module_template.format_map(locals())
    f = open(target, 'w')
    f.write('\n'.join(lines))
    f.write(ext_module)
    f.close()
    print('Created {}'.format(target))
