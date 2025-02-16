# Project 1 ENGO 651

# Book Search Web Application

This is a web application that allows users to search for books and view details and also add reviews about them. It is built using Flask and follows an MVC-like structure.

# Project Structure


📂 static/                  # Static files (CSS, JavaScript, images)
 ├── styles.css            # Main stylesheet for the project
📂 templates/               # HTML templates
 ├── base.html             # Base template for layout inheritance
 ├── book.html             # Book details page
 ├── index.html            # Home page
 ├── login.html            # User login page
 ├── register.html         # User registration page
 ├── search.html           # Book search page
📄 application.py           # Main Flask application
📄 books.csv                # Dataset containing book information
📄 import.py                # Script to import book data
📄 requirements.txt         # Dependencies for the project
📄 README.md                # Project documentation


 # Features

- User authentication (Login/Register)
- Search for books by title, author, or ISBN
- View book details
- Import book data from `books.csv`

# Installation

# Prerequisites

- Python 3.x
- Flask

# Setup Instructions

1. Clone this repository:
   
   git clone <repository-url>
   cd <project-folder>
   

2. Install dependencies:
   
   pip install -r requirements.txt
   

3. Import book data:
  
   python import.py
   

4. Run the application:
   
   flask run


5. Open your browser and go to:
   
   http://127.0.0.1:5000/



