def test_import_and_version():
    import foritech
    assert hasattr(foritech, "__version__")
    assert isinstance(foritech.__version__, str)
