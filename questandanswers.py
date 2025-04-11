import sqlite3
import os

# --- Configuration ---
DATABASE_FILE = 'quiz_bowl_app.db'
# Ensure topic names exactly match those in the Topics table
# (Case-sensitive)
TOPICS = [
    "DS 3850",                  # Intro Python
    "DS 3860",                  # Intro Databases
    "Money and Banking",
    "Theater",                  # Intro Theater
    "Investment Challenge I",   # Investment Strategies
    "Intermediate Finance"
]

# --- Sample Question Data ---
# Structure: List of dictionaries
# Each dictionary: 'topic', 'question', 'A', 'B', 'C', 'D', 'E', 'correct' ('A' through 'E')
ALL_QUESTIONS_DATA = []

# == DS 3850 (Intro Python) Questions ==
ds3850_questions = [
    {
        'topic': "DS 3850",
        'question': "Which of the following is used to define a block of code (body of a function, loop, etc.) in Python?",
        'A': "Curly braces {}", 'B': "Parentheses ()", 'C': "Indentation", 'D': "Brackets []", 'E': "END keyword",
        'correct': 'C'
    },
    {
        'topic': "DS 3850",
        'question': "What is the data type of the result of `6 / 2` in Python 3?",
        'A': "Integer (int)", 'B': "Float (float)", 'C': "String (str)", 'D': "Boolean (bool)", 'E': "List",
        'correct': 'B'
    },
    {
        'topic': "DS 3850",
        'question': "Which keyword is used to define a function in Python?",
        'A': "fun", 'B': "define", 'C': "function", 'D': "def", 'E': "proc",
        'correct': 'D'
    },
    {
        'topic': "DS 3850",
        'question': "How do you comment a single line in Python?",
        'A': "// Comment", 'B': "/* Comment */", 'C': "# Comment", 'D': "-- Comment", 'E': "' Comment",
        'correct': 'C'
    },
    {
        'topic': "DS 3850",
        'question': "Which collection type is ordered, mutable (changeable), and allows duplicate members?",
        'A': "Tuple", 'B': "Set", 'C': "Dictionary", 'D': "String", 'E': "List",
        'correct': 'E'
    },
    {
        'topic': "DS 3850",
        'question': "What does the `len()` function do when used with a list?",
        'A': "Returns the last item", 'B': "Returns the largest item", 'C': "Returns the number of items", 'D': "Sorts the list", 'E': "Reverses the list",
        'correct': 'C'
    },
    {
        'topic': "DS 3850",
        'question': "Which operator is used for exponentiation (raising to the power)?",
        'A': "^", 'B': "**", 'C': "*^", 'D': "pow() only", 'E': "//",
        'correct': 'B'
    },
    {
        'topic': "DS 3850",
        'question': "What keyword is used to exit a loop prematurely?",
        'A': "exit", 'B': "stop", 'C': "continue", 'D': "pass", 'E': "break",
        'correct': 'E'
    },
    {
        'topic': "DS 3850",
        'question': "Which of the following creates an empty dictionary?",
        'A': "dict[]", 'B': "{}", 'C': "dict()", 'D': "Both B and C", 'E': "list()",
        'correct': 'D'
    },
    {
        'topic': "DS 3850",
        'question': "What method is used to add an item to the end of a list?",
        'A': "add()", 'B': "insert()", 'C': "push()", 'D': "append()", 'E': "extend()",
        'correct': 'D'
    }
]
ALL_QUESTIONS_DATA.extend(ds3850_questions)

