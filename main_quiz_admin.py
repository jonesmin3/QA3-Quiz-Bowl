import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import os
import random

DATABASE_FILE = 'quiz_bowl_app.db'
PASSWORD = "momothecat" # Password for admin panel access
PASS_THRESHOLD = 80.0 # Percentage needed to pass a quiz

# --- Database Utility Functions ---
def connect_db(db_file=DATABASE_FILE):
    """Establishes connection to the specified SQLite database file."""
    if not os.path.exists(db_file):
        messagebox.showerror("Database Error", f"Database file '{db_file}' not found.")
        return None
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row # Access columns by name
        conn.execute("PRAGMA foreign_keys = ON;")
        print("Database connected successfully.")
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Database connection error: {e}")
        return None

def fetch_topics(conn):
    """Fetches all topic IDs and names from the Topics table."""
    if not conn: return []
    topics_list = []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Topics ORDER BY name")
        topics_list = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching topics: {e}")
        # Consider showing warning if critical
    return topics_list

def fetch_questions_for_topic(conn, topic_id):
    """Fetches all questions for a specific topic ID."""
    # Returns list of sqlite3.Row objects in this version
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, topic_id, question_text, option_a, option_b, option_c, option_d, option_e, correct_answer
            FROM Questions WHERE topic_id = ? ORDER BY id
        """, (topic_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error fetching questions for topic {topic_id}: {e}")
        messagebox.showwarning("Database Error", f"Could not load questions for the selected topic.\nError: {e}", parent=None)
        return []

# --- Start Screen Class ---
class StartScreen(ttk.Frame):
    """Initial screen with buttons to Take Quiz or Access Admin Panel."""
    def __init__(self, parent, show_admin_callback, launch_quiz_callback, **kwargs):
        super().__init__(parent, padding="20", **kwargs)
        self.parent = parent
        self.show_admin_callback = show_admin_callback
        self.launch_quiz_callback = launch_quiz_callback
        self._setup_widgets()

    def _setup_widgets(self):
        self.grid_rowconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1); self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        ttk.Label(self, text="Quiz Bowl Application", font=('Helvetica', 20, 'bold')).grid(row=0, column=0, pady=(20, 40))
        s = ttk.Style(); s.configure('Start.TButton', font=('Helvetica', 14), padding=10)
        admin_button = ttk.Button(self, text="Access Admin Panel", command=self.show_admin_callback, style='Start.TButton', width=20)
        admin_button.grid(row=1, column=0, pady=10)
        quiz_button = ttk.Button(self, text="Take Quiz", command=self.launch_quiz_callback, style='Start.TButton', width=20)
        quiz_button.grid(row=2, column=0, pady=10)

# --- Admin Panel Class ---
class AdminPanel(ttk.Frame):
    """Admin panel UI for managing questions."""
    def __init__(self, parent, db_connection, back_callback, style, **kwargs):
        super().__init__(parent, padding="10", **kwargs)
        self.parent = parent; self.conn = db_connection; self.back_callback = back_callback
        self.style = style; self.topics = []; self.questions_data = {}; self.current_topic_id = None
        self.grid_columnconfigure(1, weight=1); self._setup_widgets(); self._load_initial_data()

    def _setup_widgets(self):
        """Creates and places all widgets for the admin panel."""
        back_button=ttk.Button(self, text="< Back to Start", command=self.back_callback); back_button.grid(row=0, column=0, pady=(0,15), padx=5, sticky="w")
        ttk.Label(self, text="Admin Panel", font=('Helvetica', 16, 'bold')).grid(row=1, column=0, columnspan=2, pady=(0, 15), sticky="ew")
        ttk.Label(self, text="Manage Topic:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.topic_combobox = ttk.Combobox(self, state="readonly", width=35); self.topic_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew"); self.topic_combobox.bind("<<ComboboxSelected>>", self._load_questions_ui)
        q_list_frame = ttk.LabelFrame(self, text="Questions in Selected Topic"); q_list_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky="nsew"); q_list_frame.grid_rowconfigure(0, weight=1); q_list_frame.grid_columnconfigure(0, weight=1)
        self.question_listbox = tk.Listbox(q_list_frame, height=10, exportselection=False); self.question_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5); self.question_listbox.bind("<<ListboxSelect>>", self._display_selected_question_ui)
        list_scrollbar = ttk.Scrollbar(q_list_frame, orient=tk.VERTICAL, command=self.question_listbox.yview); list_scrollbar.grid(row=0, column=1, sticky="ns"); self.question_listbox.config(yscrollcommand=list_scrollbar.set)
        edit_frame = ttk.LabelFrame(self, text="Edit Selected Question"); edit_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew"); edit_frame.grid_columnconfigure(1, weight=1)
        self.qid_var = tk.StringVar(); self.opt_a_var = tk.StringVar(); self.opt_b_var = tk.StringVar(); self.opt_c_var = tk.StringVar(); self.opt_d_var = tk.StringVar(); self.opt_e_var = tk.StringVar(); self.correct_var = tk.StringVar()
        ttk.Label(edit_frame, text="ID:").grid(row=0, column=0, sticky="w", padx=5, pady=2); self.qid_entry = ttk.Entry(edit_frame, textvariable=self.qid_var, state="readonly"); self.qid_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(edit_frame, text="Question:").grid(row=1, column=0, sticky="nw", padx=5, pady=2); self.qtext_widget = tk.Text(edit_frame, height=4, width=40, wrap=tk.WORD); self.qtext_widget.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(edit_frame, text="Option A:").grid(row=2, column=0, sticky="w", padx=5, pady=2); self.opt_a_entry = ttk.Entry(edit_frame, textvariable=self.opt_a_var); self.opt_a_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(edit_frame, text="Option B:").grid(row=3, column=0, sticky="w", padx=5, pady=2); self.opt_b_entry = ttk.Entry(edit_frame, textvariable=self.opt_b_var); self.opt_b_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(edit_frame, text="Option C:").grid(row=4, column=0, sticky="w", padx=5, pady=2); self.opt_c_entry = ttk.Entry(edit_frame, textvariable=self.opt_c_var); self.opt_c_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(edit_frame, text="Option D:").grid(row=5, column=0, sticky="w", padx=5, pady=2); self.opt_d_entry = ttk.Entry(edit_frame, textvariable=self.opt_d_var); self.opt_d_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(edit_frame, text="Option E:").grid(row=6, column=0, sticky="w", padx=5, pady=2); self.opt_e_entry = ttk.Entry(edit_frame, textvariable=self.opt_e_var); self.opt_e_entry.grid(row=6, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(edit_frame, text="Correct (A-E):").grid(row=7, column=0, sticky="w", padx=5, pady=2); self.correct_combobox = ttk.Combobox(edit_frame, textvariable=self.correct_var, values=['A', 'B', 'C', 'D', 'E'], state="readonly", width=5); self.correct_combobox.grid(row=7, column=1, sticky="w", padx=5, pady=2)
        action_frame = ttk.Frame(self); action_frame.grid(row=5, column=0, columnspan=2, pady=10)
        self.new_button = ttk.Button(action_frame, text="New Question", command=self._prepare_new_question_ui); self.new_button.grid(row=0, column=0, padx=5)
        self.save_button = ttk.Button(action_frame, text="Save Changes", command=self._save_question, state=tk.DISABLED); self.save_button.grid(row=0, column=1, padx=5)
        self.delete_button = ttk.Button(action_frame, text="Delete Question", command=self._delete_question, state=tk.DISABLED); self.delete_button.grid(row=0, column=2, padx=5)

    def _load_initial_data(self):
        """Loads initial topic data."""
        self.topics = fetch_topics(self.conn)
        self.topic_combobox['values'] = [t['name'] for t in self.topics]
        if self.topics:
            self.topic_combobox.current(0)
            self._load_questions_ui() # Load questions for the default topic

    def _load_questions_ui(self, event=None):
        """Loads question listbox based on selected topic."""
        selected_topic_index = self.topic_combobox.current()
        questions_display_data = [] # Default to empty list
        if selected_topic_index != -1:
            selected_topic = self.topics[selected_topic_index]
            self.current_topic_id = selected_topic['id']
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT id, question_text FROM Questions WHERE topic_id = ? ORDER BY id", (self.current_topic_id,))
                questions_display_data = cursor.fetchall()
            except sqlite3.Error as e:
                 messagebox.showerror("Database Error", f"Failed to load questions list:\n{e}", parent=self)
        else:
            self.current_topic_id = None # No topic selected

        self.question_listbox.delete(0, tk.END) # Clear current list
        self.questions_data.clear() # Clear mapping
        self._clear_edit_form()
        self._disable_action_buttons()

        # Populate listbox and internal mapping {listbox_index: question_id}
        for i, q_row in enumerate(questions_display_data):
            q_id = q_row['id']; q_text = q_row['question_text']
            display_text = f"{q_id}: {q_text[:60]}{'...' if len(q_text) > 60 else ''}"
            self.question_listbox.insert(tk.END, display_text)
            self.questions_data[i] = q_id

    def _display_selected_question_ui(self, event=None):
        """Displays selected question details in the edit form."""
        selected_indices = self.question_listbox.curselection()
        if not selected_indices:
            self._clear_edit_form(); self._disable_action_buttons(); return

        selected_list_index = selected_indices[0]
        question_id = self.questions_data.get(selected_list_index)

        if question_id:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM Questions WHERE id=?", (question_id,))
                q_row = cursor.fetchone()
                if q_row:
                    # Populate form fields
                    self.qid_var.set(q_row['id'])
                    self.qtext_widget.delete('1.0', tk.END); self.qtext_widget.insert('1.0', q_row['question_text'] or "")
                    self.opt_a_var.set(q_row['option_a'] or ""); self.opt_b_var.set(q_row['option_b'] or "")
                    self.opt_c_var.set(q_row['option_c'] or ""); self.opt_d_var.set(q_row['option_d'] or "")
                    self.opt_e_var.set(q_row['option_e'] or ""); self.correct_var.set(q_row['correct_answer'].upper() if q_row['correct_answer'] else "")
                    self._enable_action_buttons(); self.save_button.config(text="Save Changes")
                else:
                     messagebox.showerror("Error", f"Could not find details for question ID {question_id}.", parent=self)
                     self._clear_edit_form(); self._disable_action_buttons()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to load question details:\n{e}", parent=self)
                self._clear_edit_form(); self._disable_action_buttons()

    def _clear_edit_form(self):
        """Clears all edit form fields."""
        self.qid_var.set(""); self.qtext_widget.delete('1.0', tk.END)
        self.opt_a_var.set(""); self.opt_b_var.set(""); self.opt_c_var.set("")
        self.opt_d_var.set(""); self.opt_e_var.set(""); self.correct_var.set("")
        try: self.question_listbox.selection_clear(0, tk.END) # Deselect listbox
        except tk.TclError: pass

    def _disable_action_buttons(self):
        """Disables Save and Delete."""
        self.save_button.config(state=tk.DISABLED); self.delete_button.config(state=tk.DISABLED)

    def _enable_action_buttons(self):
        """Enables Save and Delete."""
        self.save_button.config(state=tk.NORMAL); self.delete_button.config(state=tk.NORMAL)

    def _prepare_new_question_ui(self):
        """Prepares form for adding a new question."""
        if self.current_topic_id is None: messagebox.showwarning("No Topic Selected", "Please select a topic before adding.", parent=self); return
        self._clear_edit_form(); self._disable_action_buttons()
        self.save_button.config(state=tk.NORMAL, text="Save New Question"); self.qtext_widget.focus_set()

    def _validate_form_input(self):
        """Validates form input before saving."""
        q_text = self.qtext_widget.get("1.0", tk.END).strip()
        opts = {
            'a': self.opt_a_var.get().strip(), 'b': self.opt_b_var.get().strip(),
            'c': self.opt_c_var.get().strip(), 'd': self.opt_d_var.get().strip(),
            'e': self.opt_e_var.get().strip()
        }
        correct = self.correct_var.get().upper()
        if not q_text or not all(opts.values()): messagebox.showerror("Input Error", "Question and all Options must be filled.", parent=self); return None
        if not correct: messagebox.showerror("Input Error", "Correct Answer must be selected.", parent=self); return None
        if correct not in ['A', 'B', 'C', 'D', 'E']: messagebox.showerror("Input Error", "Correct Answer must be A-E.", parent=self); return None
        return {"question_text": q_text, **{f"option_{k}": v for k, v in opts.items()}, "correct_answer": correct}

    def _save_question(self):
        """Handles saving new or existing question to the database."""
        qid_str = self.qid_var.get(); is_new = not bool(qid_str)
        if self.current_topic_id is None and is_new: messagebox.showerror("Error", "No topic selected for new question.", parent=self); return
        form_data = self._validate_form_input()
        if form_data is None: return
        cursor = self.conn.cursor()
        try:
            if is_new:
                sql = """INSERT INTO Questions (topic_id, question_text, option_a, option_b, option_c, option_d, option_e, correct_answer) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
                params = (self.current_topic_id, form_data["question_text"], form_data["option_a"], form_data["option_b"], form_data["option_c"], form_data["option_d"], form_data["option_e"], form_data["correct_answer"])
                cursor.execute(sql, params); self.conn.commit(); messagebox.showinfo("Success", "New question added.", parent=self)
            else:
                qid = int(qid_str)
                sql = """UPDATE Questions SET question_text=?, option_a=?, option_b=?, option_c=?, option_d=?, option_e=?, correct_answer=? WHERE id=?"""
                params = (form_data["question_text"], form_data["option_a"], form_data["option_b"], form_data["option_c"], form_data["option_d"], form_data["option_e"], form_data["correct_answer"], qid)
                cursor.execute(sql, params); self.conn.commit()
                if cursor.rowcount == 0: messagebox.showwarning("Warning", f"No update ID {qid}.", parent=self)
                else: messagebox.showinfo("Success", f"Question ID {qid} updated.", parent=self)
            self._load_questions_ui(); self._clear_edit_form(); self._disable_action_buttons()
        except sqlite3.Error as e: self.conn.rollback(); messagebox.showerror("Database Error", f"Failed save:\n{e}", parent=self)
        except ValueError: messagebox.showerror("Error", "Invalid ID.", parent=self)

    def _delete_question(self):
        """Handles deleting the selected question."""
        qid_str = self.qid_var.get()
        if not qid_str: messagebox.showerror("Error", "No question selected.", parent=self); return
        try: qid = int(qid_str)
        except ValueError: messagebox.showerror("Error", "Invalid ID.", parent=self); return
        if messagebox.askyesno("Confirm Delete", f"Delete question ID {qid}?", parent=self):
            try:
                cursor = self.conn.cursor(); cursor.execute("DELETE FROM Questions WHERE id=?", (qid,)); self.conn.commit()
                if cursor.rowcount > 0: messagebox.showinfo("Success", f"Question ID {qid} deleted.", parent=self); self._load_questions_ui(); self._clear_edit_form(); self._disable_action_buttons()
                else: messagebox.showwarning("Warning", f"Could not find ID {qid}.", parent=self)
            except sqlite3.Error as e: self.conn.rollback(); messagebox.showerror("Database Error", f"Failed delete:\n{e}", parent=self)

