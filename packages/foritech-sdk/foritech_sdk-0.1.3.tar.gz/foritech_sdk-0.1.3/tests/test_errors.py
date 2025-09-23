from foritech import errors


def test_errors_hierarchy():
    e = errors.EncryptError("x")
    assert isinstance(e, errors.ForitechError)