# == DS 3860 (Intro Databases) Questions ==
ds3860_questions = [
    {
        'topic': "DS 3860",
        'question': "What is the primary goal of database normalization?",
        'A': "Increase data redundancy", 'B': "Reduce data redundancy and improve data integrity", 'C': "Make databases faster", 'D': "Decrease database security", 'E': "Combine all data into one table",
        'correct': 'B'
    },
    {
        'topic': "DS 3860",
        'question': "A table is in First Normal Form (1NF) if:",
        'A': "It has no repeating groups or multi-valued attributes", 'B': "It has a composite primary key", 'C': "All non-key attributes depend on the full primary key", 'D': "It has no transitive dependencies", 'E': "It contains redundant data",
        'correct': 'A'
    },
    {
        'topic': "DS 3860",
        'question': "In an Entity-Relationship (ER) model, what does an entity represent?",
        'A': "A relationship between tables", 'B': "An action or query", 'C': "A real-world object or concept (e.g., Customer, Product)", 'D': "An attribute of an object", 'E': "A database constraint",
        'correct': 'C'
    },
    {
        'topic': "DS 3860",
        'question': "What does 'Cardinality' in an ER diagram specify?",
        'A': "The number of attributes an entity has", 'B': "The type of relationship (e.g., identifying)", 'C': "The number of instances of one entity that can relate to instances of another entity", 'D': "The primary key of an entity", 'E': "The level of normalization",
        'correct': 'C'
    },
    {
        'topic': "DS 3860",
        'question': "Which SQL keyword is used to retrieve data from a database?",
        'A': "GET", 'B': "RETRIEVE", 'C': "SELECT", 'D': "FETCH", 'E': "OPEN",
        'correct': 'C'
    },
    {
        'topic': "DS 3860",
        'question': "Third Normal Form (3NF) primarily deals with eliminating which type of dependency?",
        'A': "Partial dependencies", 'B': "Multi-valued dependencies", 'C': "Functional dependencies", 'D': "Transitive dependencies", 'E': "Join dependencies",
        'correct': 'D'
    },
    {
        'topic': "DS 3860",
        'question': "In an ER diagram, a rectangle typically represents a(n):",
        'A': "Relationship", 'B': "Attribute", 'C': "Entity", 'D': "Cardinality constraint", 'E': "Key",
        'correct': 'C'
    },
    {
        'topic': "DS 3860",
        'question': "Which constraint ensures that a column cannot have NULL values?",
        'A': "UNIQUE", 'B': "PRIMARY KEY", 'C': "FOREIGN KEY", 'D': "CHECK", 'E': "NOT NULL",
        'correct': 'E'
    },
    {
        'topic': "DS 3860",
        'question': "A `FOREIGN KEY` constraint links a column in one table to which type of key in another table?",
        'A': "Alternate Key", 'B': "Super Key", 'C': "Candidate Key", 'D': "Primary Key", 'E': "Secondary Key",
        'correct': 'D'
    },
     {
        'topic': "DS 3860",
        'question': "What is the main characteristic of Second Normal Form (2NF)?",
        'A': "Eliminates multi-valued attributes", 'B': "Eliminates transitive dependencies", 'C': "Requires 1NF and eliminates partial dependencies", 'D': "Requires a primary key", 'E': "Allows data redundancy",
        'correct': 'C'
    }
]
ALL_QUESTIONS_DATA.extend(ds3860_questions)

