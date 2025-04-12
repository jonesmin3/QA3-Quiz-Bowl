import sqlite3
import os

# --- Configuration ---
DATABASE_FILE = 'quiz_bowl_app.db'

# --- Database Functions ---
def create_connection(db_file):
    """ Create a database connection to the SQLite database specified by db_file """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        # Optional: print(f"SQLite connection established to {db_file}")
        # Enable foreign key constraint enforcement (good practice, though less critical for reading)
        # conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database '{db_file}': {e}")
        return None

def display_table_data(conn, table_name):
    """ Fetches and prints all data from a specified table """
    print(f"\n{'='*15} Data from table: {table_name} {'='*15}")
    cursor = conn.cursor()
    try:
        # Select all data from the table
        cursor.execute(f"SELECT * FROM {table_name}") # Safe here as table_name is controlled by us

        # Fetch column names from cursor description
        column_names = [description[0] for description in cursor.description]
        print(f"Columns: {column_names}")
        print("-" * (len(str(column_names)) - 2)) # Print a separator line

        # Fetch all rows
        rows = cursor.fetchall()

        if not rows:
            print(f"Table '{table_name}' is empty.")
        else:
            # Print each row
            for row in rows:
                print(row)
            print(f"\nTotal rows in '{table_name}': {len(rows)}")

    except sqlite3.Error as e:
        print(f"Error reading from table '{table_name}': {e}")
    finally:
        # No need to close cursor explicitly when connection is closed later
        pass
    print(f"{'='* (32 + len(table_name))}")


# --- Main Execution ---
if __name__ == '__main__':
    print(f"Attempting to read data from: {DATABASE_FILE}")

    # Check if the database file exists
    if not os.path.exists(DATABASE_FILE):
        print(f"Error: Database file '{DATABASE_FILE}' not found.")
        print("Please ensure the database exists and the script is in the correct directory.")
    else:
        conn = create_connection(DATABASE_FILE)

        if conn:
            try:
                # Display data from the Topics table
                display_table_data(conn, "Topics")

                # Display data from the Questions table
                display_table_data(conn, "Questions")

            except Exception as e:
                print(f"An unexpected error occurred: {e}")
            finally:
                # Ensure the connection is always closed
                print("\nClosing database connection.")
                conn.close()
        else:
            print("Could not establish database connection. Aborting.")