from xndtools.c_utils import parser

def test_get_c_blocks():
    source = '''
struct foobar {
  int a;
} foobar_t
'''
    assert parser.get_c_blocks(source) == (
        '\nstruct foobar @@@1@@@ foobar_t\n',
        {'@@@1@@@': '{\n  int a;\n}'}
    )
