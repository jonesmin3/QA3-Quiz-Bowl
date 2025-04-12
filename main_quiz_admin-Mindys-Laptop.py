import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
import sqlite3
import os
import random

DATABASE_FILE = 'quiz_bowl_app.db'

# --- Database Utility Functions ---
def connect_db():
    """Establishes connection to the SQLite database."""
    if not os.path.exists(DATABASE_FILE):
        messagebox.showerror("Database Error", f"Database file '{DATABASE_FILE}' not found.")
        return None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        print("Database connected successfully.")
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Database connection error: {e}")
        return None

def fetch_topics(conn):
    """Fetches all topic IDs and names."""
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Topics ORDER BY name")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching topics: {e}")
        return []

def fetch_questions_for_topic(conn, topic_id):
    """Fetches all questions for a specific topic ID."""
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, question_text, option_a, option_b, option_c, option_d, option_e, correct_answer
            FROM Questions
            WHERE topic_id = ? ORDER BY id
        """, (topic_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching questions for topic {topic_id}: {e}")
        return []

# --- Start Screen Class ---
class StartScreen(ttk.Frame):
    def __init__(self, parent, show_admin_callback, launch_quiz_callback, **kwargs):
        super().__init__(parent, padding="20", **kwargs)
        self.parent = parent
        self.show_admin_callback = show_admin_callback
        self.launch_quiz_callback = launch_quiz_callback

        self._setup_widgets()

    def _setup_widgets(self):
        # Configure grid to center buttons
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1) # Spacer row
        self.grid_rowconfigure(3, weight=1) # Spacer row
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="Quiz Bowl Application", font=('Helvetica', 20, 'bold')).grid(row=0, column=0, pady=(20, 40))

        # Style for buttons
        s = ttk.Style()
        s.configure('Start.TButton', font=('Helvetica', 14), padding=10)

        admin_button = ttk.Button(self, text="Access Admin Panel",
                                  command=self.show_admin_callback,
                                  style='Start.TButton', width=20)
        admin_button.grid(row=1, column=0, pady=10)

        quiz_button = ttk.Button(self, text="Take Quiz",
                                 command=self.launch_quiz_callback,
                                 style='Start.TButton', width=20)
        quiz_button.grid(row=2, column=0, pady=10)


# --- Admin Panel Class (Modified: Removed Quiz Button) ---
class AdminPanel(ttk.Frame):
    # Removed launch_quiz_callback and associated style parameter/usage for quiz button
    def __init__(self, parent, db_connection, back_callback, style, **kwargs):
        super().__init__(parent, padding="10", **kwargs)
        self.parent = parent
        self.conn = db_connection
        self.back_callback = back_callback # Callback to go back to start screen
        self.style = style

        self.topics = []
        self.questions_data = {}
        self.current_topic_id = None

        self.grid_columnconfigure(1, weight=1)

        self._setup_widgets()
        self._load_initial_data()

    def _setup_widgets(self):
        # --- Back Button ---
        back_button = ttk.Button(self, text="< Back to Start", command=self.back_callback)
        back_button.grid(row=0, column=0, pady=(0,15), padx=5, sticky="w")

        # --- Title ---
        ttk.Label(self, text="Admin Panel", font=('Helvetica', 16, 'bold')).grid(row=1, column=0, columnspan=3, pady=(0, 15), sticky="ew")

        # --- Topic Selection ---
        ttk.Label(self, text="Manage Topic:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.topic_combobox = ttk.Combobox(self, state="readonly", width=35)
        self.topic_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.topic_combobox.bind("<<ComboboxSelected>>", self.load_questions_for_selected_topic)

        # --- Question List ---
        q_list_frame = ttk.LabelFrame(self, text="Questions in Selected Topic")
        q_list_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")
        q_list_frame.grid_rowconfigure(0, weight=1)
        q_list_frame.grid_columnconfigure(0, weight=1)

        self.question_listbox = tk.Listbox(q_list_frame, height=10, exportselection=False)
        self.question_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.question_listbox.bind("<<ListboxSelect>>", self.display_selected_question)

        list_scrollbar = ttk.Scrollbar(q_list_frame, orient=tk.VERTICAL, command=self.question_listbox.yview)
        list_scrollbar.grid(row=0, column=1, sticky="ns")
        self.question_listbox.config(yscrollcommand=list_scrollbar.set)

        # --- Editing Area ---
        edit_frame = ttk.LabelFrame(self, text="Edit Selected Question")
        edit_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        for i in range(2): edit_frame.grid_columnconfigure(i, weight=1 if i==1 else 0) # Make entry fields expand

        ttk.Label(edit_frame, text="ID:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.qid_var = tk.StringVar()
        self.qid_entry = ttk.Entry(edit_frame, textvariable=self.qid_var, state="readonly")
        self.qid_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(edit_frame, text="Question:").grid(row=1, column=0, sticky="nw", padx=5, pady=2)
        self.qtext_widget = tk.Text(edit_frame, height=4, width=40, wrap=tk.WORD)
        self.qtext_widget.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(edit_frame, text="Option A:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.opt_a_var = tk.StringVar()
        self.opt_a_entry = ttk.Entry(edit_frame, textvariable=self.opt_a_var)
        self.opt_a_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(edit_frame, text="Option B:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.opt_b_var = tk.StringVar()
        self.opt_b_entry = ttk.Entry(edit_frame, textvariable=self.opt_b_var)
        self.opt_b_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(edit_frame, text="Option C:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.opt_c_var = tk.StringVar()
        self.opt_c_entry = ttk.Entry(edit_frame, textvariable=self.opt_c_var)
        self.opt_c_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(edit_frame, text="Option D:").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        self.opt_d_var = tk.StringVar()
        self.opt_d_entry = ttk.Entry(edit_frame, textvariable=self.opt_d_var)
        self.opt_d_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(edit_frame, text="Option E:").grid(row=6, column=0, sticky="w", padx=5, pady=2)
        self.opt_e_var = tk.StringVar()
        self.opt_e_entry = ttk.Entry(edit_frame, textvariable=self.opt_e_var)
        self.opt_e_entry.grid(row=6, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(edit_frame, text="Correct (A-E):").grid(row=7, column=0, sticky="w", padx=5, pady=2)
        self.correct_var = tk.StringVar()
        self.correct_combobox = ttk.Combobox(edit_frame, textvariable=self.correct_var, values=['A', 'B', 'C', 'D', 'E'], state="readonly", width=5)
        self.correct_combobox.grid(row=7, column=1, sticky="w", padx=5, pady=2)

        # --- Action Buttons ---
        action_frame = ttk.Frame(self)
        action_frame.grid(row=5, column=0, columnspan=2, pady=10) # Adjusted row index

        self.new_button = ttk.Button(action_frame, text="New Question", command=self.prepare_new_question)
        self.new_button.grid(row=0, column=0, padx=5)

        self.save_button = ttk.Button(action_frame, text="Save Changes", command=self.save_question, state=tk.DISABLED)
        self.save_button.grid(row=0, column=1, padx=5)

        self.delete_button = ttk.Button(action_frame, text="Delete Question", command=self.delete_question, state=tk.DISABLED)
        self.delete_button.grid(row=0, column=2, padx=5)

    # --- Rest of AdminPanel methods ---
    def _load_initial_data(self):
        """Loads topics into the combobox."""
        self.topics = fetch_topics(self.conn)
        self.topic_combobox['values'] = [t['name'] for t in self.topics]
        if self.topics:
            self.topic_combobox.current(0)
            self.load_questions_for_selected_topic()

    def load_questions_for_selected_topic(self, event=None):
        """Loads questions into the listbox for the currently selected topic."""
        selected_topic_index = self.topic_combobox.current()
        if selected_topic_index == -1: return

        selected_topic = self.topics[selected_topic_index]
        self.current_topic_id = selected_topic['id']
        questions = fetch_questions_for_topic(self.conn, self.current_topic_id)
        self.question_listbox.delete(0, tk.END)
        self.questions_data.clear()
        self.clear_edit_form()
        self.disable_action_buttons()
        for i, q_row in enumerate(questions):
            display_text = f"{q_row['id']}: {q_row['question_text'][:50]}..." if len(q_row['question_text']) > 50 else f"{q_row['id']}: {q_row['question_text']}"
            self.question_listbox.insert(tk.END, display_text)
            self.questions_data[i] = q_row

    def display_selected_question(self, event=None):
        """Populates the editing form with data from the selected question."""
        selected_indices = self.question_listbox.curselection()
        if not selected_indices:
            self.clear_edit_form()
            self.disable_action_buttons()
            return
        selected_list_index = selected_indices[0]
        question_row = self.questions_data.get(selected_list_index)
        if question_row:
            self.qid_var.set(question_row['id'])
            self.qtext_widget.delete('1.0', tk.END)
            self.qtext_widget.insert('1.0', question_row['question_text'])
            self.opt_a_var.set(question_row['option_a'])
            self.opt_b_var.set(question_row['option_b'])
            self.opt_c_var.set(question_row['option_c'])
            self.opt_d_var.set(question_row['option_d'])
            self.opt_e_var.set(question_row['option_e'])
            self.correct_var.set(question_row['correct_answer'])
            self.enable_action_buttons()
            self.save_button.config(text="Save Changes")

    def clear_edit_form(self):
        """Clears all fields in the editing form."""
        self.qid_var.set("")
        self.qtext_widget.delete('1.0', tk.END)
        self.opt_a_var.set("")
        self.opt_b_var.set("")
        self.opt_c_var.set("")
        self.opt_d_var.set("")
        self.opt_e_var.set("")
        self.correct_var.set("")
        self.question_listbox.selection_clear(0, tk.END)

    def disable_action_buttons(self):
        self.save_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)

    def enable_action_buttons(self):
        self.save_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)

    def prepare_new_question(self):
        """Clears the form to prepare for adding a new question."""
        if self.current_topic_id is None:
            messagebox.showwarning("No Topic", "Please select a topic first.")
            return
        self.clear_edit_form()
        self.disable_action_buttons()
        self.save_button.config(state=tk.NORMAL, text="Save New Question")
        self.qtext_widget.focus_set()

    def save_question(self):
        """Saves changes to an existing question or saves a new question."""
        question_id = self.qid_var.get()
        is_new = not bool(question_id)
        if self.current_topic_id is None:
             messagebox.showerror("Error", "No topic selected.")
             return
        q_text = self.qtext_widget.get("1.0", tk.END).strip()
        opt_a = self.opt_a_var.get().strip()
        opt_b = self.opt_b_var.get().strip()
        opt_c = self.opt_c_var.get().strip()
        opt_d = self.opt_d_var.get().strip()
        opt_e = self.opt_e_var.get().strip()
        correct = self.correct_var.get()
        if not all([q_text, opt_a, opt_b, opt_c, opt_d, opt_e, correct]):
            messagebox.showerror("Input Error", "All fields must be filled.")
            return
        if correct not in ['A', 'B', 'C', 'D', 'E']:
            messagebox.showerror("Input Error", "Correct Answer must be A, B, C, D, or E.")
            return
        cursor = self.conn.cursor()
        try:
            if is_new:
                sql = """INSERT INTO Questions (topic_id, question_text, option_a, option_b, option_c, option_d, option_e, correct_answer) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
                cursor.execute(sql, (self.current_topic_id, q_text, opt_a, opt_b, opt_c, opt_d, opt_e, correct))
                self.conn.commit()
                messagebox.showinfo("Success", "New question added successfully.")
            else:
                sql = """UPDATE Questions SET question_text = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?, option_e = ?, correct_answer = ? WHERE id = ? AND topic_id = ?"""
                cursor.execute(sql, (q_text, opt_a, opt_b, opt_c, opt_d, opt_e, correct, question_id, self.current_topic_id))
                self.conn.commit()
                if cursor.rowcount == 0:
                     messagebox.showerror("Error", f"Failed to update question ID {question_id}. Not found or topic mismatch?")
                else:
                     messagebox.showinfo("Success", f"Question ID {question_id} updated successfully.")
            self.load_questions_for_selected_topic()
            self.clear_edit_form()
            self.disable_action_buttons()
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to save question: {e}")

    def delete_question(self):
        """Deletes the selected question after confirmation."""
        question_id = self.qid_var.get()
        if not question_id:
            messagebox.showerror("Error", "No question selected to delete.")
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete question ID {question_id}? This cannot be undone."):
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM Questions WHERE id = ?", (question_id,))
                self.conn.commit()
                if cursor.rowcount > 0:
                    messagebox.showinfo("Success", f"Question ID {question_id} deleted.")
                    self.load_questions_for_selected_topic()
                    self.clear_edit_form()
                    self.disable_action_buttons()
                else:
                    messagebox.showerror("Error", f"Could not find question ID {question_id} to delete.")
            except sqlite3.Error as e:
                 self.conn.rollback()
                 messagebox.showerror("Database Error", f"Failed to delete question: {e}")