# --- Quiz App Class ---
class QuizApp:
    """Handles the quiz-taking UI and logic, supporting multiple display modes."""
    def __init__(self, parent_window, db_connection):
        self.quiz_window = parent_window; self.conn = db_connection
        self.quiz_window.title("Quiz Bowl"); self.quiz_window.geometry("700x600")
        self.style = ttk.Style(self.quiz_window); self.style.theme_use('clam')
        self.topics = []; self.questions = []; self.current_question_index = 0; self.score = 0
        self.selected_answer = tk.StringVar() # For one_by_one mode
        self.current_topic_name = ""; self.display_mode = tk.StringVar(value="one_by_one"); self.current_mode = "one_by_one"
        self.all_answers_vars = {} # {q_index: StringVar} for all_at_once mode
        self.topic_frame = ttk.Frame(self.quiz_window, padding="10")
        self.quiz_frame = ttk.Frame(self.quiz_window, padding="10") # For active quiz UI
        self.topics = fetch_topics(self.conn)
        if not self.topics: messagebox.showerror("Init Error", "No topics found!", parent=self.quiz_window); self.quiz_window.destroy(); return
        self._setup_topic_selection_ui()
        self.quiz_window.protocol("WM_DELETE_WINDOW", self._on_quiz_closing)

    def _setup_topic_selection_ui(self):
        """Sets up topic selection and display mode choice."""
        self.quiz_frame.pack_forget(); self.topic_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(self.topic_frame, text="Select a Quiz Topic:", font=('Helvetica', 14, 'bold')).pack(pady=(10, 5))
        self.topic_listbox = tk.Listbox(self.topic_frame, height=8, font=('Helvetica', 12), exportselection=False)
        for topic in self.topics: self.topic_listbox.insert(tk.END, topic['name'])
        self.topic_listbox.pack(pady=5, padx=20, fill=tk.X)
        if self.topics: self.topic_listbox.select_set(0); self.topic_listbox.activate(0)
        mode_frame = ttk.LabelFrame(self.topic_frame, text="Quiz Display Mode", padding="10")
        mode_frame.pack(pady=(10, 10), padx=20, fill=tk.X)
        rb_one = ttk.Radiobutton(mode_frame, text="One Question at a Time", variable=self.display_mode, value="one_by_one"); rb_one.pack(anchor='w', pady=2)
        rb_all = ttk.Radiobutton(mode_frame, text="All Questions at Once", variable=self.display_mode, value="all_at_once"); rb_all.pack(anchor='w', pady=2)
        start_button = ttk.Button(self.topic_frame, text="Start Quiz", command=self._start_quiz); start_button.pack(pady=(10, 20))
        self.topic_listbox.focus_set()

    def _start_quiz(self):
        """Starts quiz based on selections."""
        selected_indices = self.topic_listbox.curselection()
        if not selected_indices: messagebox.showwarning("No Selection", "Please select a topic.", parent=self.quiz_window); return
        selected_index = selected_indices[0]; selected_topic_row = self.topics[selected_index]
        selected_topic_id = selected_topic_row['id']; self.current_topic_name = selected_topic_row['name']
        self.current_mode = self.display_mode.get()
        self.questions = fetch_questions_for_topic(self.conn, selected_topic_id) # Fetches list of Rows
        if not self.questions: return # Stop if fetch failed or no questions
        self.current_question_index = 0; self.score = 0; self.all_answers_vars.clear()
        self.topic_frame.pack_forget()
        if self.current_mode == "one_by_one": self._setup_quiz_ui_one_by_one(); self._load_question_one_by_one()
        else: self._setup_quiz_ui_all_at_once()

    # --- Methods for "One by One" Mode ---
    def _setup_quiz_ui_one_by_one(self):
        """Sets up UI for one question at a time."""
        for widget in self.quiz_frame.winfo_children(): widget.destroy()
        self.quiz_frame.pack(fill=tk.BOTH, expand=True)
        self.topic_label = ttk.Label(self.quiz_frame, text=f"Topic: {self.current_topic_name}", font=('Helvetica', 14, 'bold')); self.topic_label.pack(pady=(5, 5))
        self.q_num_label = ttk.Label(self.quiz_frame, text="", font=('Helvetica', 10)); self.q_num_label.pack(pady=(0, 5))
        total_questions = len(self.questions); self.running_score_label = ttk.Label(self.quiz_frame, text=f"Score: {self.score} / {total_questions}", font=('Helvetica', 10, 'bold')); self.running_score_label.pack(pady=(0, 10))
        self.question_label = tk.Message(self.quiz_frame, text="Loading...", font=('Helvetica', 12), width=650, justify=tk.LEFT); self.question_label.pack(pady=(5, 15), padx=10, fill=tk.X)
        self.options_frame = ttk.Frame(self.quiz_frame); self.options_frame.pack(pady=5, padx=20, anchor='w')
        self.radio_buttons = {}
        for letter in ['A', 'B', 'C', 'D', 'E']: rb = ttk.Radiobutton(self.options_frame, text=f"{letter}.", variable=self.selected_answer, value=letter, command=self._enable_check_button); rb.pack(anchor='w', pady=2); self.radio_buttons[letter] = rb
        self.feedback_label = ttk.Label(self.quiz_frame, text="", font=('Helvetica', 11, 'italic')); self.feedback_label.pack(pady=(10, 5))
        self.button_frame = ttk.Frame(self.quiz_frame); self.button_frame.pack(pady=(10, 15))
        self.check_button = ttk.Button(self.button_frame, text="Check Answer", command=self._check_answer_one_by_one, state=tk.DISABLED); self.check_button.grid(row=0, column=0, padx=5)
        self.next_button = ttk.Button(self.button_frame, text="Next Question", command=self._next_question_one_by_one, state=tk.DISABLED); self.next_button.grid(row=0, column=1, padx=5)

    def _load_question_one_by_one(self):
        """Loads current question for one-by-one mode."""
        if 0 <= self.current_question_index < len(self.questions):
            q_data = self.questions[self.current_question_index]
            self.q_num_label.config(text=f"Question {self.current_question_index + 1} of {len(self.questions)}")
            self.question_label.config(text=q_data['question_text'])
            for letter, rb_widget in self.radio_buttons.items(): rb_widget.config(text=f"{letter}. {q_data[f'option_{letter.lower()}']}", state=tk.NORMAL)
            self.selected_answer.set(""); self.feedback_label.config(text="")
            self.check_button.config(state=tk.DISABLED); self.next_button.config(state=tk.DISABLED)
            if self.current_question_index == len(self.questions) - 1: self.next_button.config(text="Show Results")
            else: self.next_button.config(text="Next Question")
        else: self._show_results()

    def _enable_check_button(self):
        """Enables check button using instate()."""
        if not hasattr(self, 'check_button') or not self.check_button.winfo_exists(): return
        if not hasattr(self, 'next_button') or not self.next_button.winfo_exists(): return
        if self.next_button.instate(['disabled']): self.check_button.config(state=tk.NORMAL)

    # *** METHOD WITH CORRECTED SAFEGUARD ***
    def _check_answer_one_by_one(self):
        """Checks the answer for the current question in one-by-one mode."""
        # Check individual widgets first
        required_widgets = ['check_button', 'next_button', 'running_score_label']
        for attr_name in required_widgets:
            if not hasattr(self, attr_name) or not getattr(self, attr_name).winfo_exists():
                print(f"Error: Widget '{attr_name}' missing in check_answer_one_by_one.")
                return # Exit if essential widget is missing

        # Separately check if the radio_buttons dictionary exists and is populated
        if not hasattr(self, 'radio_buttons') or not self.radio_buttons:
            print("Error: radio_buttons dictionary missing or empty in check_answer_one_by_one.")
            return # Exit if radio buttons weren't set up

        user_answer = self.selected_answer.get()
        if not user_answer:
            messagebox.showwarning("No Answer", "Please select an answer.", parent=self.quiz_window)
            return

        try:
            # Check index validity
            if not (0 <= self.current_question_index < len(self.questions)):
                print(f"Error: Invalid question index {self.current_question_index}")
                return # Avoid IndexError

            q_data = self.questions[self.current_question_index] # Get the sqlite3.Row
            correct_answer = q_data['correct_answer'].upper() # Use upper for comparison

            # Disable radio buttons and check button
            for rb in self.radio_buttons.values(): # Iterate through widgets in the dict
                 if rb.winfo_exists():
                    rb.config(state=tk.DISABLED)
            self.check_button.config(state=tk.DISABLED)

            # Check correctness and provide feedback
            if user_answer == correct_answer:
                self.score += 1
                self.feedback_label.config(text="Correct!", foreground='green')
            else:
                correct_option_key = f"option_{correct_answer.lower()}"
                # Check if the key exists before accessing, in case correct_answer is invalid
                correct_text = q_data[correct_option_key] if correct_answer in ['A','B','C','D','E'] else "N/A"
                self.feedback_label.config(text=f"Incorrect. Correct: {correct_answer}. {correct_text}", foreground='red')

            # Update the running score display
            total_questions = len(self.questions)
            self.running_score_label.config(text=f"Score: {self.score} / {total_questions}")

            # Enable the Next button
            self.next_button.config(state=tk.NORMAL)

        except Exception as e:
            # Catch potential errors during answer checking (e.g., KeyError if DB columns missing)
            print(f"ERROR inside check_answer_one_by_one logic: {type(e).__name__} - {e}")
            self.feedback_label.config(text="Error checking answer!", foreground='red')

    def _next_question_one_by_one(self):
        """Loads next question."""
        if not self.next_button.winfo_exists(): return
        self.current_question_index += 1; self._load_question_one_by_one()

    # --- Methods for "All At Once" Mode ---
    # *** METHOD WITH CORRECTED SCROLLABLE FRAME WIDTH HANDLING ***
    def _setup_quiz_ui_all_at_once(self):
        """Sets up the UI for all-questions-at-once mode using a scrollable frame."""
        for widget in self.quiz_frame.winfo_children(): widget.destroy()
        self.quiz_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.quiz_frame, text=f"Topic: {self.current_topic_name}", font=('Helvetica', 14, 'bold')).pack(pady=(5, 10))

        # Create Scrollable Area
        container = ttk.Frame(self.quiz_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(container)
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Frame inside the canvas to hold the actual content
        self.scrollable_frame = ttk.Frame(canvas)
        # Add frame to canvas using create_window and store the item ID
        self.scrollable_frame_window_id = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Populate Scrollable Frame
        self.all_answers_vars.clear() # Ensure it's empty before populating
        for index, q_data in enumerate(self.questions):
            q_frame = ttk.LabelFrame(self.scrollable_frame, text=f" Question {index + 1} ", padding="10")
            # Make the question frame expand horizontally within the scrollable frame
            q_frame.pack(pady=10, padx=10, fill=tk.X, expand=True) # Added expand=True

            q_label = tk.Message(q_frame, text=q_data['question_text'], font=('Helvetica', 11), width=600, justify=tk.LEFT)
            q_label.pack(anchor='w', pady=(0, 5))

            answer_var = tk.StringVar() # Unique variable for this question's answer
            self.all_answers_vars[index] = answer_var # Store it, keyed by question index
            options_letters = ['A', 'B', 'C', 'D', 'E']
            for letter in options_letters:
                option_key = f"option_{letter.lower()}"
                option_text = q_data[option_key]
                rb = ttk.Radiobutton(q_frame, text=f"{letter}. {option_text}", variable=answer_var, value=letter)
                rb.pack(anchor='w') # Pack options to the left

        # Update scroll region AND frame width when canvas is configured
        def on_canvas_configure(event):
            # Update scroll region to encompass the entire scrollable_frame
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update the width of the frame window on the canvas to match the canvas's width
            canvas.itemconfig(self.scrollable_frame_window_id, width=event.width)

        # Bind the configure event on the CANVAS to the function
        canvas.bind('<Configure>', on_canvas_configure)

        # Submit Button (Outside Scrollable Area)
        submit_button = ttk.Button(self.quiz_frame, text="Submit Quiz", command=self._check_all_answers)
        submit_button.pack(pady=15) # Place below the scrollable container


    def _check_all_answers(self):
        """Checks all answers for all-at-once mode."""
        self.score = 0; all_answered = True
        for index, q_data in enumerate(self.questions):
            user_answer = self.all_answers_vars.get(index, tk.StringVar()).get()
            if not user_answer: all_answered = False; continue # Score unanswered as incorrect
            correct_answer = q_data['correct_answer'].upper()
            if user_answer == correct_answer: self.score += 1
        if not all_answered: messagebox.showwarning("Incomplete", "Unanswered questions count as incorrect.", parent=self.quiz_window)
        self._show_results() # Show results after checking all

    # --- Common Methods ---
    def _show_results(self):
        """Displays final results (used by both modes)."""
        for widget in self.quiz_frame.winfo_children(): widget.destroy()
        self.quiz_frame.pack(fill=tk.BOTH, expand=True) # Ensure frame is visible
        ttk.Label(self.quiz_frame, text="Quiz Finished!", font=('Helvetica', 16, 'bold')).pack(pady=10)
        total_questions = len(self.questions); result_text = ""; status_text = ""; status_color = "black"
        if total_questions > 0:
            percentage = (self.score / total_questions) * 100
            if percentage >= PASS_THRESHOLD: status = "Pass"; status_color = "green"
            else: status = "Fail"; status_color = "red"
            result_text = f"Your final score: {self.score} out of {total_questions} ({percentage:.1f}%)"; status_text = f"Result: {status}"
        else: result_text = "No questions were asked."
        ttk.Label(self.quiz_frame, text=result_text, font=('Helvetica', 14)).pack(pady=5)
        if status_text: ttk.Label(self.quiz_frame, text=status_text, font=('Helvetica', 14, 'bold'), foreground=status_color).pack(pady=5)
        close_button = ttk.Button(self.quiz_frame, text="Close Quiz", command=self._on_quiz_closing); close_button.pack(pady=20)

    def _on_quiz_closing(self):
        """Handles quiz window closing."""
        if self.quiz_window.grab_status() != "none": self.quiz_window.grab_release()
        self.quiz_window.destroy()

# --- Main Application Class ---
class MainApp:
    """Main application controller."""
    def __init__(self, root):
        self.root = root; self.root.title("Quiz Bowl Application"); self.root.geometry("700x650")
        self.db_connection = connect_db()
        if not self.db_connection: self.root.destroy(); return
        self.style = ttk.Style(self.root); self.style.theme_use('clam')
        self.start_screen = None; self.admin_panel = None
        self._create_start_screen()
        self.root.protocol("WM_DELETE_WINDOW", self._on_app_closing)

    def _create_start_screen(self):
        if self.admin_panel: self.admin_panel.pack_forget()
        self.start_screen = StartScreen(self.root, show_admin_callback=self.show_admin_panel, launch_quiz_callback=self.launch_quiz)
        self.start_screen.pack(fill=tk.BOTH, expand=True)

    def show_admin_panel(self):
        password = simpledialog.askstring("Password Required", "Enter Admin Password:", parent=self.root, show='*')
        if password == PASSWORD:
            if self.start_screen: self.start_screen.pack_forget()
            if not self.admin_panel: self.admin_panel = AdminPanel(self.root, self.db_connection, back_callback=self.show_start_screen, style=self.style)
            self.admin_panel.pack(fill=tk.BOTH, expand=True)
        elif password is not None: messagebox.showerror("Access Denied", "Incorrect password.", parent=self.root)

    def show_start_screen(self):
         if self.admin_panel: self.admin_panel.pack_forget()
         if self.start_screen: self.start_screen.pack(fill=tk.BOTH, expand=True)
         else: self._create_start_screen()

    def launch_quiz(self):
        """Launches the quiz window."""
        quiz_window_exists = False
        for win in self.root.winfo_children():
             if isinstance(win, tk.Toplevel) and win.title() == "Quiz Bowl":
                 quiz_window_exists = True; print("Quiz window already open."); win.lift()
                 try:
                     win.focus_force()
                     # Corrected indentation for this block:
                     if win.grab_status() == "none": win.grab_set()
                 except tk.TclError as e: print(f"Could not focus/grab existing quiz window: {e}")
                 break # Stop checking
        if not quiz_window_exists:
             quiz_toplevel_window = tk.Toplevel(self.root)
             quiz_toplevel_window.grab_set() # Make modal
             quiz_app_instance = QuizApp(quiz_toplevel_window, self.db_connection) # Instantiates the updated QuizApp

    def _on_app_closing(self):
        """Handles application close."""
        if self.db_connection:
             try: self.db_connection.close(); print("Main database connection closed.")
             except sqlite3.Error as e: print(f"Error closing database connection: {e}")
        self.root.destroy()

# --- Main Execution Block ---
if __name__ == "__main__":
    main_window = tk.Tk()
    app = MainApp(main_window)
    main_window.mainloop()