# == Money and Banking Questions ==
money_banking_questions = [
    {
        'topic': "Money and Banking",
        'question': "Who is primarily responsible for conducting monetary policy in the United States?",
        'A': "The U.S. Treasury", 'B': "The President", 'C': "The Federal Reserve (The Fed)", 'D': "The Congress", 'E': "The World Bank",
        'correct': 'C'
    },
    {
        'topic': "Money and Banking",
        'question': "Which of these is a primary tool of monetary policy used by the Fed?",
        'A': "Setting income tax rates", 'B': "Government spending", 'C': "Open market operations (buying/selling bonds)", 'D': "Regulating stock markets", 'E': "Issuing passports",
        'correct': 'C'
    },
    {
        'topic': "Money and Banking",
        'question': "What is the 'discount rate'?",
        'A': "The interest rate banks charge their best customers", 'B': "The rate of inflation", 'C': "The interest rate at which commercial banks can borrow money directly from the Fed", 'D': "The tax rate on savings accounts", 'E': "The currency exchange rate",
        'correct': 'C'
    },
    {
        'topic': "Money and Banking",
        'question': "The 'reserve requirement' refers to the fraction of a bank's _____ that they must hold in reserve.",
        'A': "Profits", 'B': "Assets", 'C': "Checkable deposits", 'D': "Loans", 'E': "Stock value",
        'correct': 'C'
    },
    {
        'topic': "Money and Banking",
        'question': "If the Fed wants to increase the money supply, it typically will:",
        'A': "Sell government bonds", 'B': "Increase the reserve requirement", 'C': "Increase the discount rate", 'D': "Buy government bonds", 'E': "Advise Congress to raise taxes",
        'correct': 'D'
    },
     {
        'topic': "Money and Banking",
        'question': "What is fiat money?",
        'A': "Money backed by gold", 'B': "Money issued by foreign countries", 'C': "Money declared legal tender by government order, not backed by a physical commodity", 'D': "Digital currency like Bitcoin", 'E': "Money used only for international trade",
        'correct': 'C'
    },
    {
        'topic': "Money and Banking",
        'question': "What does FDIC stand for?",
        'A': "Federal Debt Insurance Corporation", 'B': "Financial Deposit Insurance Company", 'C': "Federal Deposit Insurance Corporation", 'D': "Federal Dividend Investment Commission", 'E': "Fiscal Department for International Commerce",
        'correct': 'C'
    },
    {
        'topic': "Money and Banking",
        'question': "Which measure of the money supply typically includes currency, demand deposits, traveler's checks, and other checkable deposits?",
        'A': "M0", 'B': "M1", 'C': "M2", 'D': "M3", 'E': "MB (Monetary Base)",
        'correct': 'B'
    },
    {
        'topic': "Money and Banking",
        'question': "Inflation is best described as:",
        'A': "A decrease in the overall price level", 'B': "An increase in the unemployment rate", 'C': "A sustained increase in the overall price level", 'D': "A decrease in the money supply", 'E': "A period of economic recession",
        'correct': 'C'
    },
    {
        'topic': "Money and Banking",
        'question': "Fractional reserve banking means that banks are required to hold:",
        'A': "All of their deposits in reserve", 'B': "A fraction of their deposits in reserve", 'C': "Only gold as reserves", 'D': "No reserves", 'E': "Reserves equal to their loans",
        'correct': 'B'
    }
]
ALL_QUESTIONS_DATA.extend(money_banking_questions)

# == Theater (Intro) Questions ==
theater_questions = [
    {
        'topic': "Theater",
        'question': "Which type of stage is surrounded by the audience on all sides?",
        'A': "Proscenium stage", 'B': "Thrust stage", 'C': "Black box stage", 'D': "Arena stage (Theatre-in-the-round)", 'E': "Found space",
        'correct': 'D'
    },
    {
        'topic': "Theater",
        'question': "Who is widely considered the most famous English playwright, author of 'Hamlet' and 'Romeo and Juliet'?",
        'A': "Christopher Marlowe", 'B': "George Bernard Shaw", 'C': "Oscar Wilde", 'D': "William Shakespeare", 'E': "Arthur Miller",
        'correct': 'D'
    },
    {
        'topic': "Theater",
        'question': "The person responsible for the overall artistic vision and interpretation of a play's production is the:",
        'A': "Playwright", 'B': "Producer", 'C': "Stage Manager", 'D': "Director", 'E': "Lead Actor",
        'correct': 'D'
    },
    {
        'topic': "Theater",
        'question': "Which ancient civilization is credited with the origins of Western theatre, particularly tragedy and comedy?",
        'A': "Roman", 'B': "Egyptian", 'C': "Greek", 'D': "Mesopotamian", 'E': "Chinese",
        'correct': 'C'
    },
    {
        'topic': "Theater",
        'question': "What is the written text of a play called?",
        'A': "Score", 'B': "Libretto", 'C': "Script", 'D': "Folio", 'E': "Monologue",
        'correct': 'C'
    },
     {
        'topic': "Theater",
        'question': "A 'thrust stage' extends into the audience, who sit on how many sides?",
        'A': "One", 'B': "Two", 'C': "Three", 'D': "Four", 'E': "Zero (it's flat)",
        'correct': 'C'
    },
    {
        'topic': "Theater",
        'question': "Scenery, costumes, and lighting are all elements of:",
        'A': "Acting", 'B': "Directing", 'C': "Playwriting", 'D': "Dramaturgy", 'E': "Design (Spectacle)",
        'correct': 'E'
    },
    {
        'topic': "Theater",
        'question': "A play primarily intended to make the audience laugh is categorized as a:",
        'A': "Tragedy", 'B': "History Play", 'C': "Melodrama", 'D': "Comedy", 'E': "Farce (though a type of comedy)",
        'correct': 'D'
    },
    {
        'topic': "Theater",
        'question': "The 'Antagonist' in a play is typically the character who:",
        'A': "Delivers the opening lines", 'B': "Is the main character (hero)", 'C': "Provides comic relief", 'D': "Opposes the main character (protagonist)", 'E': "Narrates the story",
        'correct': 'D'
    },
    {
        'topic': "Theater",
        'question': "What does 'blocking' refer to in theatre?",
        'A': "Forgetting lines", 'B': "The set construction", 'C': "The planned movement of actors on stage", 'D': "Audience seating arrangement", 'E': "Writing the play",
        'correct': 'C'
    }
]
ALL_QUESTIONS_DATA.extend(theater_questions)

