import sqlite3
import os


def init_database():
    con = sqlite3.connect('film_break.db')
    con.execute('PRAGMA foreign_keys = ON')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS actors (actor_id INTEGER PRIMARY KEY, actor_name TEXT UNIQUE NOT NULL);')
    cur.execute('CREATE TABLE IF NOT EXISTS directors (director_id INTEGER PRIMARY KEY, director_name TEXT NOT NULL UNIQUE);')
    cur.execute('CREATE TABLE IF NOT EXISTS filmactors (id INTEGER PRIMARY KEY, film_id INTEGER NOT NULL REFERENCES films (film_id), actor_id INTEGER NOT NULL REFERENCES actors (actor_id));')
    cur.execute('CREATE TABLE IF NOT EXISTS filmdirectors (id INTEGER PRIMARY KEY, film_id INTEGER NOT NULL REFERENCES films (film_id), director_id INTEGER NOT NULL REFERENCES directors (director_id));')
    cur.execute('CREATE TABLE IF NOT EXISTS filmgenres (id INTEGER PRIMARY KEY, film_id INTEGER REFERENCES films (film_id), genre_id INTEGER REFERENCES genres (genre_id));')
    cur.execute('CREATE TABLE IF NOT EXISTS films (film_id INTEGER PRIMARY KEY, title TEXT NOT NULL, release_year INTEGER NOT NULL, description TEXT, poster_path TEXT, film_type TEXT NOT NULL, age_rating TEXT);')
    cur.execute('CREATE TABLE IF NOT EXISTS filmscreenwriters (id INTEGER PRIMARY KEY, film_id INTEGER NOT NULL REFERENCES films (film_id), screenwriter_id INTEGER NOT NULL REFERENCES screenwriters (screenwriter_id));')
    cur.execute('CREATE TABLE IF NOT EXISTS genres (genre_id INTEGER PRIMARY KEY, genre_name TEXT UNIQUE NOT NULL);')
    cur.execute('CREATE TABLE IF NOT EXISTS otherfilmpeople (person_id INTEGER PRIMARY KEY, person_name TEXT NOT NULL, profession TEXT NOT NULL);')
    cur.execute('CREATE TABLE IF NOT EXISTS otherpeoplefilms (id INTEGER PRIMARY KEY, person_id INTEGER NOT NULL REFERENCES otherfilmpeople (person_id), film_id INTEGER NOT NULL REFERENCES films (film_id));')
    cur.execute('CREATE TABLE IF NOT EXISTS screenwriters (screenwriter_id INTEGER PRIMARY KEY, screenwriter_name TEXT NOT NULL UNIQUE);')
    cur.execute('CREATE TABLE IF NOT EXISTS userfavoriteactors (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users (user_id), actor_id INTEGER NOT NULL REFERENCES actors (actor_id));')
    cur.execute('CREATE TABLE IF NOT EXISTS userfavoritedirectors (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users (user_id), director_id INTEGER NOT NULL REFERENCES directors (director_id));')
    cur.execute('CREATE TABLE IF NOT EXISTS userfavoritefilms (id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users (user_id), film_id INTEGER REFERENCES films (film_id));')
    cur.execute('CREATE TABLE IF NOT EXISTS userfavoriteotherpeople (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users (user_id), person_id INTEGER NOT NULL REFERENCES otherfilmpeople (person_id));')
    cur.execute('CREATE TABLE IF NOT EXISTS userfavoritescreenwriters (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users (user_id), screenwriter_id INTEGER NOT NULL REFERENCES screenwriters (screenwriter_id));')
    cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT NOT NULL, nickname TEXT NOT NULL UNIQUE, phone TEXT NOT NULL UNIQUE, birth_date TEXT NOT NULL, password_hash TEXT NOT NULL, avatar_path TEXT NOT NULL);')
    cur.execute('CREATE TABLE IF NOT EXISTS watchedfilms (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users (user_id), film_id INTEGER NOT NULL REFERENCES films (film_id), rating INTEGER);')
    cur.execute('CREATE TABLE IF NOT EXISTS watchlist (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users (user_id), film_id INTEGER NOT NULL REFERENCES films (film_id));')
    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_filmactors_unique ON filmactors (film_id, actor_id);')
    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_filmdirectors_unique ON filmdirectors (film_id, director_id);')
    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_filmgenres_unique ON filmgenres (film_id, genre_id);')
    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_filmscreenwriters_unique ON filmscreenwriters (film_id, screenwriter_id);')
    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_otherpeoplefilms_unique ON otherpeoplefilms (person_id, film_id);')
    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_userfavoriteactors_unique ON userfavoriteactors (user_id, actor_id);')
    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_userfavoritedirectors_unique ON userfavoritedirectors (user_id, director_id);')
    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_userfavoritefilms_unique ON userfavoritefilms (user_id, film_id);')
    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_userfavoriteotherpeople_unique ON userfavoriteotherpeople (user_id, person_id);')
    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_userfavoritescreenwriters_unique ON userfavoritescreenwriters (user_id, screenwriter_id);')
    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_watchlist_unique ON watchlist (user_id, film_id);')

    con.commit()
    con.close()

def add():
    con = sqlite3.connect('film_break.db')
    cur = con.cursor()

    for actor in ['Джеки Чан', 'Анджелина Джоли', 'Эмма Уотсон', 'Сергей Бурунов']:
        cur.execute('INSERT OR IGNORE INTO actors (actor_name) VALUES (?)', (actor,))

    for director in ['Кристофер Нолан', 'Квентин Тарантино', 'Грета Гервиг', 'Джеймс Кэмерон']:
        cur.execute('INSERT OR IGNORE INTO directors (director_name) VALUES (?)', (director,))

    for film in [('Fight Club', 1999, 'Фильм о подпольном бойцовском клубе', 'images/fight_club.jpg', 'фильм', '18+'), ('Twilight', 2008, 'История любви вампира и обычной девушки', 'images/twilight.jpg', 'фильм', '18+')]:
        cur.execute('INSERT OR IGNORE INTO films (title, release_year, description, poster_path, film_type, age_rating) VALUES (?, ?, ?, ?, ?, ?)', film)

    for writer in ['Уильям Голдман', 'Квентин Тарантино', 'Акира Куросава', 'Джеймс Кэмерон']:
        cur.execute('INSERT OR IGNORE INTO screenwriters (screenwriter_name) VALUES (?)', (writer,))

    for person in [('Алтия Кром', 'мастер микровязания и художник'), ('Джонни Гринвуд', 'кинокомпозитор')]:
        cur.execute('INSERT OR IGNORE INTO otherfilmpeople (person_name, profession) VALUES (?, ?)', person)

    con.commit()
    con.close()

    