# application.py
from functools import wraps
import os
import logging
from flask import Flask, session, render_template, request, redirect, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import QueuePool
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database configuration section
engine = create_engine(
    os.getenv("DATABASE_URL"),
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=300,  # Recycle connections every 5 minutes
    pool_pre_ping=True,  # Enable connection health checks
    poolclass=QueuePool  # Use queue pooling for better connection management
)

db = scoped_session(sessionmaker(bind=engine))

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Remove database session after request completion"""
    db.remove()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    """Landing page"""
    if "user_id" in session:
        user = db.execute(
            text("SELECT username FROM users WHERE id = :user_id"),
            {"user_id": session["user_id"]}
        ).fetchone()
        return render_template("index.html", username=user.username if user else None)
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("register"))

        try:
            if db.execute(
                text("SELECT id FROM users WHERE username = :username"),
                {"username": username}
            ).fetchone():
                flash("Username already exists.", "danger")
                return redirect(url_for("register"))

            db.execute(
                text("INSERT INTO users (username, password) VALUES (:username, :password)"),
                {"username": username, "password": generate_password_hash(password)}
            )
            db.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            db.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash("Registration failed. Please try again.", "danger")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        try:
            user = db.execute(
                text("SELECT * FROM users WHERE username = :username"),
                {"username": username}
            ).fetchone()

            if user and check_password_hash(user.password, password):
                session["user_id"] = user.id
                flash(f"Welcome back, {username}!", "success")
                return redirect(url_for("index"))
            else:
                flash("Invalid username or password.", "danger")

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash("Login failed. Please try again.", "danger")

    return render_template("login.html")

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Book search"""
    if request.method == "POST":
        search_query = request.form.get("query", "").strip()
        search_type = request.form.get("search_type", "all")

        if not search_query:
            flash("Please enter a search term.", "warning")
            return redirect(url_for("search"))

        query_map = {
            "isbn": "isbn ILIKE :query",
            "title": "title ILIKE :query",
            "author": "author ILIKE :query",
            "all": "isbn ILIKE :query OR title ILIKE :query OR author ILIKE :query"
        }

        try:
            books = db.execute(
                text(f"SELECT * FROM books WHERE {query_map[search_type]}"),
                {"query": f"%{search_query}%"}
            ).fetchall()
            return render_template("search.html", books=books, search_query=search_query)

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            flash("Search failed. Please try again.", "danger")
            db.rollback()

    return render_template("search.html")

@app.route("/book/<isbn>")
@login_required
def book(isbn):
    """Book details and reviews"""
    try:
        book = db.execute(
            text("SELECT * FROM books WHERE isbn = :isbn"),
            {"isbn": isbn}
        ).fetchone()

        if not book:
            flash("Book not found.", "warning")
            return redirect(url_for("search"))

        reviews = db.execute(
            text("""
                SELECT r.*, u.username 
                FROM reviews r 
                JOIN users u ON r.user_id = u.id 
                WHERE r.book_id = :book_id 
                ORDER BY r.reviewed_at DESC
            """),
            {"book_id": book.id}
        ).fetchall()

        user_review = db.execute(
            text("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id"),
            {"user_id": session["user_id"], "book_id": book.id}
        ).fetchone()

        return render_template("book.html", book=book, reviews=reviews, user_review=user_review)

    except Exception as e:
        logger.error(f"Book page error: {str(e)}")
        flash("Error loading book details.", "danger")
        db.rollback()
        return redirect(url_for("search"))

@app.route("/submit-review", methods=["POST"])
@login_required
def submit_review():
    """Submit book review"""
    isbn = request.form.get("isbn")
    rating = request.form.get("rating")
    review_text = request.form.get("review", "").strip()

    if not all([isbn, rating, review_text]):
        flash("All fields are required.", "danger")
        return redirect(url_for("book", isbn=isbn))

    try:
        rating = int(rating)
        if not 1 <= rating <= 5:
            raise ValueError("Invalid rating")

        book = db.execute(
            text("SELECT id FROM books WHERE isbn = :isbn"),
            {"isbn": isbn}
        ).fetchone()

        if not book:
            flash("Book not found.", "danger")
            return redirect(url_for("search"))

        existing_review = db.execute(
            text("SELECT id FROM reviews WHERE user_id = :user_id AND book_id = :book_id"),
            {"user_id": session["user_id"], "book_id": book.id}
        ).fetchone()

        if existing_review:
            flash("You have already reviewed this book.", "warning")
            return redirect(url_for("book", isbn=isbn))

        db.execute(
            text("""
                INSERT INTO reviews (user_id, book_id, rating, review, reviewed_at)
                VALUES (:user_id, :book_id, :rating, :review, CURRENT_TIMESTAMP)
            """),
            {
                "user_id": session["user_id"],
                "book_id": book.id,
                "rating": rating,
                "review": review_text
            }
        )
        db.commit()
        flash("Review submitted successfully!", "success")

    except ValueError:
        flash("Invalid rating value.", "danger")
    except Exception as e:
        db.rollback()
        logger.error(f"Review submission error: {str(e)}")
        flash("Error submitting review.", "danger")

    return redirect(url_for("book", isbn=isbn))

@app.route("/logout")
@login_required
def logout():
    """User logout"""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)