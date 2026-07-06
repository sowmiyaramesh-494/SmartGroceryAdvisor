import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root@123",
    database="smart_grocery_advisor"
)

cursor = db.cursor()

print("Database Connected Successfully!")