# == Investment Challenge I (Investment Strategies) Questions ==
investment_questions = [
    {
        'topic': "Investment Challenge I",
        'question': "Spreading your investments across various asset classes (stocks, bonds, real estate) is known as:",
        'A': "Concentration", 'B': "Timing the market", 'C': "Diversification", 'D': "Leveraging", 'E': "Hedging",
        'correct': 'C'
    },
    {
        'topic': "Investment Challenge I",
        'question': "Which of the following generally represents ownership in a corporation?",
        'A': "Bond", 'B': "Mutual Fund", 'C': "Stock", 'D': "Certificate of Deposit (CD)", 'E': "Option",
        'correct': 'C'
    },
    {
        'topic': "Investment Challenge I",
        'question': "The relationship between risk and expected return in investments is typically:",
        'A': "Inverse (higher risk, lower return)", 'B': "Direct (higher risk, higher potential return)", 'C': "Unrelated", 'D': "Negative", 'E': "Fixed",
        'correct': 'B'
    },
    {
        'topic': "Investment Challenge I",
        'question': "An investment strategy focused on buying stocks that appear to be trading for less than their intrinsic value is called:",
        'A': "Growth investing", 'B': "Index investing", 'C': "Momentum investing", 'D': "Value investing", 'E': "Income investing",
        'correct': 'D'
    },
    {
        'topic': "Investment Challenge I",
        'question': "The S&P 500 is an example of a:",
        'A': "Type of bond", 'B': "Government agency", 'C': "Stock market index", 'D': "Mutual fund company", 'E': "Type of commodity",
        'correct': 'C'
    },
     {
        'topic': "Investment Challenge I",
        'question': "What does 'asset allocation' refer to?",
        'A': "Choosing specific stocks", 'B': "Deciding how to divide investment funds among different asset classes", 'C': "Calculating investment fees", 'D': "Predicting market movements", 'E': "Withdrawing funds from an investment",
        'correct': 'B'
    },
    {
        'topic': "Investment Challenge I",
        'question': "A 'bull market' is characterized by:",
        'A': "Falling prices and pessimism", 'B': "Rising prices and optimism", 'C': "High volatility", 'D': "Low trading volume", 'E': "Government intervention",
        'correct': 'B'
    },
    {
        'topic': "Investment Challenge I",
        'question': "Buying and holding a diversified portfolio for the long term, regardless of market fluctuations, is characteristic of:",
        'A': "Day trading", 'B': "Market timing", 'C': "Passive investing", 'D': "Active trading", 'E': "Sector rotation",
        'correct': 'C'
    },
    {
        'topic': "Investment Challenge I",
        'question': "Which type of investment typically represents a loan made by an investor to a borrower (corporate or governmental)?",
        'A': "Stock", 'B': "Real Estate", 'C': "Commodity", 'D': "Bond", 'E': "Mutual Fund Share",
        'correct': 'D'
    },
    {
        'topic': "Investment Challenge I",
        'question': "An investment strategy focusing on companies expected to grow earnings at an above-average rate is known as:",
        'A': "Value investing", 'B': "Income investing", 'C': "Growth investing", 'D': "Contrarian investing", 'E': "Index investing",
        'correct': 'C'
    }
]
ALL_QUESTIONS_DATA.extend(investment_questions)

