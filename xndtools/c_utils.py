""" Utilities for manipulating C sources.

"""
# Author: Pearu Peterson
# Created: July 2018

import os
import re

def find_include(include, include_dirs):
    """ Return path to include file in given include directories.
    """
    if os.path.isfile(include):
        return include
    for d in include_dirs:
        path = os.path.join(d, include)
        if os.path.isfile(path):
            return path
    return include

def resolve_includes(source, include_dirs = [], skip_includes = []):
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
        include_file = find_include(m.group(1), include_dirs)
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

def get_c_blocks(source,
                 _wdir=dict(counter=0, blocks={}),
):
    """ Replace all {}-blocks with generated keys.

    Parameters
    ----------
    source : str
      Specify C source.

    Returns
    -------
    new_source : str
      Source with elimanted {}-blocks
    blocks : dict
      Mapping of keys and {}-blocks.
    """
    block_re = r'{[^{}]*}'
    def block_repl(m):
        block = source[slice(*m.span())]
        _wdir['counter'] += 1
        key = '@@@{counter}@@@'.format_map(_wdir)
        _wdir['blocks'][key] = block
        return key
    new_source = re.sub(block_re, block_repl, source, re.MULTILINE | re.DOTALL)
    if '{' in new_source:
        return get_c_blocks(new_source, _wdir=_wdir)
    return new_source, _wdir['blocks']

def remove_comments(source):
    """ Return source without comments.
    """
    comment_re = r'(/[*].*?[*]/)|(//[^\n]*)'
    return re.sub(comment_re,'', source, flags=re.MULTILINE | re.DOTALL)

def get_enums(source):
    """ Return a dictionary of C enum definitions.
    """
    source, blocks = get_c_blocks(source)
    enum_re = r'enum\s+([a-zA-Z_]\w*)\s*(@@@\d+@@@)\s*;'
    enums = {}
    for name, key in re.findall(enum_re, source, re.MULTILINE | re.DOTALL):
        block = blocks[key]
        enums[name] = list(map(str.strip, block[1:-1].split(',')))
    return enums

def _normalize_typespec(typespec):
    lst = typespec.split()
    r = lst[0]
    for w in lst[1:]:
        sep = ''
        if r[-1].isalnum() and w[0].isalnum():
            sep = ' '
        r = r + sep + w
    return r

def _get_block_items(block, blocks): # helper function for get_structs
    union_match = re.compile(r'union\s*(@@@\d+@@@)').match
    rname_re = r'\w*[a-zA-Z_]' # reversed name
    rname_match = re.compile(rname_re).match
    struct_match = re.compile(r'struct\s*(@@@\d+@@@)\s*([a-zA-Z_]\w*)').match
    items = []
    for stmt in block[1:-1].split(';')[:-1]:
        stmt = stmt.strip()
        if stmt.startswith('PyObject_HEAD'):
            items.append('PyObject_HEAD')
            stmt = stmt.split(None, 1)[1]
        m = union_match(stmt)
        if m is not None:
            key,  = m.groups()
            items.append(('union',_get_block_items(blocks[key], blocks)))
            continue
        m = struct_match(stmt)
        if m is not None:
            key, name = m.groups()
            items.append(('struct',_get_block_items(blocks[key], blocks), name))
            continue
        size = None
        if stmt.endswith(']'): # <typespec> <name>[<size>]
            i = stmt.index('[')
            size = stmt[i+1:-1].strip()
            stmt = stmt[:i]
        name = rname_match(stmt[::-1]).group(0)[::-1].strip()
        assert name is not None, repr(stmt)
        typespec = stmt[:-len(name)].strip()
        if typespec.startswith('alignas'):
            typespec = typespec.split(' ', 1)[1]
        typespec = _normalize_typespec(typespec)
        items.append((typespec,name,size))
    return items

def expand_extern_C(source, blocks):
    extern_C_re = r'extern\s+["]C["]\s*(@@@\d+@@@)'
    def repl(m):
        key, = m.groups()
        return 'extern "C" ' + blocks[key]
    return re.sub(extern_C_re, repl, source, flags=re.MULTILINE | re.DOTALL)
    
def get_structs(source):
    """ Return a dictionary of C struct definitions.
    """
    source, blocks = get_c_blocks(source)
    source = expand_extern_C(source, blocks)

    struct_patterns = [
        # `typedef struct word1 word2;`          key=word1, name=word2; word1 will be replaced with word2
        r'typedef\s+struct\s*([a-zA-Z_]\w*)\s+([a-zA-Z_]\w*)\s*;',
        # `typedef struct {...} word2;`          key={...}, name=word2
        r'typedef\s+struct\s*(@@@\d+@@@)\s*([a-zA-Z_]\w*)\s*;',
        # `typedef struct word1 {...} word2;`    key={...}, name=word2; word1 is unused
        r'typedef\s+struct\s*[a-zA-Z_]\w*\s*(@@@\d+@@@)\s*([a-zA-Z_]\w*)\s*;', 
        # `struct word1 {...}`                   key=word1, name={...}; needs a key-name swap
        r'struct\s+([a-zA-Z_]\w*)\s*(@@@\d+@@@)\s*;'
    ]
    structs = {}
    for r in re.findall('|'.join(struct_patterns), source, re.MULTILINE | re.DOTALL):
        key, name = filter(bool, r)
        if name[0]=='@':                         # swap
            key, name = name, key
        if key[0]=='@':
            if name in structs:                  # replace word1 with word2
                name = structs.pop(name)
            structs[name] = _get_block_items(remove_comments(blocks[key]), blocks)
        else:
            structs[key] = name
    return structs

def _test():
    from pprint import pprint
    import sys
    fn = sys.argv[1]
    r, blocks = get_c_blocks(open(fn).read())

    r = get_enums(open(fn).read())
    print('ENUMS:')
    print(r)

    r = get_structs(open(fn).read())
    print('STRUCTS:')
    pprint(r)
    
if __name__ == '__main__':
    _test()