# --- Quiz App Class (With Debug Prints Added) ---
class QuizApp:
    def __init__(self, parent_window, db_connection):
        self.quiz_window = parent_window
        self.conn = db_connection
        self.quiz_window.title("Quiz Bowl")
        self.quiz_window.geometry("600x500")

        self.style = ttk.Style(self.quiz_window)
        self.style.theme_use('clam')

        self.topics = []
        self.questions = []
        self.current_question_index = 0
        self.score = 0
        self.selected_answer = tk.StringVar()
        self.current_topic_name = ""

        self.topic_frame = ttk.Frame(self.quiz_window, padding="10")
        self.quiz_frame = ttk.Frame(self.quiz_window, padding="10")

        self.topics = fetch_topics(self.conn)
        if not self.topics:
             messagebox.showerror("Error", "No topics found in the database!", parent=self.quiz_window)
             self.quiz_window.destroy()
             return

        self.setup_topic_selection_ui()
        self.quiz_window.protocol("WM_DELETE_WINDOW", self.on_quiz_closing)

    def fetch_questions(self, topic_id):
        self.questions = fetch_questions_for_topic(self.conn, topic_id)
        if self.questions:
            random.shuffle(self.questions)
            print(f"Fetched {len(self.questions)} questions for topic ID {topic_id}.")
            return True
        else:
            print(f"No questions found for topic ID {topic_id}.")
            return False

    def setup_topic_selection_ui(self):
        self.quiz_frame.pack_forget()
        self.topic_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(self.topic_frame, text="Select a Quiz Topic:", font=('Helvetica', 14, 'bold')).pack(pady=(10, 5))
        self.topic_listbox = tk.Listbox(self.topic_frame, height=10, font=('Helvetica', 12), exportselection=False)
        for topic in self.topics:
            self.topic_listbox.insert(tk.END, topic['name'])
        self.topic_listbox.pack(pady=5, padx=20, fill=tk.X)
        if self.topics:
            self.topic_listbox.select_set(0)
        start_button = ttk.Button(self.topic_frame, text="Start Quiz", command=self.start_quiz)
        start_button.pack(pady=(10, 20))

    def start_quiz(self):
        selected_indices = self.topic_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select a topic.", parent=self.quiz_window)
            return
        selected_index = selected_indices[0]
        selected_topic_row = self.topics[selected_index]
        selected_topic_id = selected_topic_row['id']
        self.current_topic_name = selected_topic_row['name']
        print(f"Quiz Selected Topic: {self.current_topic_name} (ID: {selected_topic_id})")
        if not self.fetch_questions(selected_topic_id):
            messagebox.showinfo("No Questions", f"No questions found for '{self.current_topic_name}'.", parent=self.quiz_window)
            return
        self.current_question_index = 0
        self.score = 0
        self.topic_frame.pack_forget()
        self.setup_quiz_ui()
        self.load_question()

    def setup_quiz_ui(self):
        for widget in self.quiz_frame.winfo_children():
            widget.destroy()
        self.quiz_frame.pack(fill=tk.BOTH, expand=True)
        self.topic_label = ttk.Label(self.quiz_frame, text=f"Topic: {self.current_topic_name}", font=('Helvetica', 14, 'bold'))
        self.topic_label.pack(pady=(5, 10))
        self.q_num_label = ttk.Label(self.quiz_frame, text="", font=('Helvetica', 10))
        self.q_num_label.pack(pady=(0, 10))
        self.question_label = tk.Message(self.quiz_frame, text="Question text", font=('Helvetica', 12), width=550, justify=tk.LEFT)
        self.question_label.pack(pady=(5, 15), padx=10, fill=tk.X)
        self.options_frame = ttk.Frame(self.quiz_frame)
        self.options_frame.pack(pady=5, padx=20, anchor='w')
        self.radio_buttons = []
        options = ['A', 'B', 'C', 'D', 'E']
        for option in options:
             # This is where enable_check_button gets linked
             rb = ttk.Radiobutton(self.options_frame, text=f"{option}.", variable=self.selected_answer, value=option, command=self.enable_check_button)
             rb.pack(anchor='w', pady=2)
             self.radio_buttons.append(rb)
        self.feedback_label = ttk.Label(self.quiz_frame, text="", font=('Helvetica', 11, 'italic'))
        self.feedback_label.pack(pady=(10, 5))
        self.button_frame = ttk.Frame(self.quiz_frame)
        self.button_frame.pack(pady=(10, 15))
        # This is where check_answer gets linked
        self.check_button = ttk.Button(self.button_frame, text="Check Answer", command=self.check_answer, state=tk.DISABLED)
        self.check_button.grid(row=0, column=0, padx=5)
        self.next_button = ttk.Button(self.button_frame, text="Next Question", command=self.next_question, state=tk.DISABLED)
        self.next_button.grid(row=0, column=1, padx=5)

    def load_question(self):
        if self.current_question_index < len(self.questions):
            question_data = self.questions[self.current_question_index]
            self.q_num_label.config(text=f"Question {self.current_question_index + 1} of {len(self.questions)}")
            self.question_label.config(text=question_data['question_text'])
            options = ['A', 'B', 'C', 'D', 'E']
            option_keys = ['option_a', 'option_b', 'option_c', 'option_d', 'option_e']
            for i, rb in enumerate(self.radio_buttons):
                rb.config(text=f"{options[i]}. {question_data[option_keys[i]]}", state=tk.NORMAL)
            self.selected_answer.set("")
            self.feedback_label.config(text="")
            self.check_button.config(state=tk.DISABLED) # Ensure check button is disabled initially
            self.next_button.config(state=tk.DISABLED) # Ensure next button is disabled initially
            if self.current_question_index == len(self.questions) - 1:
                 self.next_button.config(text="Show Results")
            else:
                 self.next_button.config(text="Next Question")
        else:
            self.show_results()

    # *** Method with DEBUG prints added ***
    def enable_check_button(self):
        """Enables Check button when an answer is selected."""
        print("--- enable_check_button called ---") # DEBUG PRINT
        if not hasattr(self, 'check_button') or not self.check_button.winfo_exists():
            print("DEBUG: Check button doesn't exist or hasn't been created yet.") # DEBUG PRINT
            return
        if not hasattr(self, 'next_button') or not self.next_button.winfo_exists():
             print("DEBUG: Next button doesn't exist or hasn't been created yet.") # DEBUG PRINT
             return

        print(f"DEBUG: Next button state is: {self.next_button['state']}") # DEBUG PRINT
        # Only enable if the question is currently active (not already checked)
        if self.next_button['state'] == tk.DISABLED:
             print("DEBUG: Enabling Check button.") # DEBUG PRINT
             self.check_button.config(state=tk.NORMAL)
        else:
             print("DEBUG: Check button NOT enabled (Next button is not disabled).") # DEBUG PRINT

    # *** Method with DEBUG prints and try/except added ***
    def check_answer(self):
        """Checks the selected answer."""
        print("--- check_answer called ---") # DEBUG PRINT
        # Check if widgets exist - added checks for other relevant widgets too
        if not hasattr(self, 'check_button') or not self.check_button.winfo_exists():
            print("DEBUG: Check button no longer exists in check_answer.")
            return
        if not hasattr(self, 'next_button') or not self.next_button.winfo_exists():
            print("DEBUG: Next button no longer exists in check_answer.")
            return
        if not hasattr(self, 'radio_buttons') or not self.radio_buttons:
             print("DEBUG: Radio buttons list doesn't exist in check_answer.")
             return

        user_answer = self.selected_answer.get()
        print(f"DEBUG: User selected: {user_answer}") # DEBUG PRINT
        if not user_answer:
            # This should only happen if check_answer is called without selection
            # which enable_check_button logic should prevent, but good to check.
            print("DEBUG: check_answer called but no answer selected.")
            messagebox.showwarning("No Answer", "Please select an answer.", parent=self.quiz_window)
            return

        try:
            # Ensure index is valid before accessing self.questions
            if not (0 <= self.current_question_index < len(self.questions)):
                print(f"ERROR: Invalid current_question_index ({self.current_question_index}) in check_answer!")
                return

            correct_answer = self.questions[self.current_question_index]['correct_answer']
            print(f"DEBUG: Correct answer is: {correct_answer}") # DEBUG PRINT

            # Disable radio buttons and check button after checking
            for rb in self.radio_buttons:
                 # Add check if radio button still exists, belt-and-suspenders
                 if rb.winfo_exists():
                    rb.config(state=tk.DISABLED)
            self.check_button.config(state=tk.DISABLED)

            if user_answer == correct_answer:
                self.score += 1
                print("DEBUG: Answer Correct.") # DEBUG PRINT
                self.feedback_label.config(text="Correct!", foreground='green')
            else:
                correct_idx = ['A', 'B', 'C', 'D', 'E'].index(correct_answer) # Potential ValueError if correct_answer is invalid
                correct_option_text = self.radio_buttons[correct_idx]['text'] # Potential IndexError if correct_idx is invalid
                print("DEBUG: Answer Incorrect.") # DEBUG PRINT
                self.feedback_label.config(text=f"Incorrect. Correct: {correct_option_text}", foreground='red')

            # Enable the Next button
            print("DEBUG: Enabling Next button.") # DEBUG PRINT
            self.next_button.config(state=tk.NORMAL)

        except IndexError as e:
             # More specific error catching
            print(f"ERROR: IndexError in check_answer! Likely accessing invalid question index or radio button index. Error: {e}")
            print(f"DEBUG: current_question_index={self.current_question_index}, len(questions)={len(self.questions)}")
        except ValueError as e:
             print(f"ERROR: ValueError in check_answer! Likely correct_answer ('{correct_answer}') is not A, B, C, D, or E. Error: {e}")
        except Exception as e:
             print(f"ERROR inside check_answer: {type(e).__name__} - {e}") # Print type of error


    def next_question(self):
        if not self.next_button.winfo_exists(): return
        self.current_question_index += 1
        self.load_question()

    def show_results(self):
        for widget in self.quiz_frame.winfo_children():
            widget.destroy()
        ttk.Label(self.quiz_frame, text="Quiz Finished!", font=('Helvetica', 16, 'bold')).pack(pady=20)
        ttk.Label(self.quiz_frame, text=f"Your final score: {self.score} out of {len(self.questions)}", font=('Helvetica', 14)).pack(pady=10)
        close_button = ttk.Button(self.quiz_frame, text="Close Quiz", command=self.on_quiz_closing)
        close_button.pack(pady=20)

    def on_quiz_closing(self):
        print("Closing quiz window.")
        # Check if grab is set before releasing (optional, good practice)
        if self.quiz_window.grab_status() != "none":
            self.quiz_window.grab_release()
        self.quiz_window.destroy()


