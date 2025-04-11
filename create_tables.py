import sqlite3
import os

# --- Configuration ---
DATABASE_FILE = 'quiz_bowl_app.db'
INITIAL_TOPICS = [
    "Money and Banking",
    "DS 3860",
    "DS 3850",
    "Investment Challenge I",
    "Theater",
    "Intermediate Finance"
]

# --- Functions ---
def create_connection(db_file):
    """ Create a database connection to the SQLite database specified by db_file """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"SQLite connection established to {db_file} (Version: {sqlite3.sqlite_version})")
        # Enable foreign key constraint enforcement (important for relational integrity)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_table(conn, create_table_sql):
    """ Create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        print(f"Executed: {create_table_sql.splitlines()[0]}...") # Print first line for brevity
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def add_topic(conn, topic_name):
    """
    Add a new topic into the Topics table.
    Uses INSERT OR IGNORE to avoid errors if the topic already exists.
    :param conn: Connection object
    :param topic_name: Name of the topic to add
    :return: topic id
    """
    sql = ''' INSERT OR IGNORE INTO Topics(name)
              VALUES(?) '''
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (topic_name,))
        conn.commit()
        # Get the id of the inserted (or ignored) row
        cursor.execute("SELECT id FROM Topics WHERE name = ?", (topic_name,))
        topic_id = cursor.fetchone()
        if topic_id:
             print(f"Topic '{topic_name}' ensured in database (ID: {topic_id[0]}).")
             return topic_id[0]
        else:
             # This case should ideally not happen with INSERT OR IGNORE
             # unless something went very wrong.
             print(f"Warning: Could not retrieve ID for topic '{topic_name}'.")
             return None

    except sqlite3.Error as e:
        print(f"Error adding topic '{topic_name}': {e}")
        return None

# --- Main Execution ---
if __name__ == '__main__':
    # Define SQL statements for creating tables
    # Using IF NOT EXISTS prevents errors if the script is run multiple times
    sql_create_topics_table = """ CREATE TABLE IF NOT EXISTS Topics (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        name TEXT NOT NULL UNIQUE
                                    ); """

    # The Questions table links to the Topics table using topic_id
    # ON DELETE CASCADE means if a topic is deleted, all its questions are also deleted.
    sql_create_questions_table = """CREATE TABLE IF NOT EXISTS Questions (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        topic_id INTEGER NOT NULL,
                                        question_text TEXT NOT NULL,
                                        answer_text TEXT NOT NULL,
                                        FOREIGN KEY (topic_id) REFERENCES Topics (id) ON DELETE CASCADE
                                    );"""

    # --- Create database and tables ---
    print(f"Creating database file: {DATABASE_FILE}")
    conn = create_connection(DATABASE_FILE)

    if conn is not None:
        # Create tables
        print("\nCreating tables...")
        create_table(conn, sql_create_topics_table)
        create_table(conn, sql_create_questions_table)

        # Add initial topics
        print("\nAdding initial topics...")
        for topic in INITIAL_TOPICS:
            add_topic(conn, topic)

        # Close the connection
        print("\nClosing database connection.")
        conn.close()
        print(f"\nDatabase '{DATABASE_FILE}' created successfully with initial topics.")
        print(f"File location: {os.path.abspath(DATABASE_FILE)}")
        print("\nNext steps:")
        print("1. You can now write Python code to add questions to the 'Questions' table.")
        print("2. You can use a tool like DB Browser for SQLite to view the database structure and content.")

    else:
        print("Error! Cannot create the database connection.")