from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ---------------------------------------------------
# Author Modell
# ---------------------------------------------------
class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    birth_date = db.Column(db.String(20), nullable=True)
    date_of_death = db.Column(db.String(20), nullable=True)

    # Beziehung zu Book (ein Autor → viele Bücher)
    books = db.relationship("Book", backref="author", lazy=True)

    def __repr__(self):
        return f"<Author {self.id}: {self.name}>"

    def __str__(self):
        return f"{self.name} (geb. {self.birth_date})"


# ---------------------------------------------------
# Book Modell
# ---------------------------------------------------
class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)

    # Foreign Key → verweist auf Author.id
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)

    def __repr__(self):
        return f"<Book {self.id}: {self.title}>"

    def __str__(self):
        return f"{self.title} ({self.publication_year})"