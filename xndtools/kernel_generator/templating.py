""" Provides templating tools.

Template - base class for templates.
Predicate - predicate function that implements boolean operations (not, or, and) using arithmetic operations (-, +, *).

Basic usage
-----------

::

  target = Template(<template target>,
                    variables = <dict of template strings>,
                    initialize = <function(data)>,
                    join = <dict of `..-list` and join functions>
                    )(<data>)

See test() function for an example.
"""
# Author: Pearu Peterson
# Created: May 2018

from pprint import pprint
from collections import defaultdict

def flatten(lst_of_lst):
    """ Flatten list of list objects.
    """
    lst = []
    for l in lst_of_lst:
        if isinstance(l, list):
            lst += flatten(l)
        else:
            lst.append(l)
    return lst

class verbosedefaultdict(defaultdict):
    """ When activated, report missing keys as not implemented features.
    """
    
    verbose = False
    def activate(self, name):
        self.name = name
        self.verbose = True

    def __missing__(self, key):
        if self.verbose:
            print('{}: not implemented key: {}'.format(self.name, key))
            return '/* {!r} not implemented */'.format(key)
        return defaultdict.__missing__(self, key)

def apply_format_map(obj, data):
    """ Apply data to Python objects containing strings.

    Parameters
    ----------
    obj : {None, list, dict, tuple}
      Specify input object. If `obj` is tuple, it is interpretted
      as `(if, ifobj[, elseobj])` construct.

    Returns
    -------
    obj : {None, list, dict}
      A transformation of input object where all string
      values are replaced by the result of `str.format_map(data)`.
    """
    if obj is None:
        return
    if isinstance(obj, str):
        try:
            return obj.format_map(data)
        except Exception as msg:
            print('apply_format_map:\n{}\n-----------------'.format(obj))
            raise
    if isinstance(obj, list):
        lst = []
        for o in obj:
            v = apply_format_map(o, data)
            if v is not None:
                lst.append(v)
        return lst
    if isinstance(obj, tuple):
        if len(obj) == 2:
            predicate, ifobj = obj
            elseobj = None
        elif len(obj) == 3:
            predicate, ifobj, elseobj = obj
        else:
            raise NotImplementedError(repr((type(obj),len(obj))))
        if predicate(data):
            return apply_format_map(ifobj, data)
        return apply_format_map(elseobj, data)
    
    if isinstance(obj, dict):
        dct = {}
        for k, o in obj.items():
            v = apply_format_map(o, data)
            if v is not None:
                dct[k] = v
        return dct

    if isinstance(obj, Block):
        start = apply_format_map(obj.start, data)
        end = apply_format_map(obj.end, data)
        return type(obj)(start, end)
        
    raise NotImplementedError(repr(type(obj)))

def apply_join(obj, data):
    """ Apply data to Python object containing str.join functions.

    Parameters
    ----------
    obj : {None, list, tuple, callable}
      Specify input object. If `obj` is tuple, it is interpretted
      as `(if, ifobj[, elseobj])` construct. If `obj` is list, the
      first non-None item is returned.

    Returns
    -------
    join_func : callable
      A join function `join_func(lst)->str`, or `None`.
    """
    if obj is None:
        return
    if isinstance(obj, str):
        return lambda lst: obj.join(flatten(lst))
    if callable(obj):
        return obj # callable is expected to apply flatten
    if isinstance(obj, tuple):
        if len(obj) == 2:
            predicate, ifobj = obj
            elseobj = None
        elif len(obj) == 3:
            predicate, ifobj, elseobj = obj
        else:
            raise NotImplementedError(repr((type(obj),len(obj))))
        if predicate(data):
            return apply_join(ifobj, data)
        return apply_join(elseobj, data)
    if isinstance(obj, list):
        for f in obj:
            j = apply_join(f, data)
            if j is not None:
                return j
        return
    raise NotImplementedError(repr(type(obj)))

class Block(object):

    def __init__(self, start, end):
        self.start = start
        self.end = end


        
