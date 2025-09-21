import parutils as u


def test_msc():

    res = u.try_bool(ok_func, 'arg1', 'arg2', kwarg1='val1', kwarg2='val2')
    assert res[0]
    assert res[1] == "ok: ('arg1', 'arg2'), {'kwarg1': 'val1', 'kwarg2': 'val2'}"

    res = u.try_bool(nok_func_args, 'arg1', 'arg2', kwarg1='val1', kwarg2='val2')
    assert not res[0]
    assert str(res[1]) == "test_error: ('arg1', 'arg2'), {'kwarg1': 'val1', 'kwarg2': 'val2'}"

    lst = ['key1=value1', 'key2=value2']
    out = u.list_to_dict(lst)

    d = {'key1': 'value1', 'key2': 'value2'}
    assert out == d

    out = u.replace_from_dict('Hello @@VAR@@', {'VAR': 'world'})
    assert out == 'Hello world'

    u.ttry(nok_func, 'test_error')
    err = "[ttry] Exception caught ('test_error') don't match expected ('test_error_1')"
    u.ttry(u.ttry, err, nok_func, 'test_error_1')
    u.ttry(u.ttry, "[ttry] No exception was caught", ok_func, 'test_error')

    with u.Wtry('test_error'):
        nok_func()
    with u.Wtry("[Wtry] No exception was caught"):
        with u.Wtry('test_error'):
            ok_func()
    err = "[Wtry] Exception caught ('test_error') don't match expected ('test_error_1')"
    with u.Wtry(err):
        with u.Wtry('test_error_1'):
            nok_func()


def nok_func():
    raise Exception('test_error')


def nok_func_args(*args, **kwargs):
    raise Exception(f'test_error: {args}, {kwargs}')


def ok_func(*args, **kwargs):
    return f'ok: {args}, {kwargs}'


if __name__ == '__main__':  # pragma: no cover
    test_msc()
