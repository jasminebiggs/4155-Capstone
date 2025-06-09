import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="your_mysql_username",
        password="your_mysql_password",
        database="your_database_name"
    )

def test_connection():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 'MySQL connection successful!'")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0]
