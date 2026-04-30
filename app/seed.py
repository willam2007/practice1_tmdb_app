import pandas as pd

CSV_PATH = '/home/willam/.cache/kagglehub/datasets/asaniczka/tmdb-movies-dataset-2023-930k-movies/versions/921/TMDB_movie_dataset_v11.csv'


def load_data():
    df = pd.read_csv(CSV_PATH)

    # Фильтруем: только вышедшие фильмы с известными данными
    df = df[df['status'] == 'Released']
    df = df[df['vote_count'] > 500]
    df = df[df['runtime'] > 0]
    df = df[df['genres'].notna()]
    df = df[df['original_language'].notna()]
    df = df[df['release_date'].notna()]

    # Берём топ 200 по количеству голосов
    df = df.sort_values('vote_count', ascending=False).head(200)

    # Год из release_date
    df['release_year'] = pd.to_datetime(df['release_date']).dt.year

    return df