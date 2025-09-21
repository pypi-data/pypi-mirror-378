from pyctftools import classiccrypto as cc


def test_enc_lower_1():
    assert cc.encrypt_shift("a", 1) == "b"


def test_enc_lower_2():
    for letter in cc.ALPHABET.lower():
        assert cc.encrypt_shift(letter, 26) == letter


def test_enc_lower_3():
    assert cc.encrypt_shift("z", 1) == "a"


def test_enc_lower_4():
    assert cc.encrypt_shift("a", -1) == "z"


def test_enc_upper_2():
    for letter in cc.ALPHABET:
        assert cc.encrypt_shift(letter, 26) == letter


def test_dec_lower_1():
    assert cc.decrypt_shift("b", 1) == "a"


def test_dec_lower_2():
    for letter in cc.ALPHABET.lower():
        assert cc.decrypt_shift(letter, 26) == letter


def test_dec_lower_3():
    assert cc.decrypt_shift("a", 1) == "z"


def test_dec_lower_4():
    assert cc.decrypt_shift("z", -1) == "a"


def test_dec_upper_2():
    for letter in cc.ALPHABET:
        assert cc.decrypt_shift(letter, 26) == letter
