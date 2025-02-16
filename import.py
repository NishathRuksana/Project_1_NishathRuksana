import os
import csv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import QueuePool

# Database configuration with connection pooling
engine = create_engine(
    os.getenv("DATABASE_URL"),
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=300,  # Reduced to match application.py
    pool_pre_ping=True,  # Added for consistency with application.py
    poolclass=QueuePool  # Added for explicit pool configuration
)
db = scoped_session(sessionmaker(bind=engine))

def import_books():
    try:
        # First verify if books table has data
        result = db.execute(text("SELECT COUNT(*) FROM books")).scalar()

        if result > 0:
            print("Books table already contains data. Proceeding with upsert operation.")

        # Read and import books from CSV
        with open("attached_assets/books.csv", "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row

            count = 0
            for isbn, title, author, year in reader:
                try:
                    db.execute(
                        text("""
                            INSERT INTO books (isbn, title, author, year) 
                            VALUES (:isbn, :title, :author, :year)
                            ON CONFLICT (isbn) DO NOTHING
                        """),
                        {"isbn": isbn, "title": title, "author": author, "year": int(year)}
                    )
                    count += 1
                    if count % 100 == 0:  # Print progress every 100 records
                        print(f"Processed {count} books...")
                        db.commit()  # Commit in batches
                except Exception as row_error:
                    print(f"Error importing row with ISBN {isbn}: {str(row_error)}")
                    continue

            db.commit()  # Final commit for remaining records
            print(f"Successfully imported/updated {count} books.")

    except Exception as e:
        db.rollback()
        print(f"Error importing books: {str(e)}")
    finally:
        db.remove()

if __name__ == "__main__":
    import_books()