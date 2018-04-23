""" Provides: generate_module.
"""
# Author: Pearu Peterson
# Created: April 2018

import os
from .generate_kernel import get_module_data

def generate_module(config_file,
                    target_file = None,
                    target_language = 'python',
                    source_dir = '',
                    package = None,
                    sources = []):
    module_data = get_module_data(config_file, package=package)
    module_data['language'] = target_language
    if target_file is None:
        target_file = os.path.join(source_dir, '{modulename}-{language}.c'.format(**module_data))
    if target_language == 'python':
        module_source = pymodule_template.format(**module_data)
    else:
        raise NotImplementedError(repr(target_language))
    f = open(target_file, 'w')
    f.write(module_source)
    f.close()
    print('Created {!r}'.format(target_file))
    
    return dict(config_file = config_file,
                sources = [target_file] + sources,
                include_dirs = [
                    os.path.dirname(__file__), # location of pygumath.c
                ] + module_data['include_dirs'],
                extname = module_data['fullname'],
                language = target_language)
    
pymodule_template = '''
#include <Python.h>
#include "ndtypes.h"
#include "pyndtypes.h"
#include "xnd.h"
#include "pyxnd.h"
#include "gumath.h"


/* libxnd.so is not linked without at least one xnd symbol. The -no-as-needed
 * linker option is difficult to integrate into setup.py. */
const void *dummy = &xnd_error;

/* Temporarily including gumath Python support functions, ought to use include "pygumath.h" approach */
#include "pygumath.c"

static PyGetSetDef gufunc_getsets [] =
{{
  {{ "kernels", (getter)gufunc_kernels, NULL, NULL, NULL}},
  {{NULL}}
}};


static PyTypeObject Gufunc_Type = {{
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "{extmodulename}.gufunc",
    .tp_basicsize = sizeof(GufuncObject),
    .tp_dealloc = (destructor)gufunc_dealloc,
    .tp_hash = PyObject_HashNotImplemented,
    .tp_call = (ternaryfunc)gufunc_call,
    .tp_getattro = PyObject_GenericGetAttr,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_getset = gufunc_getsets
}};

/****************************************************************************/
/*                                  Module                                  */
/****************************************************************************/

static struct PyModuleDef {modulename}_module = {{
    PyModuleDef_HEAD_INIT,        /* m_base */
    "{fullname}",                 /* m_name */
    NULL,                         /* m_doc */
    -1,                           /* m_size */
    NULL,                         /* m_methods */
    NULL,                         /* m_slots */
    NULL,                         /* m_traverse */
    NULL,                         /* m_clear */
    NULL                          /* m_free */
}};

static int
add_function(const gm_func_t *f, void *state)
{{
    PyObject *m = (PyObject *)state;
    PyObject *func;

    func = gufunc_new(f->name);
    if (func == NULL) {{
        return -1;
    }}

    return PyModule_AddObject(m, f->name, func);
}}

int gmk_init_{modulename}_kernels(ndt_context_t *ctx);

PyMODINIT_FUNC
PyInit_{modulename}(void)
{{
    NDT_STATIC_CONTEXT(ctx);
    PyObject *m = NULL;
    static int initialized = 0;

    if (!initialized) {{
       if (import_ndtypes() < 0) {{
            return NULL;
       }}
       if (import_xnd() < 0) {{
            return NULL;
       }}
       if (gm_init(&ctx) < 0) {{
           return seterr(&ctx);
       }}
       if (gmk_init_{modulename}_kernels(&ctx) < 0) {{
           return seterr(&ctx);
       }}
       initialized = 1;
    }}

    if (PyType_Ready(&Gufunc_Type) < 0) {{
        return NULL;
    }}

    m = PyModule_Create(&{modulename}_module);
    if (m == NULL) {{
        goto error;
    }}

    if (gm_tbl_map(add_function, m) < 0) {{
        goto error;
    }}


    return m;

error:
    Py_CLEAR(m);
    return NULL;
}}
'''


