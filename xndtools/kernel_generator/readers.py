"""Readers

Provides the following readers:

  PrototypeReader - reader of C function prototypes

References
----------

  ISO/IEC 9899:1999 specification
    http://www.open-std.org/jtc1/sc22/wg14/www/docs/n1256.pdf
"""
# Author: Pearu Peterson
# Created: April 2018


import re
import os
import configparser
from .utils import Prototype, ArgumentDeclaration


def load_kernel_config(filename):
    if not os.path.isfile(filename):
        print('load_kernel_config: {!r} is not a file.'.format(filename))
        return
    config = configparser.ConfigParser()
    config.read(filename)
    return config


class PrototypeReader(object):
    """ Reader of C function prototypes.

    Usage:

      reader = PrototypeReader()
      source = open(<header filename>).read()
      prototypes = reader(source, include_patterns = [], exclude_patterns = [])

    """
    def __init__(self,
                 extra_specifiers=[],
                 extra_conventions=[],
                 extra_qualifiers=[]):
        self.specifiers = ['inline', 'extern', 'static', 'EXTERN', 'STATIC',
                           'virtual', 'friend'] + extra_specifiers
        # todo: __declspec(...)
        self.conventions = ['__cdecl', '__clrcall', '__stdcall', '__fastcall',
                            '__thiscall', '__vectorcall'] + extra_conventions
        self.qualifiers = ['const', 'volatile', 'restrict'] + extra_qualifiers
        self._type_specs = set(['char', 'short', 'int', 'long', 'float',
                                'double', 'signed', 'unsigned', 'void',
                                '_Bool', '_Complex', 'void', 'struct', 'enum'])
        # _type_specs will contain also qualifiers, specifiers, type
        # declarations. Used to test non-names.

    def resolve_typespec_name(self, source, index=None):
        """Extract argument declaration from source. Returns ArgumentDeclarion
        instance when succesful, otherwise None.

        Argument declaration has the following form

          <type spec> <left modifier> <argument name> <right modifier>

        where
          <type spec> contains words
          <left modifier> matches `[&]` or `[*]+`
          <right modifier> is `[]`

        """
        s = source.strip()
        word_match = re.compile(r'\A[a-zA-Z_]\w*', re.MULTILINE).match
        left_modifier_match = re.compile(r'\A([*][*\s]*|[&])',
                                         re.MULTILINE).match
        right_modifier_match = re.compile(r'\A[\[]\s*[\]]',
                                          re.MULTILINE).match

        remove_white = (lambda s: re.sub(r'\s+', '', s,
                                         flags=re.MULTILINE | re.DOTALL))
        default_name = None
        if index is not None:
            default_name = 'arg{}'.format(index)
        # split source to words
        words = []
        while s:
            m = word_match(s)
            if m is not None:
                word, s = s[:m.end()], s[m.end():].lstrip()
                words.append(word)
                continue
            m = left_modifier_match(s)
            if m is not None:
                word, s = remove_white(s[:m.end()]), s[m.end():].lstrip()
                words.append(word)
                continue
            m = right_modifier_match(s)
            if m is not None:
                word, s = remove_white(s[:m.end()]), s[m.end():].lstrip()
                words.append(word)
                continue
            raise NotImplementedError(repr((s, source)))

        # extract typespec data and name
        attrs = {}
        if words and words[-1] == '[]':
            words = words[:-1]
            attrs['right_modifier'] = '[]'

        # strip type modifiers
        lst = []
        while words and words[0] in self.qualifiers:
            lst.append(words[0])
            words = words[1:]
        if lst:
            attrs['type_modifier'] = ' '.join(lst)

        if not words:
            attrs['type'] = 'void'
        elif len(words) == 1:
            attrs['type'] = words[0]
            attrs['name'] = default_name
        else:
            if words[-1] in self.qualifiers:
                attrs['name'] = default_name
                qualifiers = []
                while words and words[-1] in self.qualifiers:
                    qualifiers.append(words[-1])
                    words = words[:-1]
                attrs['qualifiers'] = ' '.join(reversed(qualifiers))
                if words[-1][0] in '*&':
                    attrs['left_modifier'] = words[-1]
                    attrs['type'] = ' '.join(words[:-1])
                else:
                    attrs['type'] = ' '.join(words)
            else:
                if words[-1][0] in '*&':
                    attrs['name'] = default_name
                    attrs['left_modifier'] = words[-1]
                    attrs['type'] = ' '.join(words[:-1])
                elif words[-2][0] in '*&':
                    attrs['name'] = words[-1]
                    attrs['left_modifier'] = words[-2]
                    attrs['type'] = ' '.join(words[:-2])
                elif words[-1] not in self._type_specs:
                    attrs['name'] = words[-1]
                    attrs['type'] = ' '.join(words[:-1])
                else:
                    attrs['name'] = default_name
                    attrs['type'] = ' '.join(words)
        self._type_specs.update(attrs['type'].split())
        return attrs

    def __call__(self, source, match_patterns=[], exclude_patterns=[]):
        """Extract C function prototypes from a text source.

        Returns a list of Prototype instances.  The Prototype instance is
        basically a dict instance with keys 'type', 'name', 'arguments'
        where arguments is a list of ArgumentDeclaration instances (dict
        with keys 'type', 'name', etc.).

        Patterns are re expressions of function names.  When include
        pattern is given, all prototypes that name do not match any
        include pattern will be skipped.  When function name matches
        exclude pattern, the corresponding prototype will be skipped
        (even when function name matches some include pattern).

        """
        comment_re = r'/[*].*?[*]/'
        cfuncproto_re = (
            r'(?=\n|\A)\s*([A-Za-z_][\w\s*]*)\(([\w,\s*&\\\[\]]*?)\)\s*;')

        # remove /* */ comments:
        source = re.sub(comment_re, '', source,
                        flags=re.MULTILINE | re.DOTALL)
        # resolve line continuations:
        source = source.replace('\\\n', '')
        # remove CPP directive lines:
        source = '\n'.join(line for line in source.split('\n')
                           if not line.startswith('#'))

        _match_patterns = []
        for p in match_patterns:
            if isinstance(p, str):
                p = re.compile(p)
            _match_patterns.append(p)
        _exclude_patterns = []
        for p in exclude_patterns:
            if isinstance(p, str):
                p = re.compile(p)
            _exclude_patterns.append(p)

        prototypes = []
        for typespec_name, arguments in re.findall(cfuncproto_re, source,
                                                   re.MULTILINE | re.DOTALL):
            typespec_name = typespec_name.strip()
            arguments = arguments.strip()
            func_attrs = self.resolve_typespec_name(typespec_name)
            func_name = func_attrs.get('name')
            if not func_name:  # a function must have a name
                continue

            skip = True and _match_patterns
            for p in _match_patterns:
                if p.match(func_name):
                    skip = False
                    break
            if skip:
                print('{}: no match: {}'.format(type(self).__name__,
                                                func_name))
                continue

            skip = False
            for p in _exclude_patterns:
                if p.match(func_name):
                    skip = True
                    break
            if skip:
                print('{}: excluded: {}'.format(type(self).__name__,
                                                func_name))
                continue

            # extract function specifiers
            types, specifiers, conventions = [], [], []
            for word in func_attrs['type'].split():
                if word in self.specifiers:
                    specifiers.append(word)
                elif word in self.conventions:
                    conventions.append(word)
                else:
                    types.append(word)
            if specifiers:
                func_attrs['specifiers'] = ' '.join(specifiers)
            if conventions:
                func_attrs['conventions'] = ' '.join(conventions)
            if types[0] in ['typedef']:
                continue
            func_attrs['type'] = ' '.join(types)

            if func_attrs['type'] in ['else', 'if', 'for', 'while', 'typedef',
                                      'case', 'do', 'switch', 'sizeof',
                                      'return', 'goto', 'case']:
                continue

            assert types, repr(typespec_name)

            # resolve arguments
            args = func_attrs['arguments'] = []
            arg_map = func_attrs['argument_map'] = {}
            if arguments in ['', 'void']:
                pass
            else:
                for i, arg in enumerate(arguments.split(',')):
                    arg = arg.strip()
                    arg_attrs = self.resolve_typespec_name(arg, index=i)
                    args.append(ArgumentDeclaration(arg_attrs))
                    arg_map[args[-1]['name']] = i
            prototype = Prototype(func_attrs)
            prototypes.append(prototype)

        return prototypes


def _main():
    """ Test PrototypeReader on real header files.
    """
    import sys
    counter = 0
    reader = PrototypeReader(
        extra_specifiers=['DEPRECATED', 'LAPACK_DECL', 'MKL_DECLSPEC',
                          'DFTI_EXTERN', 'SQLITE_API', 'SQLITE_DEPRECATED',
                          'SQLITE_EXPERIMENTAL', 'MODULE_SCOPE'],
        extra_conventions=['MKL_CALL_CONV', 'SQLITE_STDCALL'],
    )
    for filename in sys.argv[1:]:
        print(filename)
        source = open(filename).read()
        for p in reader(source, exclude_patterns=[
                r'.*_work\Z', r'.*_\Z', r'\A[A-Z0-9_]+\Z']):
            print(p['name'])
            counter += 1
            pass
    print('counter=', counter)


if __name__ == '__main__':
    _main()
