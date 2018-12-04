from pprint import pprint
import sys

from . import get_c_blocks, get_enums, get_structs


def test():
    fn = sys.argv[1]
    r, blocks = get_c_blocks(open(fn).read())

    r = get_enums(open(fn).read())
    print('ENUMS:')
    print(r)

    r = get_structs(open(fn).read())
    print('STRUCTS:')
    pprint(r)

if __name__ == '__main__':
    test()