# --- Main Application Class ---
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Bowl Application")
        self.root.geometry("700x650")

        self.db_connection = connect_db()
        if not self.db_connection:
            self.root.destroy()
            return

        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        self.start_screen = None
        self.admin_panel = None
        self._create_start_screen()

        self.root.protocol("WM_DELETE_WINDOW", self.on_app_closing)

    def _create_start_screen(self):
        if self.admin_panel:
            self.admin_panel.pack_forget()
        self.start_screen = StartScreen(self.root,
                                        show_admin_callback=self.show_admin_panel,
                                        launch_quiz_callback=self.launch_quiz)
        self.start_screen.pack(fill=tk.BOTH, expand=True)

    def show_admin_panel(self):
        if self.start_screen:
            self.start_screen.pack_forget()
        if not self.admin_panel:
            print("Creating Admin Panel...")
            self.admin_panel = AdminPanel(self.root,
                                           self.db_connection,
                                           back_callback=self.show_start_screen,
                                           style=self.style)
        self.admin_panel.pack(fill=tk.BOTH, expand=True)
        print("Showing Admin Panel.")

    def show_start_screen(self):
         if self.admin_panel:
            self.admin_panel.pack_forget()
         if self.start_screen:
             self.start_screen.pack(fill=tk.BOTH, expand=True)
         else:
             self._create_start_screen()
         print("Showing Start Screen.")

    def launch_quiz(self):
        """Launches the QuizApp in a new Toplevel window."""
        print("Launching Quiz...")
        # --- Optional: Check if quiz window already exists ---
        quiz_window_exists = False
        for win in self.root.winfo_children():
             # Check if it's a Toplevel and has the expected title (or class)
             if isinstance(win, tk.Toplevel) and win.title() == "Quiz Bowl":
                 # Or check: if isinstance(getattr(win, '_w', None), QuizApp): # More robust maybe?
                 quiz_window_exists = True
                 print("Quiz window already open.")
                 win.lift() # Bring to front
                 try:
                     win.focus_force() # Try to give it focus
                     if win.grab_status() == "none": # Re-apply grab if lost?
                          print("Re-applying grab_set.")
                          win.grab_set()
                 except tk.TclError as e:
                     print(f"Could not focus/grab existing quiz window: {e}")
                 break # Stop checking

        if not quiz_window_exists:
             quiz_toplevel_window = tk.Toplevel(self.root)
             # --- You can test commenting this grab_set out if issues persist ---
             quiz_toplevel_window.grab_set()
             # -------------------------------------------------------------------
             quiz_app_instance = QuizApp(quiz_toplevel_window, self.db_connection)

    def on_app_closing(self):
        """Handles main application closing."""
        if self.db_connection:
            print("Closing main database connection.")
            self.db_connection.close()
        self.root.destroy()


# --- Main Execution ---
if __name__ == "__main__":
    main_window = tk.Tk()
    app = MainApp(main_window)
    main_window.mainloop()