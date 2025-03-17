import mysql.connector
import re

# Establish MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Changepa$$06",
    database="betting_db"
)
cursor = conn.cursor()

# Function to clean the table name (remove sp_ or msw_ prefixes)
def clean_table_name(table_name):
    return re.sub(r'^(msw_|sp_)', '', table_name)

# Fetch all table names from the database
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

# Initialize sets to hold the `sp_*` and `msw_*` tables
sp_tables = set()
msw_tables = set()

# Loop through the tables and add to the appropriate set
for table in tables:
    table_name = table[0]

    if 'sp_' in table_name:
        sp_tables.add(clean_table_name(table_name))  # Add cleaned table name without 'sp_'
    elif 'msw_' in table_name:
        msw_tables.add(clean_table_name(table_name))  # Add cleaned table name without 'msw_'

# Find the intersection of sp_tables and msw_tables to get the common cleaned names
common_tables = sp_tables.intersection(msw_tables)

# Loop through common table names and create the new scraped_ table (empty)
for table in common_tables:
    new_table_name = f"scraped_{table}"

    # Create an empty table with the same structure as the common tables
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS `{new_table_name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        bet_name VARCHAR(255),
        team1 VARCHAR(100),
        sp_odds1 DECIMAL(10, 2),
        msw_odds1 DECIMAL(10, 2),
        team2 VARCHAR(100),
        sp_odds2 DECIMAL(10, 2),
        msw_odds2 DECIMAL(10, 2),
        team3 VARCHAR(100) NULL,
        sp_odds3 DECIMAL(10, 2) NULL,
        msw_odds3 DECIMAL(10, 2) NULL
    );
    """
    cursor.execute(create_table_sql)
    print(f"Table `{new_table_name}` created successfully (empty).")

# Commit changes and close the connection
conn.commit()
cursor.close()
conn.close()
