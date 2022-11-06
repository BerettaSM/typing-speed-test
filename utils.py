import random
import webbrowser
from tkinter import messagebox

files = {
    'English': 'words/common_words_en.txt',
    'Português': 'words/common_words_br.txt',
    'Español': 'words/common_words_es.txt',
    'Français': 'words/common_words_fr.txt'
}


def about_messagebox():

    open_git = messagebox.askyesno(title='About', message="""Created by Ramon Saviato.


Email: ramonsaviato@hotmail.com

GitHub: BerettaSM

View profile on GitHub?""")

    if open_git:
        open_github()


def get_random_words(num: int, language: str):

    file = files[language]

    with open(file, encoding='utf-8') as f:
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


def open_github():

    webbrowser.open('https://github.com/BerettaSM')
