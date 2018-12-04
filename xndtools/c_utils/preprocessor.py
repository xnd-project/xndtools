import os
import re
import subprocess
import shutil


def preprocess(source, include_dirs=(), skip_includes=()):
    """ Preprocess c source files naively or with compiler

    """
    source = _remove_comments(source)
    source = _resolve_includes(source, include_dirs=include_dirs, skip_includes=skip_includes)
    source = _resolve_macros(source, identifiers={})
    return source


def _remove_comments(source):
    """ Return source without comments.
    """
    comment_re = r'(/[*].*?[*]/)|(//[^\n]*)'
    return re.sub(comment_re,'', source, flags=re.MULTILINE | re.DOTALL)


def _resolve_includes(source, include_dirs=(), skip_includes=()):
    """ Return source with includes resolved.

    Unresolved includes are ignored.

    Parameters
    ----------
    source : str
      Specify C source code.
    include_dirs : list
      Specify a list include directories.

    Returns
    -------
    source : str
      Source with resolved includes.

    """
    include_re = r'#include\s*[<"]([^"<>]+)[>"]'
    def include_repl(m):
        include_file = _find_include(m.group(1), include_dirs)
        if not os.path.isfile(include_file) or include_file in skip_includes:
            #print('skip', include_file)
            return source[slice(*m.span())]
        print('including', include_file)
        f = open(include_file)
        include_content = remove_comments(f.read())
        f.close()
        skip_includes.append(include_file)
        return resolve_includes(include_content, include_dirs = include_dirs, skip_includes = skip_includes)
    return re.sub(include_re, include_repl, source, re.MULTILINE)


def _find_include(include, include_dirs):
    """ Return path to include file in given include directories.
    """
    if os.path.isfile(include):
        return include
    for d in include_dirs:
        path = os.path.join(d, include)
        if os.path.isfile(path):
            return path
    return include


def _resolve_macros(source, identifiers=set()):
    """ Return source with macros evaluated

    Only basic handling for now of several macros
      - #ifdef, #else, #endif
    """
    ifdef_re = r'#ifdef (\w+)(.*?)(?:#else(.*?))?#endif'

    def macro_repl(m):
        identifier, true_stmt, false_stmt = m.groups()
        if identifier in identifiers:
            return true_stmt
        else:
            return false_stmt

    return re.sub(ifdef_re, macro_repl, source, flags=re.MULTILINE | re.DOTALL)
