from pyctftools.classiccrypto import decrypt_mono_alphabetic, encrypt_mono_alphabetic


def test_correctness():
    msg = "TEST"
    key = "TEST"
    assert decrypt_mono_alphabetic(encrypt_mono_alphabetic(msg, key), key) == msg
