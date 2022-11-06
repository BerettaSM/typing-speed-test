import random

FILE = 'common_words.txt'


def get_random_words(num: int):
    with open(FILE) as f:
        all_words = [word.strip() for word in f.readlines()]
    return random.sample(all_words, num)


def get_word_differences(expected, actual):
    def compare_letter(a, b):
        return a != b
    return list(map(compare_letter, expected, actual))


def get_correct_typed_characters(expected, actual):
    differences = get_word_differences(expected, actual)
    differences = filter(lambda elem: not elem, differences)
    return len(list(differences))
