import re


def get_c_blocks(source, _wdir=dict(counter=0, blocks={})):
    """ Recursively replace all {}-blocks with generated keys.

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
            print('found union!')
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
        print('=======', stmt)
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
            structs[name] = _get_block_items(blocks[key], blocks)
        else:
            structs[key] = name
    return structs
