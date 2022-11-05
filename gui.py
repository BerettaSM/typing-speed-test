from tkinter import *
from tkinter import ttk
from ttkthemes import ThemedTk

from utils import get_random_words, get_word_differences, get_correct_typed_characters

# CONSTANTS
FONT = 'Fira Code'
MAIN_TEXT_FONT = (FONT, 18)
HIGHLIGHT_COLOR = '#b3d9ff'
CORRECT_COLOR = '#47d147'
WRONG_COLOR = '#ff3333'
TIME = 60
NUM_WORDS = 50

# FUNCTIONS


class GUI(ttk.Frame):

    def __init__(self, master):

        super().__init__(master)

        self.master: ThemedTk = master
        self.master.title('Typing Speed Test')

        self.grid(row=0, column=0, sticky=N+W+E+S)
        self.configure(padding=30)

        self.words = []
        self.next_word_start_idx = 0
        self.user_typed_words = []
        self.correct_words = 0
        self.typed_characters = 0
        self.correctly_typed_characters = 0

        # This string represents the timer event.
        self.timer = ''
        self.timer_started = False
        self.elapsed_time = 0

        self.main_label_var = None
        self.main_text_label = None
        self.main_text_area = None
        self.entry: ttk.Entry | None = None
        self.reset_button = None

        self.create_widgets()
        self.register_event_listeners()
        self.reset_state()

    def create_widgets(self):

        self.main_label_var = StringVar(value='READY')
        self.main_text_label = ttk.Label(self, textvariable=self.main_label_var)
        self.main_text_area = Text(self, width=40, height=16, borderwidth=5,
                                   relief='groove', font=MAIN_TEXT_FONT, wrap='word')
        self.main_text_area.configure(state='disabled')
        self.entry = ttk.Entry(self)
        self.reset_button = ttk.Button(self, text='reset', command=self.reset_state)

        # Positioning
        self.main_text_label.grid(row=0, column=0)
        self.main_text_area.grid(row=1, column=0)
        self.entry.grid(row=2, column=0, sticky=W+E)
        self.reset_button.grid(row=3, column=0, sticky=W+E)

        # Configuring
        for child in self.winfo_children():
            child.grid(pady=10)

    def register_event_listeners(self):

        self.entry.bind('<KeyPress>', self.revalidate_state)

    def revalidate_state(self, event):

        # Start the timer if it isn't already.
        if not self.timer_started:
            self.timer_started = True
            self.start_timer()
            self.highlight_next_word()

        curr_word = self.get_current_word()

        # The current entry state.
        user_input = self.entry.get().strip()

        # If user pressed the space bar
        if event.char == ' ':

            # If user input has any character other than a space
            if user_input != '':
                # Append user word to typed words
                self.user_typed_words.append(user_input)
                # Clear the entry widget
                self.entry.delete(0, END)
                # Highlight the next word
                self.highlight_next_word()

            # If the user correctly typed the word
            if curr_word == user_input:
                self.correct_words += 1

            # Get how many characters the user got right
            correct_characters = get_correct_typed_characters(expected=curr_word, actual=user_input)
            self.correctly_typed_characters += correct_characters

        else:
            self.typed_characters += 1

        # print(len(self.main_area.get('1.0', 'end')))

    def get_current_word(self):

        # The highlighted word the user is currently trying to type.

        curr_word_idx = len(self.user_typed_words)
        return self.words[curr_word_idx]

    def highlight_next_word(self):

        tag = 'highlighted'

        curr_word = self.get_current_word()
        start = self.next_word_start_idx
        end = start + len(curr_word)

        if tag in self.main_text_area.tag_names():
            self.main_text_area.tag_delete(tag)

        self.main_text_area.tag_add(tag, f'1.{start}', f'1.{end}')
        self.main_text_area.tag_config(tag, background=HIGHLIGHT_COLOR)

        self.next_word_start_idx = end + 1

    def start_timer(self):

        self.count_down(TIME)

    def count_down(self, count):

        minute = count // 60
        second = count % 60

        self.main_label_var.set(f'Time remaining: {minute:02}:{second:02}')

        if count > 0:

            if count != TIME:
                self.elapsed_time += 1

            self.timer = self.master.after(1000, self.count_down, count - 1)

        else:
            print('Acabou')

    def reset_state(self):

        print(f'Correct words: {self.correct_words}')
        print(f'Typed characters: {self.typed_characters}')
        print(f'Correctly typed characters: {self.correctly_typed_characters}')

        words = get_random_words(num=5)

        if self.timer:
            # Cancel timer
            self.master.after_cancel(self.timer)

        self.elapsed_time = 0
        self.correct_words = 0
        self.typed_characters = 0
        self.correctly_typed_characters = 0
        self.next_word_start_idx = 0
        self.main_label_var.set(value='READY')
        self.timer_started = False
        self.entry.delete(0, END)

        # Main text widget is disabled to avoid tampering, need to enable it again to modify its contents,
        # then disable it again.
        self.main_text_area.configure(state='normal')
        self.main_text_area.delete('1.0', END)
        self.main_text_area.insert(INSERT, ' '.join(words))
        self.main_text_area.configure(state='disabled')

        self.words = words
        self.user_typed_words = []


# def add_highlighter():
#     if 'start' in text.tag_names():
#         text.tag_delete('start')
#     else:
#         text.tag_add("start", "1.76", "1.150")
#         text.tag_config("start", background="black", foreground="white")
