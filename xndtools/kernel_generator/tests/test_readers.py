from xndtools.kernel_generator.readers import PrototypeReader


def test_PrototypeReader():
    source = '''
    int foo ();
    int foo (void);
    int foo(  void  /* hello */);
    int foo (int a, float * a, long, double *);
    int foo (int a  , float *a  , long, double*);
    int foo (int a, float * a, long, double *, long   long a  [ ] );
    int foo (int a,
             float * a, long,
             double *, long   long a  [
]
            );

    void bar0();
    extern long long bar ();
    extern long   long   __stdcall bar ();
    static double * *
    car ();
    '''

    reader = PrototypeReader()

    counter = 0
    for p in reader(source):
        if p['name'] == 'foo':
            counter += 1
            for i, a in enumerate(p['arguments']):
                if i == 0:
                    assert a['name'] == 'a'
                    assert a['type'] == 'int'
                if i == 1:
                    assert a['name'] == 'a'
                    assert a['type'] == 'float'
                    assert a['left_modifier'] == '*'
                if i == 2:
                    assert a['name'] == 'arg2'
                    assert a['type'] == 'long'
                if i == 3:
                    assert a['name'] == 'arg3'
                    assert a['type'] == 'double'
                    assert a['left_modifier'] == '*'
                if i == 4:
                    assert a['name'] == 'a'
                    assert a['type'] == 'long long'
                    assert a['right_modifier'] == '[]'
        if p['name'] == 'bar0':
            counter += 1
            assert p['type'] == 'void'
        if p['name'] == 'bar':
            counter += 1
            assert p['type'] == 'long long'
            assert p['specifiers'] == 'extern'

        if p['name'] == 'car':
            counter += 1
            assert p['type'] == 'double'
            assert p['specifiers'] == 'static'
            assert p['left_modifier'] == '**'

    assert counter == source.count(';'), repr(counter)
