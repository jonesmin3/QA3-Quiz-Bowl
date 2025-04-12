import tkinter as tk
from tkinter import ttk  # For themed widgets (optional, but looks nicer)
from tkinter import messagebox
import sqlite3
import os
import random

DATABASE_FILE = 'quiz_bowl_app.db'

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Bowl App")
        self.root.geometry("600x500") # Adjust size as needed

        # Style (optional, for ttk widgets)
        self.style = ttk.Style()
        self.style.theme_use('clam') # Or 'alt', 'default', 'classic'

        # State variables
        self.conn = None
        self.topics = [] # List of (id, name) tuples
        self.questions = [] # List of question data dictionaries/tuples for current topic
        self.current_question_index = 0
        self.score = 0
        self.selected_answer = tk.StringVar() # Holds the user's radio button selection

        # --- Frames ---
        # Frame for topic selection
        self.topic_frame = ttk.Frame(root, padding="10")
        # Frame for the quiz questions
        self.quiz_frame = ttk.Frame(root, padding="10")

        # --- Database Connection ---
        if not self.connect_db():
             messagebox.showerror("Database Error", f"Could not connect to {DATABASE_FILE}. Ensure it exists.")
             self.root.destroy() # Close app if DB connection fails
             return

        # --- Initial Setup ---
        self.fetch_topics()
        self.setup_topic_selection_ui()

        # --- Closing Protocol ---
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


    def connect_db(self):
        """Establishes connection to the SQLite database."""
        if not os.path.exists(DATABASE_FILE):
            return False
        try:
            self.conn = sqlite3.connect(DATABASE_FILE)
            # Use Row factory for easier access to columns by name
            self.conn.row_factory = sqlite3.Row
            print("Database connected successfully.")
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            self.conn = None
            return False

    def fetch_topics(self):
        """Fetches topic IDs and names from the database."""
        if not self.conn:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name FROM Topics ORDER BY name")
            self.topics = cursor.fetchall() # Fetches list of sqlite3.Row objects
            print(f"Fetched topics: {[t['name'] for t in self.topics]}")
        except sqlite3.Error as e:
            print(f"Error fetching topics: {e}")
            self.topics = []

    def fetch_questions(self, topic_id):
        """Fetches questions for the selected topic ID."""
        self.questions = []
        if not self.conn:
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, question_text, option_a, option_b, option_c, option_d, option_e, correct_answer
                FROM Questions
                WHERE topic_id = ?
            """, (topic_id,))
            self.questions = cursor.fetchall() # List of sqlite3.Row objects
            if self.questions:
                random.shuffle(self.questions) # Shuffle questions for variety
                print(f"Fetched {len(self.questions)} questions for topic ID {topic_id}.")
                return True
            else:
                print(f"No questions found for topic ID {topic_id}.")
                return False
        except sqlite3.Error as e:
            print(f"Error fetching questions: {e}")
            self.questions = []
            return False

    def setup_topic_selection_ui(self):
        """Creates the UI elements for selecting a topic."""
        # Clear any existing frames first (in case of restart)
        self.quiz_frame.pack_forget()
        self.topic_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.topic_frame, text="Select a Quiz Topic:", font=('Helvetica', 14, 'bold')).pack(pady=(10, 5))

        self.topic_listbox = tk.Listbox(self.topic_frame, height=10, font=('Helvetica', 12), exportselection=False)
        for topic in self.topics:
            self.topic_listbox.insert(tk.END, topic['name']) # Insert topic name
        self.topic_listbox.pack(pady=5, padx=20, fill=tk.X)

        # Select first item by default if list is not empty
        if self.topics:
            self.topic_listbox.select_set(0)

        start_button = ttk.Button(self.topic_frame, text="Start Quiz", command=self.start_quiz)
        start_button.pack(pady=(10, 20))

    def start_quiz(self):
        """Starts the quiz for the selected topic."""
        selected_indices = self.topic_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select a topic from the list.")
            return

        selected_index = selected_indices[0]
        selected_topic_row = self.topics[selected_index] # Get the sqlite3.Row object
        selected_topic_id = selected_topic_row['id']
        self.current_topic_name = selected_topic_row['name'] # Store name for display

        print(f"Selected Topic: {self.current_topic_name} (ID: {selected_topic_id})")

        if not self.fetch_questions(selected_topic_id):
            messagebox.showinfo("No Questions", f"No questions found for the topic '{self.current_topic_name}'.")
            return

        # Reset state for the new quiz
        self.current_question_index = 0
        self.score = 0

        # Switch frames
        self.topic_frame.pack_forget()
        self.setup_quiz_ui()
        self.load_question()

    def setup_quiz_ui(self):
        """Creates the UI elements for displaying questions and answers."""
        self.quiz_frame.pack(fill=tk.BOTH, expand=True)

        # Topic Label
        self.topic_label = ttk.Label(self.quiz_frame, text=f"Topic: {self.current_topic_name}", font=('Helvetica', 14, 'bold'))
        self.topic_label.pack(pady=(5, 10))

        # Question Number Label
        self.q_num_label = ttk.Label(self.quiz_frame, text="", font=('Helvetica', 10))
        self.q_num_label.pack(pady=(0, 10))

        # Question Text Label (using Message for potential wrapping)
        self.question_label = tk.Message(self.quiz_frame, text="Question text goes here", font=('Helvetica', 12), width=550, justify=tk.LEFT)
        self.question_label.pack(pady=(5, 15), padx=10, fill=tk.X)

        # Radio Buttons Frame
        self.options_frame = ttk.Frame(self.quiz_frame)
        self.options_frame.pack(pady=5, padx=20, anchor='w')

        self.radio_buttons = []
        options = ['A', 'B', 'C', 'D', 'E']
        for option in options:
             rb = ttk.Radiobutton(self.options_frame, text=f"{option}. Option Text", variable=self.selected_answer, value=option, command=self.enable_check_button)
             rb.pack(anchor='w', pady=2)
             self.radio_buttons.append(rb)

        # Feedback Label
        self.feedback_label = ttk.Label(self.quiz_frame, text="", font=('Helvetica', 11, 'italic'))
        self.feedback_label.pack(pady=(10, 5))

        # Buttons Frame
        self.button_frame = ttk.Frame(self.quiz_frame)
        self.button_frame.pack(pady=(10, 15))

        # Check Answer Button
        self.check_button = ttk.Button(self.button_frame, text="Check Answer", command=self.check_answer, state=tk.DISABLED)
        self.check_button.grid(row=0, column=0, padx=5)

        # Next Question Button
        self.next_button = ttk.Button(self.button_frame, text="Next Question", command=self.next_question, state=tk.DISABLED)
        self.next_button.grid(row=0, column=1, padx=5)


    def load_question(self):
        """Loads the current question and options into the UI."""
        if self.current_question_index < len(self.questions):
            question_data = self.questions[self.current_question_index]

            # Update Question Number Label
            self.q_num_label.config(text=f"Question {self.current_question_index + 1} of {len(self.questions)}")

            # Update Question Text
            self.question_label.config(text=question_data['question_text'])

            # Update Radio Button Options
            options = ['A', 'B', 'C', 'D', 'E']
            option_texts = [
                question_data['option_a'],
                question_data['option_b'],
                question_data['option_c'],
                question_data['option_d'],
                question_data['option_e']
            ]

            for i, rb in enumerate(self.radio_buttons):
                rb.config(text=f"{options[i]}. {option_texts[i]}", state=tk.NORMAL) # Enable radio buttons

            # Reset state for the new question
            self.selected_answer.set("") # Clear previous selection
            self.feedback_label.config(text="") # Clear feedback
            self.check_button.config(state=tk.DISABLED) # Disable check until an option is selected
            self.next_button.config(state=tk.DISABLED) # Disable next until answer is checked

        else:
            # End of quiz
            self.show_results()

    def enable_check_button(self):
        """Enables the Check Answer button once a radio button is selected."""
        # This check might be redundant if check_answer disables radios,
        # but good practice if logic changes.
        if self.check_button['state'] == tk.NORMAL:
             return # Avoid re-enabling if already checked

        if self.selected_answer.get(): # Check if a value is selected
            self.check_button.config(state=tk.NORMAL)

    def check_answer(self):
        """Checks the selected answer against the correct answer."""
        user_answer = self.selected_answer.get()
        if not user_answer:
            messagebox.showwarning("No Answer", "Please select an answer.")
            return

        correct_answer = self.questions[self.current_question_index]['correct_answer']

        # Disable radio buttons and check button after checking
        for rb in self.radio_buttons:
            rb.config(state=tk.DISABLED)
        self.check_button.config(state=tk.DISABLED)

        if user_answer == correct_answer:
            self.score += 1
            self.feedback_label.config(text="Correct!", foreground='green')
        else:
            # Find the full text of the correct answer
            correct_option_text = ""
            correct_idx = ['A', 'B', 'C', 'D', 'E'].index(correct_answer)
            correct_option_text = self.radio_buttons[correct_idx]['text'] # Get text from the correct radio btn

            self.feedback_label.config(text=f"Incorrect. The correct answer was: {correct_option_text}", foreground='red')

        # Enable the Next button
        self.next_button.config(state=tk.NORMAL)
        if self.current_question_index == len(self.questions) - 1:
             self.next_button.config(text="Show Results") # Change button text for last question


    def next_question(self):
        """Loads the next question or shows results if finished."""
        self.current_question_index += 1
        self.load_question()

    def show_results(self):
        """Displays the final score."""
        # Clear the quiz frame
        for widget in self.quiz_frame.winfo_children():
            widget.destroy()

        # Display results
        ttk.Label(self.quiz_frame, text="Quiz Finished!", font=('Helvetica', 16, 'bold')).pack(pady=20)
        ttk.Label(self.quiz_frame, text=f"Your final score: {self.score} out of {len(self.questions)}", font=('Helvetica', 14)).pack(pady=10)

        # Option to restart
        restart_button = ttk.Button(self.quiz_frame, text="Select Another Topic", command=self.setup_topic_selection_ui)
        restart_button.pack(pady=20)


    def on_closing(self):
        """Handles window closing event."""
        if self.conn:
            print("Closing database connection.")
            self.conn.close()
        self.root.destroy()


# --- Main Execution ---
if __name__ == "__main__":
    main_window = tk.Tk()
    app = QuizApp(main_window)
    main_window.mainloop()