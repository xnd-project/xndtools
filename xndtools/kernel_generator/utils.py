
import re
import ctypes
import sys
import distutils.sysconfig
import os
import warnings

intent_names = ['input', 'inplace', 'inout', 'output', 'hide']

supported_intent_lst = [
    ('input',),    # argument contains input data that is not modified,
                   # non-contiguous data is copied
    ('inout',),    # argument contains input data that can be modified
                   # inplace, non-contiguous data triggers ValueError
    ('inplace',),  # argument contains input data that can be modified
                   # inplace, non-contigous data is copied from and to
                   # input
    ('hide',),     # argument is removed from the list of function
                   # arguments. The argument contains input data that
                   # is uniquely determined by other input arguments
                   # (such as shape), or the argument is a cache-like
                   # that content can be ignored
    ('output',),   # argument content is modified and returned,
                   # argument is not shown in the input list (implicit
                   # hide), always contiguous
    ('input',   'output'),  #
    ('inout',   'output'),  #
    ('inplace', 'output'),  #
    ('hide',    'output'),  # same as output
]


def is_intent_inany(data):
    return data.get('intent', ()) in [('input',), ('inplace',), ('inout',),
                                      ('input', 'output'),
                                      ('inplace', 'output'),
                                      ('inout', 'output')]


def is_intent_outany(data):
    return data.get('intent', ()) in [('output',), ('input', 'output'),
                                      ('inplace', 'output'),
                                      ('inout', 'output')]


def is_intent_input(data):
    return data.get('intent') == ('input',)


def is_intent_inplace(data):
    return data.get('intent') == ('inplace',)


def is_intent_inout(data):
    return data.get('intent') == ('inout',)


def is_intent_output(data):
    return data.get('intent') == ('output',)


def is_intent_hide(data):
    return data.get('intent') == ('hide',)


def is_intent_input_output(data):
    return data.get('intent') == ('input', 'output')


def is_intent_inplace_output(data):
    return data.get('intent') == ('inplace', 'output')


def is_intent_inout_output(data):
    return data.get('intent') == ('inout', 'output')


def is_fortran(data):
    # only applicable for 2 or more dimensional arrays:
    return data.get('fortran', False)


def is_c(data): return not data.get('fortran', False)


def is_tensor(data):
    return len(data.get('shape', ())) > 1


def is_vector(data):
    return len(data.get('shape', ())) == 1