class Template(object):
    """ Template class.
    """
    def __init__(self, template,
                 variables = {},
                 initialize = None,
                 join = {},
                 sort = {},
                 name = None):
        """Parameters
        ----------
        template : {str, dict, list, tuple}

          Specify template target object. String parts of the template
          target may contain str.format substitutions that will be
          filled in the application step, except for tuple.

          When template target is a tuple, the template is called
          conditional template. The first item of a tuple is predicate
          function and the second item is template target when the
          predicate(data) returns True, otherwise the third item is
          template target when give.

        variables : dict
          Specify auxialiary mapping of local substitutions.

        initialize : {None, callable}

          Specify an initialize function with a signature
          initialize(data). The function is used to update data
          with computed values.
        
        join : dict
          Specify join mapping of `...-list` values.

        sort : dict
          Specify sort mapping of `...-list` values.

        name : {None, str}
          Specify name for the template. Useful for debugging.


        """
        self.template = template
        self.variables = variables
        self.initialize = initialize
        self.subtemplates = {}
        self.name = name
        self.join = join
        self.sort = sort

    def __setitem__(self, key, value):
        self.subtemplates[key] = value
        if isinstance(value, type(self)) and value.name is None:
            value.name = key
        
    def __getitem__(self, key):
        return self.subtemplates[key]
        
    def __call__(self, data, parent_data = {}):
        """Apply data to template target and return result.

        Parameters
        ----------
        data : dict
          Specify data via `key`-`value` pairs. See Notes below for
          the algorithm of using the data object.

        parent_data : dict
          Contains parents data. [INTERNAL]

        Notes
        -----

        The following algorithm is used to compute the result of
        applying data to template target:

        If data `value` is a string, all occurrences of str.format
        substitutions with `key` in the template target are replaced
        with `value`.

        If data `value` is a list, its items are applied to
        sub-templates.  New data keys `...-list` with (initially
        empty) list values are created as follows:

        If sub-result is a string, it will be added to `key`+'-list'.
        If sub-result is a list, each element (that is not None) is added to `key`-list.
        If sub-result is a mapping, each item is added to `sub-key`+'-list'.
        If sub-result is None, it will be ignored.

        Prior applying `...-list` items to results, these are
        concatenated together using `join` functions. The `join`
        functions may post-process the list, e.g. by sorting it.
        """
        tmp_data = verbosedefaultdict(list)
        tmp_data['<data-keys>'] = '<'+'|'.join(data)+'>'
        if self.initialize is not None:
            self.initialize(data)
        for k, v in data.items():
            if isinstance(v, list):
                tmp_data[k] += v
            else:
                tmp_data[k] = v
            if isinstance(v, list) and v:
                subtemplate = self.subtemplates.get(k)
                if subtemplate is None:
                    print('{}(name={}).__call__:warning: no sub-template {!r} (available: {})'.format(type(self).__name__, self.name, k, ', '.join(self.subtemplates)))
                elif not callable(subtemplate):
                    print('{}(name={}).__call__:warning: sub-template {!r} not callable'.format(type(self).__name__, self.name, k))
                else:
                    for v_ in v:
                        v__ = parent_data.copy()
                        v__.update(data)
                        r = subtemplate(v_, v__)
                        if r is None:
                            pass
                        elif isinstance(r, str):
                            subkey = k + '-list'
                            tmp_data[subkey].append(r)
                        elif isinstance(r, list):
                            subkey = k + '-list'
                            tmp_data[subkey].extend(r)
                        elif isinstance(r, dict):
                            for k_, r_ in r.items():
                                subkey = k_ + '-list'
                                if isinstance(r_, str):
                                    tmp_data[subkey].append(r_)
                                elif isinstance(r_, list):
                                    #print(r_)
                                    tmp_data[subkey].extend(r_)
                                else:
                                    raise NotImplementedError(repr((self.name, k,k_,type(r_))))
                        else:
                            raise NotImplementedError(repr((self.name, k,type(r))))


        for k in list(tmp_data):
            v = tmp_data[k]
            sorter = self.sort.get(k)
            if sorter is not None:
                v = sorter(v)
            tmp_data[k] = v

        #pprint(tmp_data)
            
        for k in list(tmp_data):
            v = tmp_data[k]
            if k.endswith('-list'):
                assert isinstance(v, list),repr(type(v))
                d = defaultdict(list)
                for v_ in v:
                    if isinstance(v_, Block):
                        k_ = k[:-5]
                        d[k_ + '-start-list'].append(v_.start)
                        d[k_ + '-end-list'].insert(0, v_.end)
                    else:
                        d[k].append(v_)
                for k_, v_ in d.items():
                    tmp_data[k_] = self._get_join(k_, data)(v_)

                #tmp_data[k] = self._get_join(k, data)(tmp_data[k])

        for k, v in parent_data.items():
            if k not in tmp_data:
                tmp_data[k] = v

        tmp_data.activate(self.name)

        variables = apply_format_map(self.variables, tmp_data)
        
        for k, v in variables.items():
            if k in tmp_data:
                v1 = tmp_data[k]
                if v1 != v:
                    print('{}(name={}).__call__:warning: data overrides variable {!r} value {!r} with {!r}'\
                          .format(type(self).__name__, self.name, k, v, v1))
            else:
                tmp_data[k] = v

        return apply_format_map(self.template, tmp_data)

    def _get_join(self, k, data):
        j = apply_join(self.join.get(k), data)
        if j is None:
            print('{}(name={}).get_join: not implemented {!r}, using default join.'.format(type(self).__name__, self.name, k))
            return lambda lst: ''.join(flatten(lst)) # default is simple join
        return j