# == Intermediate Finance Questions ==
finance_questions = [
    {
        'topic': "Intermediate Finance",
        'question': "What does 'Time Value of Money' (TVM) fundamentally state?",
        'A': "Money loses value over time due to inflation", 'B': "A dollar received today is worth more than a dollar received in the future", 'C': "Interest rates always go up", 'D': "Future money is more valuable than present money", 'E': "All investments earn the same rate of return",
        'correct': 'B'
    },
    {
        'topic': "Intermediate Finance",
        'question': "Which capital budgeting technique calculates the present value of future cash flows minus the initial investment?",
        'A': "Payback Period", 'B': "Internal Rate of Return (IRR)", 'C': "Accounting Rate of Return (ARR)", 'D': "Profitability Index (PI)", 'E': "Net Present Value (NPV)",
        'correct': 'E'
    },
    {
        'topic': "Intermediate Finance",
        'question': "The Internal Rate of Return (IRR) is the discount rate at which:",
        'A': "NPV is maximized", 'B': "NPV equals zero", 'C': "NPV is minimized", 'D': "The payback period is shortest", 'E': "Future cash flows equal initial investment (undiscounted)",
        'correct': 'B'
    },
    {
        'topic': "Intermediate Finance",
        'question': "WACC stands for:",
        'A': "Weighted Average Cost of Capital", 'B': "Working Asset Current Cost", 'C': "Weighted Asset Computation Cost", 'D': "World Average Currency Conversion", 'E': "Worst Assumed Capital Cost",
        'correct': 'A'
    },
    {
        'topic': "Intermediate Finance",
        'question': "What does the WACC represent for a company?",
        'A': "Its historical average profit margin", 'B': "The required return on its equity", 'C': "The average rate of return required by all of its investors (debt and equity)", 'D': "The risk-free rate of return", 'E': "The cost of issuing new stock",
        'correct': 'C'
    },
     {
        'topic': "Intermediate Finance",
        'question': "If a project's NPV is positive, the company should generally:",
        'A': "Reject the project", 'B': "Be indifferent about the project", 'C': "Accept the project", 'D': "Recalculate using IRR", 'E': "Wait for interest rates to drop",
        'correct': 'C'
    },
    {
        'topic': "Intermediate Finance",
        'question': "The process of planning and managing a firm's long-term investments is known as:",
        'A': "Working Capital Management", 'B': "Financial Statement Analysis", 'C': "Capital Budgeting", 'D': "Risk Management", 'E': "Dividend Policy",
        'correct': 'C'
    },
    {
        'topic': "Intermediate Finance",
        'question': "Systematic risk (or market risk) is risk that:",
        'A': "Can be eliminated through diversification", 'B': "Affects only a specific company", 'C': "Affects a large number of assets or the entire market", 'D': "Is related to a company's management team", 'E': "Is zero for government bonds",
        'correct': 'C'
    },
    {
        'topic': "Intermediate Finance",
        'question': "Calculating the future value of a present sum is called:",
        'A': "Discounting", 'B': "Compounding", 'C': "Amortizing", 'D': "Factoring", 'E': "Budgeting",
        'correct': 'B'
    },
    {
        'topic': "Intermediate Finance",
        'question': "Which component is typically considered 'risk-free' when calculating the cost of equity using CAPM?",
        'A': "Beta", 'B': "Market Risk Premium", 'C': "Return on company stock", 'D': "Return on a U.S. Treasury Bill/Bond", 'E': "Expected market return",
        'correct': 'D'
    }
]
ALL_QUESTIONS_DATA.extend(finance_questions)


# --- Database Functions ---
def create_connection(db_file):
    """ Create a database connection to the SQLite database specified by db_file """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"SQLite connection established to {db_file}")
        # Enable foreign key constraint enforcement
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def execute_sql(conn, sql_statement):
    """ Execute a single SQL statement """
    try:
        cursor = conn.cursor()
        cursor.execute(sql_statement)
        conn.commit()
        print(f"Executed: {sql_statement.splitlines()[0]}...")
    except sqlite3.Error as e:
        print(f"Error executing SQL: {e}\nStatement: {sql_statement}")