class NormalizedTypeMap(dict):
    """C type specification map to normalized type name.

    Normalized type name is `<kind><bits>` where <kind> is
    int|float|complex and <bits> is the correspong type bit width.

    Basic usage:
      m = NormalizedTypeMap(
            {'int':'int64'},     # initialized map forces int to be int64
            strip_left=['my_'],  # define strip strings
            strip_right=['_t'])
      m('double') -> 'float64'
      # needs compile time verification. When wrong, use initialize map:
      m('MY_float') -> 'float32'
      m('int')      -> 'int64'
      # bits are defined using types.sizeof(ctypes.c_short):
      m('short_t')  -> 'int16'

    Algorithm:
      0. ctype is C type specification string containing only [A-Za-z0-9_ ]
      1. when ctype is in the map, return the map value
      2. determine ctype kind with re.match. When failed, warn and
         return ctype.
      3. lower ctype, [obsolete: remove 'const' part], strip ctype from
         left and right
      4. if ctypes has `c_+ctype` attribute,
         set bits = ctypes.sizeof(ctypes.`c_+ctype`)
      5. otherwise if ctype ends with digits, assume these are bits
      6. otherwise give up with warning and return ctype
      7. update the map with {ctype:`<kind><bits>`}
      7. return `<kind><bits>`

    """
    # Author: Pearu Peterson
    # Created: April 2018

    def __init__(self, initial={}, strip_left=[], strip_right=[]):
        dict.__init__(self)
        self.update(dict(void='void',
                         bool='bool',
                         int8='int8', int16='int16', int32='int32',
                         int64='int64', int128='int128',
                         uint8='uint8', uint16='uint16', uint32='uint32',
                         uint64='uint64', uint128='uint128',
                         complex32='complex32', complex64='complex64',
                         complex128='complex128', complex256='complex256',
                         complex512='complex512',
                         float16='float16', float32='float32',
                         float64='float64', float128='float128'))

        self.default_zero_map = dict(
            void=None,
            bool='false',
            int8='0', int16='0', int32='0',
            int64='0l', int128='0ll',
            uint8='0', uint16='0', uint32='0u',
            uint64='0ul', uint128='0ull',
            complex32='{0.0f, 0.0f}', complex64='{0.0f, 0.0f}',
            complex128='{0.0, 0.0}', complex256='{0.0lf, 0.0lf}',
            complex512='{0.0llf, 0.0llf}',
            float16='0.0f', float32='0.0f', float64='0.0',
            float128='0.0lf', float256='0.0llf')

        self.strip_left = strip_left
        self.strip_right = strip_right

        self.complex_match = re.compile(r'.*(complex)',
                                        re.IGNORECASE | re.DOTALL).match
        self.complex_match = re.compile(r'.*(complex)',
                                        re.IGNORECASE | re.DOTALL).match
        self.float_match = re.compile(r'.*(float|double)',
                                      re.IGNORECASE | re.DOTALL).match
        self.int_match = re.compile(r'.*(byte|char|short|int|long|signed)',
                                    re.IGNORECASE | re.DOTALL).match
        self.uint_match = re.compile(
            r'.*((unsigned)\s+(byte|char|short|int|long)|size_t|ssize_t|uint|'
            r'ulong|ushort|ubyte|uchar)',
            re.IGNORECASE | re.DOTALL).match
        self.bool_match = re.compile(r'.*(bool)',
                                     re.IGNORECASE | re.DOTALL).match
        self.bits_match = re.compile(r'.*?(?P<bits>\d+)\Z').match

        for k, v in initial.items():
            if v not in self:
                v = self(v)
            if v in self:
                v = self[v]
            self[k] = v

    def get_zero(self, ctype):
        """ Return zero constant value (as string) for given C type specification.
        """
        ntype = self(ctype)
        zero = self.default_zero_map.get(ntype, 'FAILURE')
        if zero == 'FAILURE':
            print('{}({!r}): failed to find zero constant value, returning'
                  ' None.'.format(type(self).__name__, ntype))
            zero = None
        return zero

    def __call__(self, ctype):
        """Return normalized type of given C type specification.

        Parameters
        ----------
        ctype : str
          Specify C type specification.

        Returns
        -------
        name : str
          The normalized type name in the form `<kind><bits>`
        """
        orig_ctype = ctype
        # if ctype.startswith('const '):
        #    ctype = ctype[6:]

        r = self.get(ctype)
        if r is not None:
            return r

        kind = None
        bits = None
        if self.complex_match(ctype):
            kind = 'complex'
        elif self.float_match(ctype):
            kind = 'float'
        elif self.int_match(ctype):
            kind = 'int'
        elif self.uint_match(ctype):
            kind = 'uint'
        elif self.bool_match(ctype):
            kind = 'bool'
            bits = ''
        else:
            print('{}({!r}): failed to determine type kind, returning as is.'
                  .format(type(self).__name__, ctype))
            self[ctype] = '<fill-me-in>'
            return orig_ctype

        if bits is None:
            n = ctype.lower().replace(' ', '')
            for s in self.strip_left:
                if n.startswith(s):
                    n = n[len(s):]
                    break
            for s in self.strip_right:
                if n.endswith(s):
                    n = n[:-len(s)]
                    break

            n = 'c_'+n
            t = getattr(ctypes, n, None)
            bits = None
            if t is not None:
                bits = str(8 * ctypes.sizeof(t))
            else:
                m = self.bits_match(n)
                if m is not None:
                    bits = m.group('bits')
                    try:
                        bits = int(bits)
                    except Exception as e:
                        print('{}: failed to extract type bits from {!r}: {}'
                              .format(type(self).__name__, n, e))
                        bits = None
                    if kind == 'complex':
                        bits = bits * 8
                    if not (bits % 8 == 0 and bits > 0 and bits <= 1024):
                        # unrealistic bit value
                        bits = None

        if bits is not None:
            r = '{}{}'.format(kind, bits)
            self[ctype] = r
            return r

        print('{}({!r}): failed to determine type bits, returning as is.'
              .format(type(self).__name__, ctype))
        self[ctype] = '<fill-me-in>'
        return orig_ctype