class Predicate(object):
    """A predicate function with logical operations (implemented using
    arithmetics operators).
    """
    
    def __init__(self, func = True):
        if isinstance(func, bool):
            func_value = func
            func = lambda data: func_value
        self.func = func

    def __call__(self, data):
        return self.func(data)
        
    def __neg__(self):
        return type(self)(lambda data: not self(data))

    def __add__(self, other):
        if callable(other):
            return type(self)(lambda data: self(data) or other(data))
        return NotImplemented
    __radd__ = __add__

    def __mul__(self, other):
        if callable(other):
            return type(self)(lambda data: self(data) and other(data))
        return NotImplemented
    __rmul__ = __mul__

    
def has(key): # example usage of Predicate
    return Predicate(lambda data: key in data)

def test():
    data = dict(
        project_name = 'example',
        kernels = [
            dict(kernel_name = 'foo',
                 kernel_type = 'void',
                 arguments = [
                     dict(name = 'n',
                          type = 'int*',
                          input = True,
                          value = 'len(x)',
                          depends = 'x',
                     ),
                     dict(name = 'x',
                          type = 'double*',
                          value = 'NULL',
                          shapes = ('n',),
                          output = True,
                     ),
                 ]
            )
        ]
    )

    is_input = Predicate(lambda adata: adata.get('input'))
    is_output = lambda adata: adata.get('output')
    is_scalar_ptr = lambda adata: adata.get('shapes') is None and adata.get('type', 'void').endswith('*')
    
    c_source_template = '''
/* Project name : {project_name} */
{kernels-list}
'''

    kernel_template = '''
/* Kernel name : {kernel_name} */
/* Inputs: {inputs-list} */
/* Outputs: {outputs-list} */
/* Visibles: {visibles-list} */
{kernel_type} wapper_{project_name}_{kernel_name}() {{
  {initialize-list}
  {block-start-list}
  {kernel_name}({arguments-list});
  {block-end-list}
}}
'''
    
    template = Template(dict(
        c_source = c_source_template,
    ))

    def join_initialize(lst):
        stmts = {}
        d = {}
        for i in range(0,len(lst),3):
            stmt, name, deps = lst[i:i+3]
            stmts[name] = stmt
            if deps:
                deps = set(deps.replace(' ', '').split(','))
            else:
                deps = set()
            d[name] = deps
        lst = [n for n in d if not d[n]]
        n_ = None
        while len(lst) < len(d):
            if len(lst) == n_:
                print('join_initialize:WARNING:circular dependence detected!: {!r}'.format(d))
                break
            n_ = len(lst)
            for n, deps in d.items():
                if n in lst:
                    continue
                if not deps.difference(lst):
                    lst.append(n)
                    continue
        return '\n  '.join([stmts[n] for n in lst])
    
    template['kernels'] = Template(
        dict(
            kernels = kernel_template
        ),
        join = {'arguments-list': ', ',
                'inputs-list': ', ',
                'outputs-list': ', ',
                'visibles-list': ', ',
                'initialize-list': join_initialize,
                'block-start-list': '\n  ',
                'block-end-list': '\n  ',
        }
        
    )

    template['kernels']['arguments'] = Template(
        dict(arguments = (is_scalar_ptr, '&{name}', '{name}'),
             inputs = (is_input, '{name}'),
             outputs = (is_output, '{name}'),
             #visibles = (is_output+is_input, '{name}'),
             visibles = [(is_input, '{name}'), (is_output, '{name}')],
             initialize = (has('value'), ['{name} = {value};', '{name}', (has('depends'),'{depends}', '')]),
             block = [Block('/* start {name} */', '/* end {name} */')]
        ),
    )
    
    result = template(data)

    for k, v in result.items():
        print('-'*20)
        print(k+':')
        print('-'*20)
        print(v)
        print('='*20)


        
    
if __name__ == '__main__':
    test()
