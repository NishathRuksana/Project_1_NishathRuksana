import os
import csv
import psycopg2

# Get the DATABASE_URL from the environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

with open("books.csv", "r") as file:
    reader = csv.reader(file)
    next(reader)  # Skip header
    for isbn, title, author, year in reader:
        cur.execute("INSERT INTO books (isbn, title, author, year) VALUES (%s, %s, %s, %s)",
                    (isbn, title, author, year))

conn.commit()
cur.close()
conn.close()