class Prototype(dict):
    """ Prototype instance returned by PrototypeReader.
    """

    def __repr__(self):
        return '{}({})'.format(type(self).__name__,
                               ', '.join('{}={}'.format(k, v)
                                         for k, v in self.items()))

    def __str__(self):
        return '{type} {name}({_arguments});'.format(
            _arguments=', '.join(map(str, self['arguments'])) or 'void',
            _specifiers=(self.get('specifiers') or ''),
            _conventions=(self.get('conventions') or ''),
            **self)

    def update_typemap(self, typemap):
        for a in self['arguments']:
            a.update_typemap(typemap)
        typemap(self['type'])

    def signature(self, typemap, kind='ndtypes', prefix=''):
        args = ', '.join(
            [prefix + a.signature(typemap, kind=kind, prototype=self)
             for a in self['arguments']])
        s = ArgumentDeclaration(self).signature(typemap, kind=kind)
        if kind == 'ndtypes':
            return '{} -> {}'.format(args, prefix + s)
        elif kind == 'match':
            return '({}) {}'.format(args, s)
        raise NotImplementedError(repr(kind))

    def get_argument(self, name):
        return self['arguments'][self['argument_map'][name]]

    def set_argument_fortran(self, name):
        a = self.get_argument(name)
        a['fortran'] = True

    def set_argument_c(self, name):
        a = self.get_argument(name)
        a['fortran'] = False

    def set_argument_value(self, name, value):
        # print('{}.set_argument_value({!r}, {!r})'
        #       .format(type(self).__name__, name, value))
        a = self.get_argument(name)
        if value[-1] in '])':
            i = value.index('(')
            assert i != -1, repr(value)
            f = value[:i].strip().lower()
            args = value[i+1:-1].strip()
            if f == 'shape':
                value = 'xnd_fixed_shape_at(&gmk_input_{})'.format(args)
            elif f == 'len':
                value = 'xnd_fixed_shape_at(&gmk_input_{}, 0)'.format(args)
            elif f == 'ndim':
                value = 'xnd_ndim(&gmk_input_{})'.format(args)
            else:
                print('{}.set_argument_value:NOT IMPL:{!r}'
                      .format(type(self).__name__, value))
            if 'value' in a:
                print('{}.set_argument_value:WARNING: overriding {!r} value'
                      ' {!r} with {!r}'.format(type(self).__name__, name,
                                               a['value'], value))
            a['value'] = value
        else:
            a['value'] = value

    def set_argument_depends(self, name, depends):
        a = self.get_argument(name)
        a_depends = a.get('depends')
        if a_depends is None:
            a['depends'] = set(depends)
        else:
            a_depends.update(depends)

    def set_argument_intent(self, name, intent):
        a = self.get_argument(name)

        if isinstance(intent, set):
            intent = tuple(sorted(intent))
        elif isinstance(intent, str):
            intent = intent,

        if 'intent' in a:
            intent = tuple(sorted(a['intent']+intent))
        if intent == ('hide', 'output'):
            intent = ('output',)
        if intent in supported_intent_lst:
            a['intent'] = intent
        else:
            raise ValueError('{}.set_argument_shape:intent {!r} of argument'
                             ' {!r} is not supported.'
                             .format(type(self).__name__, intent, name))

    def set_argument_shape(self, name, shape):
        a = self.get_argument(name)
        a['shape'] = [dict(value=dim) for dim in shape]

    def __get_sorted_arguments(self):  # NOT USED
        """Return a list of argument names sorted in the order of their
        mutual dependecies.  Independent arguments come first.
        """
        raise 0
        d = dict([(a['name'], a.get('depends', set()))
                  for a in self['arguments']])
        args = [n for n in d if not d[n]]
        n_ = None
        while len(args) < len(d):
            if len(args) == n_:
                print('{}.get_sorted_arguments:WARNING:circular dependence'
                      ' detected!: {!r}'.format(type(self).__name__, d))
                args += [n for n in d if n not in args]  # complete arfs
                break
            n_ = len(args)
            for n, depends in d.items():
                if n in args:
                    continue
                if not depends.difference(args):
                    args.append(n)
                    continue
        return args

    def get_input_output_arguments(self):
        input_args, output_args = [], []
        for a in self['arguments']:
            if a.is_intent_outany:
                output_args.append(a)
            if a.is_intent_inany:
                input_args.append(a)
        return input_args, output_args


