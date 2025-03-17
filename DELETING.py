import mysql.connector

# MySQL connection details
DB_HOST = "localhost"  # Change if using a remote database
DB_USER = "root"  # Change to your MySQL username
DB_PASSWORD = "Changepa$$06"  # Change to your MySQL password
DB_NAME = "betting_db"  # Change to your database name

# Connect to MySQL
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = conn.cursor()

# Disable foreign key checks (to prevent issues with constraints)
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

# Fetch all table names
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = %s;", (DB_NAME,))
tables = cursor.fetchall()

# Drop all tables
for (table_name,) in tables:
    drop_query = f"DROP TABLE IF EXISTS `{table_name}`;"
    print(f"Dropping table: {table_name}")
    cursor.execute(drop_query)

# Re-enable foreign key checks
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

# Commit and close the connection
conn.commit()
cursor.close()
conn.close()

print("✅ All tables deleted successfully!")

conn.commit()
cursor.close()
conn.close()

print("✅ All tables deleted successfully!")