def get_topic_id(conn, topic_name):
    """ Get the ID of a topic from the Topics table """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM Topics WHERE name = ?", (topic_name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            print(f"Warning: Topic '{topic_name}' not found in the database.")
            return None
    except sqlite3.Error as e:
        print(f"Error retrieving topic ID for '{topic_name}': {e}")
        return None

def add_question(conn, topic_id, q_data):
    """ Add a single question to the Questions table """
    sql = ''' INSERT INTO Questions(topic_id, question_text, option_a, option_b, option_c, option_d, option_e, correct_answer)
              VALUES(?,?,?,?,?,?,?,?) '''
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (
            topic_id,
            q_data['question'],
            q_data['A'],
            q_data['B'],
            q_data['C'],
            q_data['D'],
            q_data['E'],
            q_data['correct']
        ))
        # Removed commit from here to commit once after all insertions
        return cursor.lastrowid # Return the id of the inserted question
    except sqlite3.Error as e:
        print(f"Error adding question: {e}\nData: {q_data}")
        return None
    except KeyError as e:
        print(f"Error: Missing key in question data: {e}\nData: {q_data}")
        return None


# --- Main Execution ---
if __name__ == '__main__':
    if not os.path.exists(DATABASE_FILE):
        print(f"Error: Database file '{DATABASE_FILE}' not found.")
        print("Please run the script to create the database first.")
    else:
        print(f"Connecting to database: {DATABASE_FILE}")
        conn = create_connection(DATABASE_FILE)

        if conn:
            print("\n" + "="*40)
            print("WARNING:")
            print("This script will:")
            print("1. DROP the existing 'Questions' table (if it exists).")
            print("2. CREATE a new 'Questions' table suitable for multiple-choice.")
            print("3. Populate the new table with sample questions.")
            print("Any data currently in the 'Questions' table will be lost.")
            print("="*40 + "\n")

            # --- Step 1: Modify Schema ---
            print("Modifying Questions table schema...")
            sql_drop_questions_table = "DROP TABLE IF EXISTS Questions;"
            # New schema for Questions table
            sql_create_new_questions_table = """CREATE TABLE IF NOT EXISTS Questions (
                                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                    topic_id INTEGER NOT NULL,
                                                    question_text TEXT NOT NULL,
                                                    option_a TEXT NOT NULL,
                                                    option_b TEXT NOT NULL,
                                                    option_c TEXT NOT NULL,
                                                    option_d TEXT NOT NULL,
                                                    option_e TEXT NOT NULL,
                                                    correct_answer TEXT NOT NULL CHECK(correct_answer IN ('A', 'B', 'C', 'D', 'E')),
                                                    FOREIGN KEY (topic_id) REFERENCES Topics (id) ON DELETE CASCADE
                                                );"""
            execute_sql(conn, sql_drop_questions_table)
            execute_sql(conn, sql_create_new_questions_table)
            print("Schema modification complete.")

            # --- Step 2: Add Questions ---
            print("\nAdding questions to the database...")
            question_count = 0
            skipped_count = 0
            for q_data in ALL_QUESTIONS_DATA:
                topic_name = q_data.get('topic')
                if not topic_name:
                    print(f"Skipping question due to missing topic: {q_data.get('question')}")
                    skipped_count += 1
                    continue

                topic_id = get_topic_id(conn, topic_name)

                if topic_id:
                    question_id = add_question(conn, topic_id, q_data)
                    if question_id:
                         question_count += 1
                         # print(f"Added question ID {question_id} for topic '{topic_name}'") # Uncomment for verbose output
                    else:
                         skipped_count += 1
                else:
                    # Error message printed within get_topic_id
                    skipped_count += 1

            # --- Step 3: Commit and Close ---
            if question_count > 0:
                print(f"\nCommitting {question_count} added questions...")
                conn.commit() # Commit all changes at once
            else:
                 print("\nNo questions were added.")

            print("\nClosing database connection.")
            conn.close()

            print("\n--- Summary ---")
            print(f"Successfully added {question_count} questions.")
            if skipped_count > 0:
                print(f"Skipped {skipped_count} questions (due to errors or missing topics). Check warnings above.")
            print(f"Database '{DATABASE_FILE}' has been populated.")

        else:
            print("Failed to connect to the database. Aborting.")