from pyctftools import classiccrypto as cc


def test_strip():
    input = """a
b c"""
    assert cc.strip_text(input, strip_spaces=False) == "a b c"
