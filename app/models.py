from .extensions import db

# Таблица связи многие-ко-многим
movie_genre = db.Table(
    "movie_genre",
    db.Column("movie_id", db.Integer, db.ForeignKey("movie.id"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("genre.id"), primary_key=True),
)


class Language(db.Model):
    __tablename__ = "language"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    movies = db.relationship("Movie", back_populates="language")


class Genre(db.Model):
    __tablename__ = "genre"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    movies = db.relationship("Movie", secondary=movie_genre, back_populates="genres")


class Movie(db.Model):
    __tablename__ = "movie"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    release_year = db.Column(db.Integer, nullable=False)
    budget = db.Column(db.BigInteger, nullable=False)
    revenue = db.Column(db.BigInteger, nullable=False)
    popularity = db.Column(db.Float, nullable=False)
    vote_average = db.Column(db.Float, nullable=False)
    vote_count = db.Column(db.Integer, nullable=False)
    runtime = db.Column(db.Integer, nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey("language.id"), nullable=False)

    language = db.relationship("Language", back_populates="movies")
    genres = db.relationship("Genre", secondary=movie_genre, back_populates="movies")
