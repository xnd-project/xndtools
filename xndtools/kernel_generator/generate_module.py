""" Provides: generate_module.
"""
# Author: Pearu Peterson
# Created: April 2018

import os
from .generate_kernel import get_module_data


def generate_module(config_file,
                    target_file=None,
                    target_language='python',
                    source_dir='',
                    package=None,
                    sources=[]):
    module_data = get_module_data(config_file)
    module_data['language'] = target_language
    if target_file is None:
        target_file = os.path.join(source_dir, '{module_name}-{language}.c'
                                   .format(**module_data))
    if target_language == 'python':
        module_source = pymodule_template.format(**module_data)
    else:
        raise NotImplementedError(repr(target_language))
    f = open(target_file, 'w')
    f.write(module_source)
    f.close()
    print('Created {!r}'.format(target_file))

    extname = module_data['module_name']
    if package is not None:
        extname = package + '.' + extname

    return dict(config_file=config_file,
                sources=[target_file] + sources,
                include_dirs=module_data['include_dirs'],
                library_dirs=module_data['library_dirs'],
                libraries=module_data['libraries'],
                extname=extname,
                language=target_language,
                has_xnd=module_data['has_xnd'])


pymodule_template = '''
#include <Python.h>
#include "ndtypes.h"
#include "pyndtypes.h"
#include "gumath.h"
#include "pygumath.h"


/****************************************************************************/
/*                              Module globals                              */
/****************************************************************************/

/* Function table */
static gm_tbl_t *gmk_{module_name}_table = NULL;

/****************************************************************************/
/*                                  Module                                  */
/****************************************************************************/

static struct PyModuleDef {module_name}_module = {{
    PyModuleDef_HEAD_INIT,        /* m_base */
    "{module_name}",              /* m_name */
    NULL,                         /* m_doc */
    -1,                           /* m_size */
    NULL,                         /* m_methods */
    NULL,                         /* m_slots */
    NULL,                         /* m_traverse */
    NULL,                         /* m_clear */
    NULL                          /* m_free */
}};

int gmk_init_{module_name}_kernels(gm_tbl_t *tbl, ndt_context_t *ctx);

PyMODINIT_FUNC
PyInit_{module_name}(void)
{{
    NDT_STATIC_CONTEXT(ctx);
    PyObject *m = NULL;
    static int initialized = 0;

    if (!initialized) {{
       if (import_ndtypes() < 0) {{
            return NULL;
       }}
       if (import_gumath() < 0) {{
            return NULL;
       }}

       gmk_{module_name}_table = gm_tbl_new(&ctx);
       if (gmk_{module_name}_table == NULL) {{
           return Ndt_SetError(&ctx);
       }}

       if (gmk_init_{module_name}_kernels(gmk_{module_name}_table, &ctx) < 0) {{
           return Ndt_SetError(&ctx);
       }}

       initialized = 1;
    }}

    m = PyModule_Create(&{module_name}_module);
    if (m == NULL) {{
        goto error;
    }}

    if (Gumath_AddFunctions(m, gmk_{module_name}_table) < 0) {{
        goto error;
    }}

    return m;

error:
    Py_CLEAR(m);
    return NULL;
}}
'''
