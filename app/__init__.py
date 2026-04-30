import os
from flask import Flask
from .extensions import db
from .models import Language, Genre, Movie


def create_app():
    app = Flask(__name__, instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'))

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'tmdb.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .views import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()
        _seed_data()

    return app


def _seed_data():
    if Language.query.first():
        return

    from .seed import load_data
    import pandas as pd

    df = load_data()

    lang_map = {}
    genre_map = {}

    for _, row in df.iterrows():
        # Язык
        lang_name = str(row['original_language'])
        if lang_name not in lang_map:
            lang = Language(name=lang_name)
            db.session.add(lang)
            lang_map[lang_name] = lang

        # Жанры
        for genre_name in str(row['genres']).split(','):
            genre_name = genre_name.strip()
            if genre_name and genre_name not in genre_map:
                genre = Genre(name=genre_name)
                db.session.add(genre)
                genre_map[genre_name] = genre

    db.session.flush()

    for _, row in df.iterrows():
        lang_name = str(row['original_language'])
        movie = Movie(
            title=str(row['title']),
            release_year=int(row['release_year']),
            budget=int(row['budget']),
            revenue=int(row['revenue']),
            popularity=float(row['popularity']),
            vote_average=float(row['vote_average']),
            vote_count=int(row['vote_count']),
            runtime=int(row['runtime']),
            language=lang_map[lang_name],
        )
        for genre_name in str(row['genres']).split(','):
            genre_name = genre_name.strip()
            if genre_name in genre_map:
                movie.genres.append(genre_map[genre_name])
        db.session.add(movie)

    db.session.commit()