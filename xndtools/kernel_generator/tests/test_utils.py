import pytest
from xndtools.kernel_generator.utils import split_expression, resolve_path

def test_split_expression():
    assert split_expression('') == []
    assert split_expression('  a ') == ['a']
    assert split_expression('  a , b ') == ['a', 'b']
    assert split_expression('a,b,c') == ['a', 'b', 'c']
    assert split_expression('a(b)') == ['a(b)']
    assert split_expression('a(b, c)') == ['a(b, c)']
    assert split_expression('a[b, c]') == ['a[b, c]']
    assert split_expression('a(b, c), d') == ['a(b, c)', 'd']
    assert split_expression('a[b, c], d') == ['a[b, c]', 'd']
    assert split_expression('a, b(c), d(e, f), g(h), i') == ['a', 'b(c)', 'd(e, f)', 'g(h)', 'i']
    assert split_expression('a[b,c[d,e(f,g)]],h') == ['a[b,c[d,e(f,g)]]','h']

def test_resolve_path():
    import os
    import sys
    from distutils.sysconfig import get_python_lib
    site = get_python_lib()
    
    rpath = lambda *args: resolve_path(*args, normpath=False)
    assert rpath('a/b') == 'a/b'
    assert rpath('a/b', 'p') == 'p/a/b'
    assert resolve_path('<prefix>/a') == os.path.join(sys.prefix, 'a')
    assert resolve_path('<site>/a') == os.path.join(site, 'a')

    os.environ['TEST_RESOLVE_PATH'] = 'foo'
    assert resolve_path('${TEST_RESOLVE_PATH}/a') == os.path.join('foo','a')
    with pytest.warns(UserWarning):
        assert resolve_path('${TEST_RESOLVE_PATH_NOT_EXISTING}/a') == os.path.join('${TEST_RESOLVE_PATH_NOT_EXISTING}','a')

    assert resolve_path('${TEST_RESOLVE_PATH_NOT_EXISTING|bar}/a') == os.path.join('bar','a')
    assert resolve_path('${TEST_RESOLVE_PATH_NOT_EXISTING|<prefix>}/a') == os.path.join(sys.prefix,'a')
    assert resolve_path('p/${TEST_RESOLVE_PATH_NOT_EXISTING|}/a') == os.path.join('p','a')
