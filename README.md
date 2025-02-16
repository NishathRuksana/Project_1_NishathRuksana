# Project 1 ENGO 651

# Book Search Web Application

This is a web application that allows users to search for books and view details and also add reviews about them. It is built using Flask and follows an MVC-like structure.

# Project Structure


📂 static/                  
 ├── styles.css            
📂 templates/               
 ├── base.html             
 ├── book.html             
 ├── index.html            
 ├── login.html            
 ├── register.html         
 ├── search.html           
📄 application.py           
📄 books.csv                
📄 import.py                
📄 requirements.txt         
📄 README.md                


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



