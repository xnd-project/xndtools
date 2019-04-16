from xndtools.c_utils import preprocessor


def test_remove_comments():
    source = '''
// Hello World
int a = 1;
/* this is a comment
 * asdfasdfasdf
 */
int b;// asdf
'''
    assert preprocessor._remove_comments(source) == '''

int a = 1;

int b;
'''


def test_resolve_macros():
    source = '''
#ifdef ASDF
int a = 1;
#else
int b = 2;
#endif
'''
    assert preprocessor._resolve_macros(source) == '''

int b = 2;

'''
    assert preprocessor._resolve_macros(source, {'ASDF'}) == '''

int a = 1;

'''


def test_preprocessor():
    preprocessor.preprocess('''
#include <stdio.h>

int a = 1;
    ''')
