from tkinter import ttk
from ttkthemes import ThemedTk

from gui import GUI


def main():
    window = ThemedTk(theme='breeze')
    GUI(window)
    window.mainloop()


if __name__ == '__main__':
    main()