class ArgumentDeclaration(dict):

    def __repr__(self):
        return '{}({})'.format(type(self).__name__,
                               ', '.join('{}={}'.format(k, v)
                                         for k, v in self.items()))

    def __str__(self):
        return (
            '{type} {_left_modifier} {_qualifiers} {_name}{_right_modifier}'
            .format(
                _type_modifier=(self.get('type_modifier') or ''),
                _left_modifier=(self.get('left_modifier') or ''),
                _right_modifier=(self.get('right_modifier') or ''),
                _qualifiers=(self.get('qualifiers') or ''),
                _name=(self.get('name') or ''),
                **self))

    @property
    def is_scalar(self):
        return not (self.get('left_modifier') or self.get('right_modifier'))

    @property
    def is_scalar_ptr(self):
        return (self.get('left_modifier') == '*'
                and not self.get('right_modifier')
                and not self.get('shape'))

    @property
    def is_array(self):
        return self.get('left_modifier') == '*' and self.get('shape')

    is_intent_inany = property(is_intent_inany)
    is_intent_outany = property(is_intent_outany)
    is_intent_input = property(is_intent_input)
    is_intent_inplace = property(is_intent_inplace)
    is_intent_inout = property(is_intent_inout)
    is_intent_output = property(is_intent_output)
    is_intent_hide = property(is_intent_hide)
    is_intent_input_output = property(is_intent_input_output)
    is_intent_inplace_output = property(is_intent_inplace_output)
    is_intent_inout_output = property(is_intent_inout_output)
    is_fortran = property(is_fortran)
    is_c = property(is_c)
    is_tensor = property(is_tensor)
    is_vector = property(is_vector)

    def update_typemap(self, typemap):
        typemap(self['type'])

    def signature(self, typemap, kind='ndtypes', prototype=None):
        if kind == 'ndtypes':  # obsolete?
            stype = typemap(self['type'])
            name = self.get('name')
            left_modifier = self.get('left_modifier')
            right_modifier = self.get('right_modifier')
            if left_modifier == '*':
                assert not right_modifier
                if name:
                    return '{}(<dimensions> {})'.format(self['name'], stype)
                return '<dimensions> {}'.format(stype)
            assert not left_modifier, repr((left_modifier, str(self),
                                            str(prototype)))
            assert not right_modifier
            if name:
                return '{}({})'.format(self['name'], stype)
            return stype
        if kind == 'match':
            r = ''
            name = self.get('name')
            if name is not None:
                name = name.lower()
                # if prototype is None: # function
                #    repl = '_'
                #    name = name.replace('s',repl).replace('d',repl)
                #       .replace('c', repl).replace('z',repl)
                r += name
            r = (self.get('left_modifier', '') + r
                 + self.get('right_modifier', ''))
            # if self['type'].startswith('const'):
            #    r = 'const ' + r
            return r
        raise NotImplementedError(repr(kind))


