# data tables
artists_dict = {}  # artist table
song_dict = {}  # song table
genre_dict = {}  # genre table
# dependency tables
song_performers = []
song_genre = []
artist_genre = []
# billboard table
billboard = []


def load_data_pickle():
    import pickle
    global artists_dict, song_dict, genre_dict, song_performers, artist_genre, song_genre, billboard
    with open('artist_table.pickle', 'rb') as f:
        artists_dict = pickle.load(f)
    with open('song_table.pickle', 'rb') as f:
        song_dict = pickle.load(f)
    with open('genre_table.pickle', 'rb') as f:
        genre_dict = pickle.load(f)

    with open('song_performers.pickle', 'rb') as f:
        song_performers = pickle.load(f)

    with open('song_genre.pickle', 'rb') as f:
        song_genre = pickle.load(f)
    with open('artist_genre.pickle', 'rb') as f:
        artist_genre = pickle.load(f)

    with open('billboard.pickle', 'rb') as f:
        billboard = pickle.load(f)


def print_all_data():
    print('Songs:')
    print(song_dict)
    print('Artists:')
    print(artists_dict)
    print('Genres:')
    print(genre_dict)
    print('song_genre:')
    print(song_genre)
    print('artist_genre:')
    print(artist_genre)
    print('song_performers:')
    print(song_performers)
    print('billboard:')
    print(billboard)


# /////////////////////DB


load_data_pickle()

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    # Подключение к существующей базе данных
    connection = psycopg2.connect(user="postgres",
                                  database="billboard_data",
                                  # пароль, который указали при установке PostgreSQL
                                  password="admin",
                                  host="127.0.0.1",
                                  port="5432")
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    # Курсор для выполнения операций с базой данных
    cursor = connection.cursor()
except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)

'''
def add_song_data():
    for song in song_dict.values():
        # if not song['id_song'] == 66:
        #    continue
        title_song = str(clear_data(song['title_song']))
        released_song = str(clear_data(song['released_song']))
        length_song = str(clear_data(song['length_song']))
        album_song = str(clear_data(song['album_song']))
        values = str(song['id_song']) + ", '" + title_song + "', " + released_song + ", " \
                 + length_song + ", '" + album_song + "'"
        insert_query = "INSERT INTO song (id_song, title_song, released_song, length_song, album_song) VALUES (" + values + ")"
        print(insert_query)
        cursor.execute(insert_query)
        connection.commit()
'''


def add_data(data__, name_table):
    if isinstance(data__, dict):
        data_ = data__.values()
    elif isinstance(data__, list):
        data_ = data__
    else:
        data_ = ''
    for data in data_:
        insert_query_keys = ''
        insert_query_value = ''
        id_check = True
        for key, value in data.items():
            insert_query_keys += str(key) + ','
            if id_check:
                id_check = False
                insert_query_value += clear_data(value) + ','
                continue
            if key == 'bio':
                insert_query_value += '\'\'\'' + clear_bio(value) + '\'\'\','
            else:
                insert_query_value += '\'' + (clear_data(value))+'\','

        insert_query = "INSERT INTO " + name_table + " (" + insert_query_keys[:-1] + ") VALUES (" + insert_query_value[:-1] + ")"
        print(insert_query)
        cursor.execute(insert_query)
        connection.commit()


def clear_bio(bio: str):
    bio = bio.replace("'",'"')
    return bio


def clear_data(data):

    if isinstance(data, bool) or isinstance(data, int):
        return str(data)
    value = data.split('\'')
    new_data = ''
    if len(value) > 1:
        for elem in range(len(value)):
            if len(value)-1 == elem:
                new_data += value[elem]
            else:
                new_data += value[elem] + '\'\''
    else:
        new_data = data
    new_data = new_data.split('\n')
    if len(new_data) > 1:
        new_data = str(new_data[1])
    else:
        new_data = str(new_data[0])
    return new_data


def info_bd():
    cursor.execute("SELECT * from artist")
    print("artist", cursor.fetchall())
    cursor.execute("SELECT * from song")
    print("song", cursor.fetchall())
    cursor.execute("SELECT * from genre")
    print("genre", cursor.fetchall())
    cursor.execute("SELECT * from billboard")
    print("billboard", cursor.fetchall())
    cursor.execute("SELECT * from song_genre")
    print("song_genre", cursor.fetchall())
    cursor.execute("SELECT * from artist_genre")
    print("artist_genre", cursor.fetchall())
    cursor.execute("SELECT * from song_performers")
    print("song_performers", cursor.fetchall())


def del_bd(name_table):
    delete_query = "Delete from " + name_table + " *"
    cursor.execute(delete_query)
    connection.commit()


def del_all():
    del_bd('song_performers')
    del_bd('artist_genre')
    del_bd('song_genre')
    del_bd('billboard')
    del_bd('artist')
    del_bd('song')
    del_bd('genre')


def add_all():
    add_data(artists_dict, 'artist')
    add_data(song_dict, 'song')
    add_data(genre_dict, 'genre')
    add_data(billboard, 'billboard')
    add_data(song_performers, 'song_performers')
    add_data(artist_genre, 'artist_genre')
    add_data(song_genre, 'song_genre')


del_all()
add_all()
info_bd()
