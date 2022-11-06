from tkinter import *
from tkinter import ttk
from ttkthemes import ThemedTk

from utils import get_random_words, get_word_differences, get_correct_typed_characters

# ------------------ CONSTANTS ---------------- #
TIME = 60
NUM_WORDS = 50
FONT = 'Fira Code'
MAIN_TEXT_FONT = (FONT, 18)
HIGHLIGHT_COLOR = '#b3d9ff'
CORRECT_COLOR = '#47d147'
WRONG_COLOR = '#ff3333'
CORRECT_LETTER_TAG = 'correct letter'
CORRECT_WORD_TAG = 'correct word'
WRONG_LETTER_TAG = 'wrong letter'
WRONG_WORD_TAG = 'wrong word'
HIGHLIGHT_TAG = 'highlighted'
# --------------------------------------------- #


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

        self.update_tracer_id = None
        self.entry_val = None
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
        self.entry_val = StringVar()
        self.entry = ttk.Entry(self, textvariable=self.entry_val)
        self.reset_button = ttk.Button(self, text='reset', command=self.reset_state)

        # Positioning
        self.main_text_label.grid(row=0, column=0)
        self.main_text_area.grid(row=1, column=0)
        self.entry.grid(row=2, column=0, sticky=W+E)
        self.reset_button.grid(row=3, column=0, sticky=W+E)

        # Tags for highlighting
        self.main_text_area.tag_config(HIGHLIGHT_TAG, background=HIGHLIGHT_COLOR)
        self.main_text_area.tag_config(CORRECT_LETTER_TAG, background=HIGHLIGHT_COLOR, foreground=CORRECT_COLOR)
        self.main_text_area.tag_config(WRONG_LETTER_TAG, background=HIGHLIGHT_COLOR, foreground=WRONG_COLOR)
        self.main_text_area.tag_config(CORRECT_WORD_TAG, foreground=CORRECT_COLOR)
        self.main_text_area.tag_config(WRONG_WORD_TAG, foreground=WRONG_COLOR)

        # Configuring
        for child in self.winfo_children():
            child.grid(pady=10)

    def register_event_listeners(self):

        self.update_tracer_id = self.entry_val.trace('w', self.revalidate_state)

    def revalidate_state(self, *args):

        # Start the timer if it isn't already.
        if not self.timer_started:
            self.timer_started = True
            self.start_timer()

        curr_word = self.get_current_word()  # TODO: If this is None, all words were traversed and program should exit.

        # The current entry state.
        user_input = self.entry_val.get()
        stripped_user_input = user_input.strip()

        # Update word highlighting
        self.update_current_word_highlighting()

        # If user pressed the space bar
        if len(user_input) > 0 and user_input[-1] == ' ':

            curr_word_start_idx = self.next_word_start_idx
            curr_word_end_idx = curr_word_start_idx + len(curr_word)

            # If user input has any character other than a space
            if len(stripped_user_input) > 0:
                # Append user word to typed words
                self.user_typed_words.append(user_input)
                # Clear the entry widget
                self.entry.delete(0, END)
                # Update next word's start index
                self.next_word_start_idx += len(curr_word) + 1  # 1 is the space in between words

            self.clear_word_highlighting_tags(curr_word_start_idx, curr_word_end_idx)

            # If the user correctly typed the word
            if curr_word == stripped_user_input:
                self.correct_words += 1
                self.highlight_tag_word_as_completed(curr_word_start_idx, curr_word_end_idx, correct_word=True)

            else:
                self.highlight_tag_word_as_completed(curr_word_start_idx, curr_word_end_idx, correct_word=False)

            # Get how many characters the user got right
            correct_characters = get_correct_typed_characters(expected=curr_word, actual=stripped_user_input)
            self.correctly_typed_characters += correct_characters

            self.update_current_word_highlighting()

        else:
            self.typed_characters += 1

    def get_current_word(self):

        # The highlighted word the user is currently trying to type.

        try:
            curr_word_idx = len(self.user_typed_words)
            return self.words[curr_word_idx]

        except IndexError:
            return None

    def update_current_word_highlighting(self):

        curr_word = self.get_current_word()
        start = self.next_word_start_idx
        end = start + len(curr_word)

        user_input = self.entry_val.get().strip()
        user_input_len = len(user_input)

        differences = get_word_differences(curr_word, user_input)

        # If user inputted more characters than current word has, there's no need to update the highlighting.
        if user_input_len <= len(differences):

            self.clear_word_highlighting_tags(start, end)

            for i in range(user_input_len):

                # Compare the words, letter by letter,
                # painting that letter green if it's right,
                # red if it's wrong.

                letter_is_right = not differences[i]

                section_start = start + i
                section_end = section_start + 1

                if letter_is_right:
                    self.main_text_area.tag_add(CORRECT_LETTER_TAG, f'1.{section_start}', f'1.{section_end}')

                else:
                    self.main_text_area.tag_add(WRONG_LETTER_TAG, f'1.{section_start}', f'1.{section_end}')

            remainder_start = start + user_input_len
            # Normal highlight for remainder of the word if there's no more input to compare to.
            self.main_text_area.tag_add(HIGHLIGHT_TAG, f'1.{remainder_start}', f'1.{end}')

    def clear_word_highlighting_tags(self, start_index, end_index):
        # Clear all current tags
        for tag in (HIGHLIGHT_TAG, CORRECT_LETTER_TAG, WRONG_LETTER_TAG):
            self.main_text_area.tag_remove(tag, f'1.{start_index}', f'1.{end_index}')

    def highlight_tag_word_as_completed(self, start_index, end_index, correct_word=False):

        tag = CORRECT_WORD_TAG if correct_word else WRONG_WORD_TAG

        self.main_text_area.tag_add(tag, f'1.{start_index}', f'1.{end_index}')

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

        # Debugging
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

        # Need to momentarily disable the trace, otherwise resetting the entry input would trigger a revalidation
        self.entry_val.trace_vdelete('w', self.update_tracer_id)
        self.entry_val.set('')
        self.update_tracer_id = self.entry_val.trace('w', self.revalidate_state)

        # Main text widget is disabled to avoid tampering, need to enable it to modify its contents,
        # then disable it again.
        self.main_text_area.configure(state='normal')
        self.main_text_area.delete('1.0', END)
        self.main_text_area.insert(INSERT, ' '.join(words))
        self.main_text_area.configure(state='disabled')

        self.words = words
        self.user_typed_words = []
        self.update_current_word_highlighting()