def split_expression(expr):
    """ Return a list of subexpressions separated by commas.
    """
    expr = expr.strip()
    if not expr:
        return []
    k = expr.find(',')
    if k == -1:
        return [expr.strip()]

    i = None
    for p_, r_ in zip('([{', ')]}'):
        j = expr.find(p_)
        if j == -1:
            continue
        if i is None or j < i:
            i, p, r = j, p_, r_
    if i is None:
        return [e.strip() for e in expr.split(',')]
    if k < i:
        return [expr[:k].rstrip()] + split_expression(expr[k+1:])
    level = 0
    j = None
    for i_, c in enumerate(expr):
        if c == p:
            level += 1
        elif c == r:
            level -= 1
            if level == 0:
                j = i_
                break
    if j is None:
        raise ValueError('split_expression: failed on {!r}'.format(expr))
    k = expr.find(',', j)
    if k == -1:
        return [expr]
    return [expr[:k].rstrip()] + split_expression(expr[k+1:])


def prettify(source, target='c', skip_emptylines=True):
    """ Simple prettier of source code.
    """
    if target == 'c':
        intent_str = '    '
        intent_count = 0
        next_count = 0
        lines = []
        stmt_match = re.compile(r'\A(if|while|else)\b[^;]*\Z').match
        comment_start_match = re.compile(r'\A\s*/[*]').match
        comment_end_match = re.compile(r'.*?[*]/\s*\Z').match
        comment = False
        for orig_line in source.splitlines():
            cstart = comment_start_match(orig_line)
            cend = comment_end_match(orig_line)
            if comment or cstart:
                comment = not cend
                lines.append(orig_line)
                continue

            line = orig_line.strip() if intent_count else orig_line
            if skip_emptylines and (not line and intent_count):
                continue
            start = line.count('{')
            stop = line.count('}')
            diff = start - stop
            if next_count and diff:
                next_count = 0
            if diff >= 0:
                lines.append(intent_str * (intent_count+next_count) + line)
                intent_count += diff
            else:
                intent_count += diff
                lines.append(intent_str * (intent_count+next_count) + line)
            next_count = 0
            if stmt_match(line) and not diff:
                next_count = 1
        assert intent_count == 0
        return '\n'.join(lines)
    return source


def resolve_path(path, prefix=None, normpath=True):
    """Apply environment variables to path and resolve <...>
    substitutions, return normalized path.

    Parameters
    ----------
    path : str
      Specify path containing slashes as path separators,
      `${...|...}` substrings and `<...>` substrings.
    prefix : {str, None}
      Specify prefix for path

    Returns
    -------
    path : str
      Resolved path.
    """
    sys_prefix = sys.prefix
    site = distutils.sysconfig.get_python_lib()
    path = path.replace('<prefix>', sys_prefix).replace('<site>', site)

    def repl_env(mobj):
        name = mobj.group(0)[2:-1]
        default = None
        if '|' in name:
            name, default = name.split('|', 1)
        value = os.environ.get(name, default)
        if value is not None:
            return value
        warnings.warn(
            f'resolve_path: environment variable {name} not defined.',
            stacklevel=4)
        return mobj.group(0)

    path = re.sub(r'[$][{]([a-zA-Z_][a-zA-Z_\d]*([|][^}]*|))[}]',
                  repl_env, path)
    if not os.path.isabs(path) and prefix is not None:
        path = os.path.join(prefix, path)
    if normpath:
        path = os.path.normpath(path)
    return path


def test_prettify():
    source = '''
foo () {
  a = 1;
  (for i=0; i++; i<10) {
    if (i>=1)
{
    if (i<5)
     a += 1;
}
    }
}
'''
    result = prettify(source)
    expect = '''
foo () {
    a = 1;
    (for i=0; i++; i<10) {
        if (i>=1)
        {
            if (i<5)
                a += 1;
        }
    }
}'''
    assert result == expect, repr((result, expect))


if __name__ == '__main__':
    test_prettify()
