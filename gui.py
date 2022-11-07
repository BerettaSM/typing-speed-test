import io
from tkinter import *
from tkinter import ttk

from ttkthemes import ThemedTk
from PIL import Image, ImageTk

from utils import files, about_messagebox
from utils import get_random_words, get_word_differences, get_correct_typed_characters
from images import ICON

# ------------------ CONSTANTS ---------------- #
TIME_IN_SECONDS = 60
NUM_WORDS = 200
FONT = 'Fira Code'
TITLE_TEXT_FONT = (FONT, 24)
MAIN_TEXT_FONT = (FONT, 18)
BUTTON_TEXT_FONT = (FONT, 14)
BACKGROUND_COLOR = '#FFFFF0'
HIGHLIGHT_COLOR = '#94CFEB'
HIGHLIGHT_BORDER_COLOR = '#4EB5EA'
CORRECT_COLOR = '#47D147'
WARNING_COLOR = '#FCB814'
WRONG_COLOR = '#FF3333'
CORRECT_TAG = 'correct letter'
WRONG_TAG = 'wrong letter'
HIGHLIGHT_TAG = 'highlighted'
CENTER_TAG = 'center'
# --------------------------------------------- #


class GUI(ttk.Frame):

    def __init__(self, master):

        super().__init__(master)

        self.master: ThemedTk = master
        self.master.title('Typing Speed Test')
        self.master.resizable(width=False, height=False)

        icon = ImageTk.PhotoImage(Image.open(io.BytesIO(ICON)))
        self.master.wm_iconphoto(False, icon)

        self.grid(row=0, column=0, sticky=N+W+E+S)
        self.configure(padding=30)

        self.style = None

        self.language = None
        self.language_options = None

        self.words = []
        self.next_word_start_idx = 0
        self.user_typed_words = []
        self.correct_words = 0
        self.typed_characters = 0
        self.correctly_typed_characters = 0

        self.last_run_cpm = None
        self.last_run_ccpm = None
        self.last_run_wpm = None
        self.last_run_accuracy = None

        # This string represents the timer event.
        self.timer = ''
        self.timer_started = False

        self.info_panel = None

        self.cpm_var = None
        self.cpm_label = None
        self.cpm_dif_var = None
        self.cpm_dif_label = None
        self.ccpm_var = None
        self.ccpm_label = None
        self.ccpm_dif_var = None
        self.ccpm_dif_label = None
        self.wpm_var = None
        self.wpm_label = None
        self.wpm_dif_var = None
        self.wpm_dif_label = None
        self.accuracy_var = None
        self.accuracy_label = None
        self.accuracy_diff_var = None
        self.accuracy_diff_label = None

        self.main_label_var = None
        self.title_label = None
        self.main_text_area = None

        self.input_panel = None

        self.update_tracer_id = None
        self.entry_val = None
        self.entry: ttk.Entry | None = None
        self.reset_button = None

        self.create_widgets()
        self.register_event_listeners()
        self.reset_state()

    def create_widgets(self):

        my_menu = Menu(self.master)
        self.master.config(menu=my_menu)
        self.master.option_add('*tearOff', False)
        file_menu = Menu(my_menu)
        my_menu.add_cascade(label='File', menu=file_menu)
        help_menu = Menu(my_menu)
        my_menu.add_cascade(label='Help', menu=help_menu)
        file_menu.add_command(label='Quit', command=self.master.quit)
        help_menu.add_command(label='About', command=about_messagebox)

        languages = list(files.keys())

        # Setup
        self.language = StringVar()
        self.language_options = ttk.OptionMenu(self, self.language,
                                               languages[0], *languages,
                                               command=self.language_changed)

        self.main_label_var = StringVar()
        self.title_label = ttk.Label(self, textvariable=self.main_label_var)

        self.info_panel = ttk.Frame(self)
        self.cpm_var = StringVar(value='CPM: ---')
        self.cpm_label = ttk.Label(self.info_panel, textvariable=self.cpm_var)
        self.cpm_dif_var = StringVar()
        self.cpm_dif_label = ttk.Label(self.info_panel, textvariable=self.cpm_dif_var)
        self.ccpm_var = StringVar(value='CCPM: ---')
        self.ccpm_label = ttk.Label(self.info_panel, textvariable=self.ccpm_var)
        self.ccpm_dif_var = StringVar()
        self.ccpm_dif_label = ttk.Label(self.info_panel, textvariable=self.ccpm_dif_var)
        self.wpm_var = StringVar(value='WPM: ---')
        self.wpm_label = ttk.Label(self.info_panel, textvariable=self.wpm_var)
        self.wpm_dif_var = StringVar()
        self.wpm_dif_label = ttk.Label(self.info_panel, textvariable=self.wpm_dif_var)
        self.accuracy_var = StringVar(value='ACC: ---')
        self.accuracy_label = ttk.Label(self.info_panel, textvariable=self.accuracy_var)
        self.accuracy_diff_var = StringVar()
        self.accuracy_diff_label = ttk.Label(self.info_panel, textvariable=self.accuracy_diff_var)

        self.main_text_area = Text(self)
        self.input_panel = ttk.Frame(self)
        self.entry_val = StringVar()
        self.entry = ttk.Entry(self.input_panel, textvariable=self.entry_val)
        self.reset_button = ttk.Button(self.input_panel, command=self.reset_state)

        # Positioning
        self.language_options.grid(row=0, column=0)
        self.title_label.grid(row=1, column=0)

        self.info_panel.grid(row=2, column=0)
        self.cpm_label.grid(row=0, column=0)
        self.cpm_dif_label.grid(row=0, column=1)
        self.ccpm_label.grid(row=0, column=2)
        self.ccpm_dif_label.grid(row=0, column=3)
        self.wpm_label.grid(row=0, column=4)
        self.wpm_dif_label.grid(row=0, column=5)
        self.accuracy_label.grid(row=0, column=6)
        self.accuracy_diff_label.grid(row=0, column=7)

        self.main_text_area.grid(row=3, column=0)
        self.input_panel.grid(row=4, column=0)
        self.entry.grid(row=0, column=1, sticky=N+W+S+E)
        self.reset_button.grid(row=0, column=0, sticky=N+W+S+E)

        # Configuring
        self.configure(padding='30')
        for child in self.winfo_children():
            child.grid(pady=10)

        self.info_panel.grid()
        for i, child in enumerate(self.info_panel.winfo_children()):
            if i in (2, 4, 6):
                child.grid(padx=(15, 0))

        self.main_text_area.configure(width=45, height=10, borderwidth=0)
        self.main_text_area.configure(wrap='word', state='disabled')
        self.input_panel.configure(padding='10')
        self.entry.grid(padx=(10, 0))
        self.entry.focus_set()
        self.reset_button.configure(text='Reset', width=10)

        # Styling
        self.style = ttk.Style()
        self.title_label.configure(font=TITLE_TEXT_FONT, background=BACKGROUND_COLOR)
        for child in self.info_panel.winfo_children():
            if child.winfo_class() == 'TLabel':
                child: ttk.Label
                child.configure(font=BUTTON_TEXT_FONT, background=BACKGROUND_COLOR)

        self.main_text_area.configure(font=MAIN_TEXT_FONT)
        self.main_text_area.configure(highlightbackground=HIGHLIGHT_BORDER_COLOR, highlightthickness=1)
        self.entry.configure(justify='center', font=TITLE_TEXT_FONT, width=26)
        self.style.configure('TButton', font=BUTTON_TEXT_FONT)
        self.style.configure('TFrame', background=BACKGROUND_COLOR)

        # Tags for highlighting
        self.main_text_area.tag_config(HIGHLIGHT_TAG, background=HIGHLIGHT_COLOR)
        self.main_text_area.tag_config(CORRECT_TAG, foreground=CORRECT_COLOR)
        self.main_text_area.tag_config(WRONG_TAG, foreground=WRONG_COLOR)

        # Tag for centering
        self.main_text_area.tag_config(CENTER_TAG, justify='center')

    def register_event_listeners(self):

        self.update_tracer_id = self.entry_val.trace('w', self.revalidate_state)
        self.master.bind('<Return>', self.reset_state)
        # Disable scrolling with mouse.
        self.main_text_area.bind('<MouseWheel>', lambda e: 'break')

    def language_changed(self, *args):

        self.reset_state()

    def revalidate_state(self, *args):

        # Start the timer if it isn't already.
        if not self.timer_started:
            self.timer_started = True
            self.start_timer()

        curr_word = self.get_current_word()

        # The current entry state.
        user_input = self.entry_val.get().lower()
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

                # Update next word's start index
                self.next_word_start_idx += len(curr_word) + 1  # +1 is the space in between words.

            # Clear the entry widget, this means the widget will never hold a white space.
            self.entry.delete(0, END)

            self.clear_word_highlighting_tags(curr_word_start_idx, curr_word_end_idx)

            # If the user correctly typed the word
            if curr_word == stripped_user_input:
                self.correct_words += 1
                self.highlight_tag_word_as_completed(curr_word_start_idx, curr_word_end_idx, correct_word=True)

            # User got it wrong.
            else:
                self.highlight_tag_word_as_completed(curr_word_start_idx, curr_word_end_idx, correct_word=False)

            # Get how many characters the user got right
            correct_characters = get_correct_typed_characters(expected=curr_word, actual=stripped_user_input)
            self.correctly_typed_characters += correct_characters

            # If this is None, all words were traversed and program should exit.
            curr_word = self.get_current_word()

            if curr_word:
                self.update_current_word_highlighting()

            else:
                self.trigger_end_stats()

            # Auto-scroll to keep upcoming words in view.
            next_few_characters = 100
            self.main_text_area.see(f'1.{curr_word_end_idx + next_few_characters}')

        else:
            self.typed_characters += 1

    def get_current_word(self):

        # The highlighted word the user is currently trying to type.

        try:
            curr_word_idx = len(self.user_typed_words)
            return self.words[curr_word_idx]

        except IndexError:
            # All words were traversed.
            return None

    def update_current_word_highlighting(self):

        curr_word = self.get_current_word()
        start = self.next_word_start_idx
        end = start + len(curr_word)

        user_input = self.entry_val.get().strip().lower()
        user_input_len = len(user_input)

        differences = get_word_differences(curr_word, user_input)

        # If user inputted more characters than current word has, there's no need to update the highlighting.
        if user_input_len <= len(differences):

            self.clear_word_highlighting_tags(start, end)

            # Normal background highlight
            self.main_text_area.tag_add(HIGHLIGHT_TAG, f'1.{start}', f'1.{end}')

            # self.entry_val.set('')

            for i in range(user_input_len):

                # Compare the words, letter by letter,
                # painting that letter green if it's correct,
                # red if it's wrong.

                letter_is_right = not differences[i]

                letter_start_idx = start + i
                letter_end_idx = letter_start_idx + 1

                if letter_is_right:
                    self.main_text_area.tag_add(CORRECT_TAG, f'1.{letter_start_idx}', f'1.{letter_end_idx}')

                else:
                    self.main_text_area.tag_add(WRONG_TAG, f'1.{letter_start_idx}', f'1.{letter_end_idx}')

    def clear_word_highlighting_tags(self, start_index, end_index):
        # Clear all tags in between indices.
        for tag in (HIGHLIGHT_TAG, CORRECT_TAG, WRONG_TAG):
            self.main_text_area.tag_remove(tag, f'1.{start_index}', f'1.{end_index}')

    def highlight_tag_word_as_completed(self, start_index, end_index, correct_word=False):

        tag = CORRECT_TAG if correct_word else WRONG_TAG

        self.main_text_area.tag_add(tag, f'1.{start_index}', f'1.{end_index}')

    def start_timer(self):

        self.count_down(TIME_IN_SECONDS)

    def count_down(self, count):

        minute = count // 60
        second = count % 60

        self.main_label_var.set(f'Time remaining: {minute:02}:{second:02}')

        if count > 0:

            if count < TIME_IN_SECONDS * .15:
                self.title_label.configure(foreground=WRONG_COLOR)

            elif count < TIME_IN_SECONDS * .4:
                self.title_label.configure(foreground=WARNING_COLOR)

            self.timer = self.master.after(1000, self.count_down, count - 1)

        else:
            self.trigger_end_stats()

    def trigger_end_stats(self):

        # CPM - Characters per minute.
        cpm = self.typed_characters
        last_cpm = self.last_run_cpm
        # Corrected CPM.
        ccpm = self.correctly_typed_characters
        last_ccpm = self.last_run_ccpm
        # WPM - Words per minute.
        wpm = self.correct_words
        last_wpm = self.last_run_wpm
        # Accuracy
        acc = round(ccpm / cpm * 100, 2)
        last_run_acc = self.last_run_accuracy

        self.cpm_var.set(f'CPM: {cpm}')
        self.ccpm_var.set(f'CCPM: {ccpm}')
        self.wpm_var.set(f'WPM: {wpm}')
        self.accuracy_var.set(f'ACC: {acc}%')

        if last_cpm is not None:
            dif_cpm = cpm - last_cpm
            dif_ccpm = ccpm - last_ccpm
            dif_wpm = wpm - last_wpm
            dif_acc = round(acc - last_run_acc, 2)

            self.cpm_dif_var.set(f'{"+" if dif_cpm >= 0 else "-"}{abs(dif_cpm)}')
            self.cpm_dif_label.configure(foreground=CORRECT_COLOR if dif_cpm >= 0 else WRONG_COLOR)
            self.ccpm_dif_var.set(f'{"+" if dif_ccpm >= 0 else "-"}{abs(dif_ccpm)}')
            self.ccpm_dif_label.configure(foreground=CORRECT_COLOR if dif_ccpm >= 0 else WRONG_COLOR)
            self.wpm_dif_var.set(f'{"+" if dif_wpm >= 0 else "-"}{abs(dif_wpm)}')
            self.wpm_dif_label.configure(foreground=CORRECT_COLOR if dif_wpm >= 0 else WRONG_COLOR)
            self.accuracy_diff_var.set(f'{"+" if dif_acc >= 0 else "-"}{abs(dif_acc)}%')
            self.accuracy_diff_label.configure(foreground=CORRECT_COLOR if dif_acc >= 0 else WRONG_COLOR)

        self.last_run_cpm = cpm
        self.last_run_ccpm = ccpm
        self.last_run_wpm = wpm
        self.last_run_accuracy = acc

        self.reset_state()

    def reset_state(self, *args):

        language = self.language.get()

        words = get_random_words(num=NUM_WORDS, language=language)

        if self.timer:
            # Cancel timer
            self.master.after_cancel(self.timer)

        self.correct_words = 0
        self.typed_characters = 0
        self.correctly_typed_characters = 0
        self.next_word_start_idx = 0
        self.main_label_var.set(value='READY')
        self.title_label.configure(foreground=CORRECT_COLOR)
        self.timer_started = False

        # Need to momentarily disable the trace, otherwise resetting entry_val would trigger a revalidation.
        self.entry_val.trace_vdelete('w', self.update_tracer_id)
        self.entry_val.set('')
        self.update_tracer_id = self.entry_val.trace('w', self.revalidate_state)

        # Main text widget is disabled to avoid tampering, need to enable it to modify its contents,
        # then disable it again.
        self.main_text_area.configure(state='normal')
        self.main_text_area.delete('1.0', END)
        self.main_text_area.insert(INSERT, ' '.join(words), CENTER_TAG)
        self.main_text_area.configure(state='disabled')

        self.words = words
        self.user_typed_words = []
        self.update_current_word_highlighting()
        self.entry.focus_set()
