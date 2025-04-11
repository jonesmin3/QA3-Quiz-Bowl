# QA3-Project: Quiz Bowl Application

## The PASSWORD to access the administrator interface is:
- CanIPleaseHaveExtraCreditPorFavor

## Overview

This project is a quarterly assessment where you will develop a comprehensive Quiz Bowl application with a graphical user interface (GUI). The application will integrate database management with frontend development to provide a complete application experience. The application has two major components:

1. **Administrator Interface**: Allows an admin to manage quiz content (password-protected).
2. **User Interface**: Provides a platform for users to take quizzes based on topics from courses the user is enrolled in.

## Features

- **Administrator Interface**:
  - Login screen with password protection.
  - Forms for adding, viewing, modifying, and deleting quiz questions.
  - Admin access to five different categories of quizzes, each corresponding to a course.
  
- **User Interface**:
  - Welcome screen where users can select a quiz category.
  - Quiz interface that presents multiple-choice questions.
  - Immediate feedback for each answer.
  - A scoring mechanism to track performance.

## Database Structure

The application includes a database with 6 tables, one for each course category. Each table contains:

- At least 10 multiple-choice questions per course:
- Each question includes:
  - Question text
  - 5 Answer-choice options
  - Correct answer

## Technical Requirements

### Application Entry Point

- A login screen offers two paths:
  1. **Administrator Access** (password-protected).
  2. **Quiz Taker Access** (no authentication required).

### Administrator Workflow

- Forms for:
  - Adding new questions (category selection, question text, answer options, correct answer).
  - Viewing existing questions (filterable by category).
  - Modifying or deleting questions.
  
### Quiz Taker Workflow

- Welcome screen with category selection.
- Quiz interface displaying questions (either one by one or all at once, depending on the design choice).
- Answer submission with immediate feedback.
- Final score display after completing the quiz.

### Programming Requirements

- **Question Class**: Handles question display and answer validation.
- **Error Handling**: Proper error handling for database operations.
- **Object-Oriented Design**: Following OOP principles.
- **Comments & Documentation**: Include appropriate comments for better code readability.

## Installation Instructions

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.x**: This application is written in Python, so you'll need Python 3.x installed on your system.
  - [Download Python 3.x](https://www.python.org/downloads/)

- **Git**: You'll need Git to clone the repository to your local machine.
  - [Download Git](https://git-scm.com/)

- **Tkinter**: Tkinter is the standard Python interface to the Tk GUI toolkit and is used for creating the graphical user interface. Tkinter is included with Python, so no separate installation is needed. If for some reason it's not available, you can install it using:
  - **Windows/Linux**: Tkinter is bundled with Python, but you can install it with:
    ```bash
    sudo apt-get install python3-tk   # For Ubuntu/Debian
    ```

- **SQLite3 (optional)**: If you're using SQLite as the database, it's included with Python, but you might want to ensure that the `sqlite3` library is available:
  - **Windows/Linux**: SQLite3 is included with Python 3.x. If needed, you can install the `sqlite3` package via:
    ```bash
    pip install sqlite3
    ```

### Steps

1. **Clone the Repository**

   Open your terminal or command prompt and run the following command to clone the repository:

   ```bash
   git clone https://github.com/your-username/quiz-bowl.git
  
### Key Updates:
- **Tkinter**: Included information on how Tkinter is used for the GUI and how to install it (if not pre-installed).
- **SQLite3**: Added information for the SQLite database, as it's commonly used for applications like this.
- **Dependencies**: If you have a `requirements.txt` file, it would be ideal to list the necessary packages in that file. However, I also included manual installation instructions for Tkinter and SQLite, in case the user needs them.
  
This should now cover all necessary installation details and libraries.