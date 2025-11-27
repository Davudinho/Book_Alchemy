from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
import os
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

# ---------------------------------------------------
# Environment-Variablen laden
# ---------------------------------------------------
load_dotenv()

app = Flask(__name__)

# SECRET_KEY aus .env
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")

# API-KEY aus .env
API_KEY = os.getenv("API_KEY")

# ---------------------------------------------------
# Datenbank Konfiguration
# ---------------------------------------------------
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# ---------------------------------------------------
# Startseite
# ---------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    query = request.args.get("q")
    sort_by = request.args.get("sort", "title")

    books_query = Book.query

    # Suche
    if query:
        books_query = books_query.filter(Book.title.like(f"%{query}%"))

    # Sortierung
    if sort_by == "author":
        books_query = books_query.join(Author).order_by(Author.name.asc())
    else:
        books_query = books_query.order_by(Book.title.asc())

    books = books_query.all()

    return render_template(
        "home.html",
        books=books,
        sort_by=sort_by,
        query=query
    )


# ---------------------------------------------------
# Autor hinzufügen
# ---------------------------------------------------
@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form.get("name")
        birth_date = request.form.get("birth_date")
        date_of_death = request.form.get("date_of_death")

        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )

        try:
            db.session.add(new_author)
            db.session.commit()
            flash("Author added successfully!", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Database error: {str(e)}", "danger")

        return render_template("add_author.html", success=True)

    return render_template("add_author.html", success=False)


# ---------------------------------------------------
# Buch hinzufügen
# ---------------------------------------------------
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    authors = Author.query.order_by(Author.name).all()

    if request.method == "POST":
        isbn = request.form.get("isbn")
        title = request.form.get("title")
        publication_year = request.form.get("publication_year")
        author_id = request.form.get("author_id")

        new_book = Book(
            isbn=isbn,
            title=title,
            publication_year=publication_year,
            author_id=author_id
        )

        try:
            db.session.add(new_book)
            db.session.commit()
            flash("Book added successfully!", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Database error: {str(e)}", "danger")

        return render_template("add_book.html", authors=authors, success=True)

    return render_template("add_book.html", authors=authors, success=False)


# ---------------------------------------------------
# Buch löschen (inkl. Autor, wenn leer)
# ---------------------------------------------------
@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author

    try:
        db.session.delete(book)
        db.session.commit()

        # Falls Autor danach keine Bücher mehr hat → löschen
        if len(author.books) == 0:
            db.session.delete(author)
            db.session.commit()
            flash(f"Book and author '{author.name}' deleted.", "success")
        else:
            flash(f"Book '{book.title}' deleted.", "success")

    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Error deleting book: {str(e)}", "danger")

    return redirect(url_for("home"))


# ---------------------------------------------------
# Tabellen initialisieren
# ---------------------------------------------------
if __name__ == "__main__":
    # Falls du einmalig Tabellen erstellen willst:
    # with app.app_context():
    #     db.create_all()

    app.run(debug=True)
