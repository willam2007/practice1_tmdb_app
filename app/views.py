from flask import Blueprint, render_template
from sqlalchemy import func
from .models import Language, Genre, Movie, movie_genre
from .extensions import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    # --- Таблицы ---

    languages = db.session.query(
        Language.id,
        Language.name.label("Язык"),
    ).select_from(Language)

    genres = db.session.query(
        Genre.id,
        Genre.name.label("Жанр"),
    ).select_from(Genre)

    movies = db.session.query(
        Movie.id,
        Movie.title.label("Название"),
        Movie.release_year.label("Год"),
        Movie.runtime.label("Длительность (мин)"),
        Movie.vote_average.label("Рейтинг"),
        Movie.vote_count.label("Голосов"),
        Movie.popularity.label("Популярность"),
        Language.name.label("Язык"),
    ).join(Language, Movie.language_id == Language.id)

    # --- Запрос 1: Выборка со связанными таблицами, фильтрация и сортировка ---
    # Фильмы с рейтингом выше 8.0, вышедшие после 2000 года, отсортированные по рейтингу
    query1 = (
        db.session.query(
            Movie.title.label("Название"),
            Movie.release_year.label("Год"),
            Movie.vote_average.label("Рейтинг"),
            Language.name.label("Язык"),
        )
        .join(Language, Movie.language_id == Language.id)
        .filter(Movie.vote_average > 8.0, Movie.release_year > 2000)
        .order_by(Movie.vote_average.desc())
    )

    # --- Запрос 2: Вычисление по строкам (прибыль) ---
    # Название, бюджет, сборы и вычисленная прибыль для фильмов с ненулевым бюджетом
    profit = (Movie.revenue - Movie.budget).label("Прибыль")
    query2 = (
        db.session.query(
            Movie.title.label("Название"),
            Movie.release_year.label("Год"),
            Movie.budget.label("Бюджет"),
            Movie.revenue.label("Сборы"),
            profit,
        )
        .filter(Movie.budget > 0, Movie.revenue > 0)
        .order_by(profit.desc())
    )

    # --- Запрос 3: Группировка и агрегатные функции ---
    # Количество фильмов, средний рейтинг и суммарные сборы по жанрам
    query3 = (
        db.session.query(
            Genre.name.label("Жанр"),
            func.count(Movie.id).label("Кол-во фильмов"),
            func.round(func.avg(Movie.vote_average), 2).label("Средний рейтинг"),
            func.max(Movie.vote_average).label("Макс. рейтинг"),
        )
        .join(movie_genre, Genre.id == movie_genre.c.genre_id)
        .join(Movie, Movie.id == movie_genre.c.movie_id)
        .group_by(Genre.name)
        .order_by(func.count(Movie.id).desc())
    )

    # --- Запрос 4: Группировка с фильтрацией по исходным записям и по сгруппированным ---
    # Языки, у которых более 3 фильмов и средний рейтинг выше 7.5
    query4 = (
        db.session.query(
            Language.name.label("Язык"),
            func.count(Movie.id).label("Кол-во фильмов"),
            func.round(func.avg(Movie.vote_average), 2).label("Средний рейтинг"),
            func.round(func.avg(Movie.popularity), 1).label("Средняя популярность"),
        )
        .join(Movie, Movie.language_id == Language.id)
        .filter(Movie.release_year >= 1990)
        .group_by(Language.name)
        .having(
            func.count(Movie.id) > 3,
            func.avg(Movie.vote_average) > 7.5,
        )
        .order_by(func.avg(Movie.vote_average).desc())
    )

    # --- Запрос 5: Вложенный запрос ---
    # Фильмы с рейтингом выше среднего по всей базе
    avg_rating = db.session.query(func.avg(Movie.vote_average)).scalar_subquery()
    query5 = (
        db.session.query(
            Movie.title.label("Название"),
            Movie.release_year.label("Год"),
            Movie.vote_average.label("Рейтинг"),
            Language.name.label("Язык"),
        )
        .join(Language, Movie.language_id == Language.id)
        .filter(Movie.vote_average > avg_rating)
        .order_by(Movie.vote_average.desc())
    )

    return render_template(
        'index.html',
        languages_head=languages.statement.columns.keys(),
        languages_body=languages.all(),
        genres_head=genres.statement.columns.keys(),
        genres_body=genres.all(),
        movies_head=movies.statement.columns.keys(),
        movies_body=movies.all(),
        query1_head=query1.statement.columns.keys(),
        query1_body=query1.all(),
        query2_head=query2.statement.columns.keys(),
        query2_body=query2.all(),
        query3_head=query3.statement.columns.keys(),
        query3_body=query3.all(),
        query4_head=query4.statement.columns.keys(),
        query4_body=query4.all(),
        query5_head=query5.statement.columns.keys(),
        query5_body=query5.all(),
    )
