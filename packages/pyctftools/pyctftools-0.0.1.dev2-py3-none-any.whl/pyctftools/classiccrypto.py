from typing import Dict, Iterable
import pyctftools.letter_frequencies as lf
from english_words import get_english_words_set

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def strip_text(
    input: str,
    to_lower=False,
    to_upper=False,
    strip_spaces=True,
    strip_specials=True,
    strip_numbers=True,
) -> str:
    input = input.replace("\t", " ")
    input = input.replace("\n", " ").replace("\r", " ")
    if strip_spaces:
        input = input.replace(" ", "")
    if to_lower:
        input = input.lower()
    if to_upper:
        input = input.upper()
    if strip_specials:
        input = "".join(e for e in input if e.isspace() or e.isalnum())
    if strip_numbers:
        input = "".join(e for e in input if not e.isnumeric())
    return input


def dictionary_attack(
    cipher: str,
    keys: Iterable,
    method,
    word_list=get_english_words_set(["web2"], lower=True, alpha=True),
    threshold: float = 1,
) -> Dict:
    if not cipher:
        print("Cipher cannot be empty")
        return {}

    scores = {}
    for key in keys:
        score = 0
        clear = method(cipher, key)
        clear_stripped = strip_text(clear, to_lower=True, strip_spaces=False)
        clear_list = clear_stripped.split(" ")
        for word in clear_list:
            if word in word_list:
                score += 1
        score /= len(clear_list)
        scores[key] = score
        if score >= threshold:
            print(
                f"Found score of {score} using key {key}, resulting in the "
                + "following cleartext:"
            )
            print(clear)
    best_key = max(scores, key=lambda key: scores[key])
    print(
        f"Key with best score is {best_key} with score "
        + f"{round(scores[best_key], 2)} resulting in cleartext:\n"
    )
    print(method(cipher, best_key))
    return scores


def frequency_distribution(
    input: str,
    ignore_case=True,
    ignore_specials=True,
    ignore_numbers=False,
    absolute_frequencies=True,
) -> Dict:
    input = input.replace(" ", "").replace("\t", "")
    if ignore_case:
        input = input.upper()
    if ignore_specials:
        input = "".join(e for e in input if e.isalnum())
    if ignore_numbers:
        input = "".join(e for e in input if not e.isnumeric())

    char_counts = {}
    for e in input:
        if e in char_counts:
            char_counts[e] += 1
        else:
            char_counts[e] = 1

    # Add missing letters, set to 0
    for letter in ALPHABET:
        if letter not in char_counts:
            char_counts[letter] = 0

    if absolute_frequencies:
        return char_counts
    else:
        return {k: round(v / len(input), 4) for (k, v) in char_counts}


def print_frequency_distribution(
    input: str | dict,
    sort_on_count=True,
    ignore_case=True,
    ignore_specials=True,
    ignore_numbers=False,
    include_absolute_frequencies=True,
) -> None:
    MAX_WIDTH = 200

    if isinstance(input, dict):
        if include_absolute_frequencies:
            print(
                "Ignoring include_absolute_frequencies=True since a dict is "
                + "supplied as input"
            )
            include_absolute_frequencies = False
        freq_dist = input
    elif isinstance(input, str):
        # Filter input as required
        input = strip_text(
            input,
            to_upper=ignore_case,
            strip_specials=ignore_specials,
            strip_numbers=ignore_numbers,
        )
        # Calculate frequency distribution
        freq_dist = frequency_distribution(
            input,
            ignore_case,
            ignore_specials,
            ignore_numbers,
            include_absolute_frequencies,
        )

    # Sort the dictionary based on either key or value
    if sort_on_count:
        sorted_dict = dict(sorted(freq_dist.items(), key=lambda k: k[1], reverse=True))
    else:
        sorted_dict = dict(sorted(freq_dist.items()))

    # Calculate total
    total = len(input)
    print(f"Total: {total}")

    for key, value in sorted_dict.items():
        if include_absolute_frequencies:
            rel_freq = value / total
            print(
                f"{key}: {value:<{len(str(total))}} {round(rel_freq * 100, 2):>8}%"
                + f"\t{round(rel_freq * MAX_WIDTH) * '#'}"
            )
        else:
            print(
                f"{key}: {round(value * 100, 2):>8}%\t"
                + f"{round(value * MAX_WIDTH) * '#'}"
            )


