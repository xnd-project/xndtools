

from xndtools.kernel_generator.utils import split_expression

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
