import os
import cs50

from cs50 import sql
from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/logout")
def logout():
	session.pop('user', None)
	return render_template("login.html")

@app.route("/register", methods = ["POST", "GET"])
def register(): 
	if request.method == "GET":
		 return render_template("register.html")
	else: 
		username = request.form.get("username")
		password = request.form.get("password")
		if username == "" or password == "":
			return render_template("register.html", message="Please fill out all necessary fields.")

		elif db.execute("SELECT * FROM users WHERE username = :username",
	                          {"username":username}).rowcount == 1:
	    		return render_template("register.html", message="Username already exist")

		else:
			db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
			{"username":username, "password":password})
			db.commit()
			return render_template("login.html")

@app.route("/login", methods = ["POST", "GET"])
def login():
	if request.method == "GET":
		return render_template("login.html")
	else: 
		session.pop('user', None)
		username = request.form.get("username")
		password = request.form.get("password")
		if username is None or password is None:
			return render_template("login.html", message="Please fill out all necessary fields.")
		if db.execute("SELECT * FROM users WHERE username = :username and password = :password",
			{"username":username, "password":password}).rowcount == 1:
			user_ids = db.execute("SELECT id FROM users WHERE username = :username", {"username":username}).fetchone()
			session['user_id'] = user_ids[0]
			return render_template("search.html")
		else: 
			return render_template("login.html", message="Incorrect username or password")

@app.route("/search", methods = ["POST", "GET"])
def search():
	if request.method == "GET":
		return render_template("search.html")
	else: 
		title = request.form.get("title")
		author = request.form.get("author")
		isbn = request.form.get("isbn")
		books = []
		if title == "" and author == "" and isbn == "":
			return render_template("search.html", message="Please enter a keyword or phrase.")
		
		if title:
			books += db.execute("SELECT * FROM books WHERE title iLIKE :title", {"title":"%" + title + "%"}).fetchall()
		if author: 
			books += db.execute("SELECT * FROM books WHERE author iLIKE :author", {"author":"%" + author + "%"}).fetchall()
		if isbn: 
			books += (db.execute("SELECT * FROM books WHERE isbn iLIKE :isbn", {"isbn":isbn}).fetchall())

		if books =="":
			return render_template("results.html", message="No matches")
		else:
			return render_template("results.html", books=books)

@app.route("/book/<isbn>", methods = ["POST", "GET"])
def book(isbn):

	book_id = db.execute("SELECT id FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()[0]

	if request.method == "POST":

		comment = request.form.get('comment')
		rating = int(request.form.get('rating'))
		user_id = session["user_id"]
		

		repeats = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id", {"user_id":user_id, "book_id":book_id}).fetchone()
		if repeats is not None:
			return redirect("/book/" + isbn)
		else:
			db.execute("INSERT INTO reviews (book_id, comment, rating, user_id) VALUES \
				(:book_id, :comment, :rating, :user_id)", { "book_id":book_id, "comment": comment, "rating":rating, "user_id":user_id})
			db.commit()

			return redirect("/book/" + isbn)
	else:		

		book = []
		reviews = []
		book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
		reviews = db.execute("SELECT users.username, comment, rating FROM users INNER JOIN reviews \
			on users.id = reviews.user_id WHERE book_id = :book_id", {"book_id":book_id}).fetchall()

		return render_template("book.html", book=book, reviews=reviews)