def frequency_analysis(input: str, language: str) -> None:
    MAX_WIDTH = 100

    # Check if language is supported
    if language not in lf.SUPPORTED_LANGUAGES:
        print(f"The language {language} is currently not supported")
        return

    # Get frequency distrubutions of ciphertext and language
    cipher_dist = dict(sorted(frequency_distribution(input).items()))
    lang_dist = dict(sorted(lf.SUPPORTED_LANGUAGES[language].items()))

    # Print frequency distributions
    print("The frequency distribution of the input is:")
    # print_frequency_distribution(input, sort_on_count=False)
    print_frequency_distribution(input, sort_on_count=True)
    print(f"\nThe frequency distribution of {language} is:")
    print_frequency_distribution(lang_dist, sort_on_count=True)

    # Determine naive key
    sorted_cipher_dist = sorted(cipher_dist.items(), key=lambda k: k[1], reverse=True)
    sorted_lang_dist = sorted(lang_dist.items(), key=lambda k: k[1], reverse=True)
    naive_key = {}
    for i in range(len(sorted_lang_dist)):
        clear_char = sorted_lang_dist[i][0]
        cipher_char = sorted_cipher_dist[i][0]
        naive_key[clear_char] = cipher_char

    # Print naive key
    print("\nNaive key would be:")
    print(ALPHABET)
    print("".join(naive_key[a] for a in ALPHABET))

    # Print cipher decrypted with naive key
    print("\nIn which case the cleartext would be:")
    print(decrypt_mono_alphabetic(input, naive_key))


def brute_force_shift(input: str):
    return dictionary_attack(input, range(26), decrypt_shift)


def encrypt_shift(input: str, key: int) -> str:
    result = []
    for c in input:
        if c.isalpha():
            if c.islower():
                result.append(chr((ord(c) - ord("a") + key) % 26 + ord("a")))
            else:
                result.append(chr((ord(c) - ord("A") + key) % 26 + ord("A")))
        else:
            result.append(c)
    return "".join(result)


def decrypt_shift(input: str, key: int) -> str:
    return encrypt_shift(input, key * -1)


def encrypt_mono_alphabetic(input: str, key: str | dict) -> str:
    if isinstance(key, str):
        input = input.upper()
        key = key.upper()
        cipher_alphabet = ""
        for e in key + ALPHABET:
            if e not in cipher_alphabet:
                cipher_alphabet += e
        trans_dict = {a: b for (a, b) in zip(ALPHABET, cipher_alphabet)}
        input = "".join(a if a not in trans_dict else trans_dict[a] for a in input)
    elif isinstance(key, dict):
        input = input.upper()
        input = "".join(a if a not in key else key[a] for a in input)
    return input


def decrypt_mono_alphabetic(
    input: str, key: str | dict, for_undefined: str = "lower"
) -> str:
    """Decrypts a message encrypted with a mono alphabetic substitution cipher.
    The key should be the exact key used to encrypt the message
    (i.e. not the inverse) and can be given as a string or as a dict"""
    if isinstance(key, str):
        input = input.upper()
        key = key.upper()
        cipher_alphabet = ""
        for e in key + ALPHABET:
            if e not in cipher_alphabet:
                cipher_alphabet += e
        trans_dict = {a: b for (a, b) in zip(cipher_alphabet, ALPHABET)}
    elif isinstance(key, dict):
        input = input.upper()
        trans_dict = {v: k for k, v in key.items()}  # Invert the translation dict

    match for_undefined:
        case "lower":
            clear = "".join(
                a.lower() if a not in trans_dict else trans_dict[a] for a in input
            )
        case "blank":
            clear = "".join(
                " " if a not in trans_dict else trans_dict[a] for a in input
            )
        case "underscore":
            clear = "".join(
                "_" if a not in trans_dict else trans_dict[a] for a in input
            )
        case _:
            clear = "".join(a if a not in trans_dict else trans_dict[a] for a in input)

    return clear


def generate_vigenere_key(msg, key):
    key = list(key)
    if len(msg) == len(key):
        return key
    else:
        for i in range(len(msg) - len(key)):
            key.append(key[i % len(key)])
    return "".join(key)


def encrypt_vigenere(input, key):
    encrypted_text = []
    key = generate_vigenere_key(input, key)
    for i in range(len(input)):
        char = input[i]
        if char.isupper():
            encrypted_char = chr(
                (ord(char) + ord(key[i]) - 2 * ord("A")) % 26 + ord("A")
            )
        elif char.islower():
            encrypted_char = chr(
                (ord(char) + ord(key[i]) - 2 * ord("a")) % 26 + ord("a")
            )
        else:
            encrypted_char = char
        encrypted_text.append(encrypted_char)
    return "".join(encrypted_text).upper()


def decrypt_vigenere(input, key):
    decrypted_text = []
    key = generate_vigenere_key(input, key)
    for i in range(len(input)):
        char = input[i]
        if char.isupper():
            decrypted_char = chr((ord(char) - ord(key[i]) + 26) % 26 + ord("A"))
        elif char.islower():
            decrypted_char = chr((ord(char) - ord(key[i]) + 26) % 26 + ord("a"))
        else:
            decrypted_char = char
        decrypted_text.append(decrypted_char)
    return "".join(decrypted_text).upper()
