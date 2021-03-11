

from bs4 import BeautifulSoup
import requests as req

url = "https://en.wikipedia.org/"
billboard_url = "wiki/Billboard_Year-End_Hot_100_singles_of_"
url_genius = 'https://genius.com/'
url_artist = 'artists/'
url_song_end = '-lyrics'

song_genre_table: str = 'song_table'
artist_genre_table: str = 'artist_table'


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

all_data = []  # parsing data of billboard table
artist_check = []  # some coolest mans use different hrefs on the same artist, and this need to dodge it


def request_construct(url_req, class__):
    resp = req.get(url + url_req)
    soup = BeautifulSoup(resp.text, 'lxml')
    title = str(soup.find('title').string).split(' - Wikipedia')[0]
    table = soup.find('table', class_=class__)
    try:
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
    except AttributeError:
        rows = AttributeError
    return rows, title


def get_billboard_data(year):
    rows, current_title = request_construct(billboard_url + str(year), 'wikitable sortable')
    print('Get ' + str(year) + ' year')
    skip = True
    for row in rows:
        # In first iter always row = null
        if skip:
            skip = False
            continue
        url_song = prepare_url_song(row.text)
        all_data_data = {
            'song': {
                'href': [],
                'title': []
            },
            'artist': {
                'href': [],
                'title': []
            },
            'year': year,
            'position': 0,
            'upg_song': url_song
        }
        song_title = True
        for cols in row.find_all('td'):
            # if this's place
            if cols.text.rstrip() in [str(x) for x in (range(1, 101))]:
                all_data_data['position'] = cols.text.rstrip()
                continue
            text_data = []
            href_data = []
            for item in cols.find_all('a'):
                href_data.append(item.get('href'))
                text_data.append(item.text)
            if song_title:
                all_data_data['song']['title'] = text_data
                all_data_data['song']['href'] = href_data
                song_title = False
            else:
                all_data_data['artist']['title'] = text_data
                all_data_data['artist']['href'] = href_data

        # If don't have a link, just add name and error link
        if not all_data_data['song']['title']:
            all_data_data['song']['title'] = [row.find_all('td')[1].text.split('"')[1]]
        if not all_data_data['song']['href']:
            # in this case we just skip that, because at this page no have table
            all_data_data['song']['href'] = ['/wiki/Error/'+all_data_data['song']['title'][0]]
        if not all_data_data['artist']['title']:
            all_data_data['artist']['title'] = row.find_all('td')[2].text.rstrip()
        if not all_data_data['artist']['href']:
            # in this case we just skip that, because at this page no have table
            for all_data_elem in all_data:
                if all_data_elem['artist']['title'] == all_data_data['artist']['title']:
                    all_data_data['artist']['href'] = all_data_elem['artist']['href']
            all_data_data['artist']['href'] = ['/wiki/Error/' + all_data_elem['artist']['title'][0]]
        all_data.append(all_data_data)


def prepare_url_song(data):
    data_ = data.splitlines()
    title = data_[2].replace("'", '')[1:-1]
    title = title.replace("(", '')
    title = title.replace(")", '')
    title = title.replace(",", '')
    title = title.replace("?", '')
    title = title.replace("&", 'and')
    title = '-'.join(title.split())
    try:
        artists = data_[3].split('featuring')[0]
    except:
        artists = data_[2].split('featuring')[0]
    artists = prepare_url_artist(artists)
    url_song = artists+'-'+title
    return url_song


def set_song_and_get_current_true_id(id_step=0) -> int:
    current_song = set_and_get_song(id_step)
    id_song = current_song['id_song']
    return id_song


def set_and_get_song(id_step) -> dict:
    link_song = all_data[id_step]['song']['href'][0]
    title_song = all_data[id_step]['song']['title'][0]

    if link_song not in song_dict.keys():
        rows, current_url = request_construct(link_song, 'infobox')
        if current_url in song_dict.keys():
            current_song = song_dict[current_url]
        else:
            current_song = set_and_get_data_song(rows, link_song, title_song, all_data[id_step]['year'], link_song,
                                                 all_data[id_step]['upg_song'])
    else:
        current_song = song_dict[link_song]
    return current_song


def set_and_get_data_song(rows, link_song, title_song, year, link, upg) -> dict:
    song_data = {
        'id_song': len(song_dict) + 1,
        'title_song': title_song,
        'released_song': str(year),
        'length_song': '',
        'album_song': 'Single',  # if it's not in the album then it is a single
        'image_song': 'https://checkpoint.com.ru/_mod_files/ce_images/eshop/vinyl-logo.png',
        'wiki_link_song': url+link,
        'youtube_link': ''
    }
    # If no have table of song, then we will stay only on the title
    if rows is AttributeError:
        song_dict[link_song] = song_data
        set_genres('', song_data['id_song'], 'no_data')
        return song_data

    for row in rows:
        item = row.text

        if row.find('img') is not None and song_data['image_song'] == 'https://checkpoint.com.ru/_mod_files/ce_images/eshop/vinyl-logo.png':
            song_data['image_song'] = row.find('img').attrs['src']

        elif item[:6] == 'Length':
            try:
                length_data = item[6:]
                length_data_left = length_data.split(':')[0].split()
                length_data_right = length_data.split(':')[1].split()
                length_data = length_data_left[0] + ':' + length_data_right[0][:2]
                song_data['length_song'] = length_data
            except:
                pass

        elif item[:4] == 'from':
            if 'EP' in item and 'album' in item:
                album = item.split('album')[1][1:]
            else:
                album = row.contents[0].contents[1].text
            song_data['album_song'] = album.split('(')[0]

        elif item[:8] == 'Released':
            try:
                released = row.find(class_='plainlist')
                if released is None:
                    released = row.find(class_='published').next

                elif released.find(class_='flagicon') is not None:
                    released = released.find_all('a')[0].next.next
                else:
                    released = released.next
                if len(released.split('(')) > 1:
                    released = released.split('(')[0][:-1]
                released = released.replace(u'\xa0', u' ')
                song_data['released_song'] = date_normalise(released.rstrip(), year)
                continue
                # some strange in the encoding. it's normalisation
            except:
                pass
            try:
                released = item[8:].splitlines()
                if len(released) > 1:
                    released = released[1]
                else:
                    released = released[0]
                if len(released.split('(')) > 1:
                    released = released.split('(')[0][:-1]
                released = released.replace(u'\xa0', u' ')
                song_data['released_song'] = date_normalise(released.rstrip(), year)
                continue
            except:
                released = ''
            song_data['released_song'] = date_normalise(released.rstrip(), year)

        elif item[:5] == 'Genre':
            set_genres(row, song_data['id_song'], song_genre_table)

    img, youtube = request_construct_song_upg(upg)
    if img:
        song_data['image_song'] = img
    if youtube:
        song_data['youtube_link'] = youtube

    song_dict[link_song] = song_data
    return song_data


def request_construct_song_upg(url_req):
    resp = req.get(url_genius + url_req + url_song_end)
    img = False
    youtube = False
    if resp.status_code == 404:
        return img, youtube
    soup = BeautifulSoup(resp.text, 'lxml')
    try:
        img = str(soup).split('&quot;custom_song_art_image_url&quot;:&quot;')[1].split('&quot;')[0]
    except:
        try:
            img = str(soup).split('<img class="SizedImage__NoScript-sc-1hyeaua-1 hYJUSb" src="')[1].split('"')[0]
        except:
            try:
                img = str(soup).split('https://images.genius.com/')[1].split('"')[0]
                img = 'https://images.genius.com/' + img
            except:
                img = False
    try:
        youtube = str(soup).split('http://www.youtube.com/watch?v=')[1].split('&')[0]
        if len(youtube) > 15:
            youtube = youtube.split('\\')[0]
        youtube = 'http://www.youtube.com/watch?v=' + youtube
    except:
        youtube = False
    return img, youtube


def set_artists_and_get_current_true_id(id_step=0) -> list:
    current_artists = set_and_get_artists(id_step)
    current_artists_id = [int(x['id_artist']) for x in current_artists]
    return current_artists_id


def set_and_get_artists(id_step=0, num_art=0, current_artists=None) -> list:
    if current_artists is None:
        current_artists = []
    name_artist = all_data[id_step]['artist']['title'][num_art]
    link_artist = all_data[id_step]['artist']['href'][num_art]

    current_artist = {}

    if link_artist not in artists_dict.keys():
        rows, current_title = request_construct(link_artist, 'infobox')
        if current_title in artist_check:
            for href, artist in artists_dict.items():
                name_low = artist['name_artist'].lower()
                if current_title == 'Lady A':
                    current_title = 'Lady Antebellum'
                elif '(band)' in current_title:
                    current_title = current_title.split(' (band)')[0]
                elif current_title == 'Dr. Hook & the Medicine Show':
                    current_title = 'Dr. Hook'
                elif current_title == 'The Jackson 5':
                    current_title = 'The Jacksons'
                elif current_title == 'The Moody Blues':
                    current_title = 'Moody Blues'
                elif current_title == 'Sly and the Family Stone':
                    current_title = 'Sly & the Family Stone'
                elif current_title == 'Four Tops':
                    current_title = 'The Four Tops'
                elif current_title == 'B. J. Thomas':
                    current_title = 'B.J. Thomas'
                elif current_title == 'Gary Lewis & the Playboys':
                    current_title = 'Gary Lewis and the Playboys'
                elif current_title == "Booker T. & the M.G.'s":
                    current_title = "Booker T & the M.G.'s"
                elif current_title == "Ames Brothers":
                    current_title = "The Ames Brothers"
                elif current_title == "The Pussycat Dolls":
                    current_title = "Pussycat Dolls"
                elif current_title == "KC and the Sunshine Band":
                    current_title = "KC & the Sunshine Band"
                elif current_title == "Paul McCartney and Wings":
                    current_title = "Wings"
                elif current_title == "Nitty Gritty Dirt Band":
                    current_title = "The Dirt Band"
                elif current_title == "Kenny Rogers and The First Edition":
                    current_title = "The First Edition"
                elif current_title == "Skip & Flip":
                    current_title = "Skip and Flip"
                if name_low == name_artist.lower() or name_low == current_title.lower():
                    current_artist = artists_dict[href]
                    break
            if current_artist == {}:
                print(current_title)
                print(artist_check)
                #print(artists_dict)
                raise TimeoutError

        else:
            artist_check.append(current_title)
            current_artist = set_and_get_data_artist(rows, link_artist, name_artist, link_artist)
    else:
        current_artist = artists_dict[link_artist]

    current_artists.append(current_artist)

    # if artist no have genre then we add them from the song
    ids_artists = [x['id_artist'] for x in artist_genre]
    if current_artist['id_artist'] not in ids_artists:
        # id_step+1 == id_song
        set_genres(id_step, current_artist['id_artist'], 'Add genres to artist')

    if len(all_data[id_step]['artist']['href']) > num_art + 1 is not None:
        set_and_get_artists(id_step, num_art + 1, current_artists)
    return current_artists


def set_and_get_data_artist(rows, link_artist, name_artist, link) -> dict:
    artist_data = {
        'id_artist': len(artists_dict) + 1,
        'name_artist': name_artist,
        'age_artist': '0',
        'group_artist': False,
        'image_artist': '',
        'wiki_link_artist': url+link,
        'bio': ''
    }
    # If no have table of artist, then we will stay only on the name
    if rows is AttributeError:
        upg_artist(artist_data, name_artist)
        artists_dict[link_artist] = artist_data
        return artist_data

    for row in rows:
        item = row.text

        if row.find('img') is not None and artist_data['image_artist'] == '':
            artist_data['image_artist'] = row.find('img').attrs['src']

        elif item[:5] == 'Genre' or item[:6] == 'Genres':
            set_genres(row, artist_data['id_artist'], artist_genre_table)

        elif item[:4] == 'Born':
            info = row.contents[1].find(class_='bday')
            if info is not None:
                artist_data['age_artist'] = info.text
        elif item[:4] == 'Died':
            info = item.split('aged')[1]
            info = info.split(')')[0]
            if info is not None:
                info = ''.join(filter(lambda x: x.isdigit(), info))
                artist_data['age_artist'] = '-' + info
            else:
                artist_data['age_artist'] = '-1'
        elif item[:7] == 'Members' or item[:12] == 'Past members':
            artist_data['group_artist'] = True

    if artist_data['group_artist'] and artist_data['image_artist'] == '':
        artist_data['image_artist'] = 'https://www.freepngimg.com/thumb/jazz/41971-9-jazz-musician-image-png-download-free.png'
    elif not artist_data['group_artist'] and artist_data['image_artist'] == '':
        artist_data['image_artist'] = 'https://xazokouti.gr/wp-content/uploads/2018/03/silhouette-man-with-mic-1152212_372467532-e1449107442618.jpg'

    upg_artist(artist_data, name_artist)

    artists_dict[link_artist] = artist_data

    return artist_data


def upg_artist(artist_data, name_artist):
    img, bio = request_construct_artist_upg(name_artist)
    if img:
        artist_data['image_artist'] = img
    if bio:
        artist_data['bio'] = bio


def request_construct_artist_upg(name):
    url_req = prepare_url_artist(name)
    resp = req.get(url_genius + url_artist + url_req)
    img = False
    text_about = False
    if resp.status_code == 404:
        return img, text_about
    soup = BeautifulSoup(resp.text, 'lxml')
    img_ = soup.find('div', class_='user_avatar')
    skip = len(url_req) + 3
    try:
        img = img_.attrs['style'].split('url(')[1][1:-3]
    except:
        pass
    try:
        text_about = soup.text.split('About')[1].split('Popular')[0].rstrip()[skip:]
        if 'Advertise Event Space Privacy Policy Licensing Jobs Developers Terms of Use Copyright Policy' in text_about\
                or '2021 Genius Media Group Inc.' in text_about:
            text_about = False
    except:
        pass
    return img, text_about


def prepare_url_artist(name):
    name = name.replace("'", '')
    name = name.replace(".", '')
    name = name.replace(' +', '')
    name = name.replace('&', ' and ')
    name = name.replace('$', 'S')
    url_name = '-'.join(name.split())
    return url_name


def set_genres(row, id_elem, table_affiliation):
    global artist_genre

    if table_affiliation == 'Add genres to artist':
        link_song = all_data[row]['song']['href']
        if isinstance(link_song, list):
            link_song = link_song[0]
        song_id = song_dict[link_song]['id_song']
        # song_id = 2
        ids_songs = [x['id_song'] for x in song_genre]

        # Can be song and artist have no genres
        if song_id in ids_songs:
            genre_list = [{'id_genre': genre['id_genre'], 'id_artist': id_elem}
                          for genre in song_genre if genre['id_song'] == song_id]
            artist_genre += genre_list
        return
    if table_affiliation == 'no_data':
        href = 'no data'
        title = 'Default genre'
        id_genre = set_genre_and_get_current_true_id(title, href)
        set_genre_dependency(song_genre_table, id_genre, id_elem)
        return

    for link in row.find_all('a'):
        title = link.get('title')
        href = link.get('href')

        # sometimes we have genre announcement
        if title == 'Music genre':
            continue
        # skip some garbage
        if href[:6] != '/wiki/':
            continue

        # i don't know why, but that that is two difference page
        title_checker = title.split('(')
        if len(title_checker) > 1:
            brackets = title_checker[1].split(')')
            brackets = str(brackets[0])
            if 'music' in brackets.lower() or 'genre' in brackets.lower() or 'hip hop' in brackets.lower():
                title = title_checker[0][:-1]

        if href == '/wiki/Hip_hop_music':
            href = '/wiki/Hip_hop'
            title = 'Hip hop'

        # check if have the same genre name, but different links
        for key, value in genre_dict.items():
            if title.lower() in value['name_genre'].lower():
                href = key
                break

        # sometimes somehow registers of letters are different
        href = href.lower()
        id_genre = set_genre_and_get_current_true_id(title, href)
        set_genre_dependency(table_affiliation, id_genre, id_elem)


def set_genre_and_get_current_true_id(title, href):
    if href in genre_dict.keys():
        genre_data = genre_dict[href]
    else:
        genre_data = {
            'id_genre': len(genre_dict) + 1,
            'name_genre': title,
            'image_genre': 'https://cf.girlsaskguys.com/q3140488/0897e277-a395-4ab9-91fb-2436d29a9dff.jpg'
        }
        genre_dict[href] = genre_data
    return genre_data['id_genre']


def set_genre_dependency(table_affiliation, id_genre, id_elem):
    genre_dependency = {
        'id_genre': id_genre,
    }
    if table_affiliation is song_genre_table:
        genre_dependency['id_song'] = id_elem
        song_genre.append(genre_dependency)
    elif table_affiliation is artist_genre_table:
        genre_dependency['id_artist'] = id_elem
        artist_genre.append(genre_dependency)


def set_song_performers(id_song, id_artists):
    for id_artist in id_artists:
        song_performers_data = {'id_song': id_song, 'id_artist': id_artist}
        if song_performers_data not in song_performers:
            song_performers.append(song_performers_data)


def set_billboard(id_step=0, id_song=0):
    billboard_data = {
        'id_song': id_song,
        'position': get_position(id_step),
        'year': all_data[id_step]['year']
    }
    billboard.append(billboard_data)


def get_position(id_step):
    if not int(all_data[id_step]['year']) == 2020:
        return all_data[id_step]['position']
    else:
        return id_step + 1


def main(year_start=2020, year_stop=1946):
    get_billboard_info(year_stop, year_start)
    writing_data(year_start)


def writing_data(year_default):
    year_default = str(year_default)
    for step in range(0, len(all_data)):
        year_current = str(all_data[step]['year'])
        if not year_default == year_current:
            saving_data_pickle()
            print(year_default, 'IS SAVED, CHILL!')
            year_default = year_current
        id_song = set_song_and_get_current_true_id(step)
        id_artist = set_artists_and_get_current_true_id(step)
        set_song_performers(id_song, id_artist)
        set_billboard(step, id_song)
        print(step + 1, ' is added, year:', year_current)
        print(song_dict[all_data[step]['song']['href'][0]])
        for href_art in all_data[step]['artist']['href']:
            try:
                print(artists_dict[href_art])
            except:
                print('Artist is already in dict', all_data[step]['artist'])
        print('len dict ', len(song_dict))
    saving_data_pickle()
    print_all_data()


def do_one_year(year):
    get_billboard_data(year)
    writing_data(year)
    print_all_data()


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


def saving_data_pickle():
    import pickle

    with open('artist_table.pickle', 'wb') as f:
        pickle.dump(artists_dict, f)
    with open('song_table.pickle', 'wb') as f:
        pickle.dump(song_dict, f)
    with open('genre_table.pickle', 'wb') as f:
        pickle.dump(genre_dict, f)

    with open('song_performers.pickle', 'wb') as f:
        pickle.dump(song_performers, f)

    with open('song_genre.pickle', 'wb') as f:
        pickle.dump(song_genre, f)
    with open('artist_genre.pickle', 'wb') as f:
        pickle.dump(artist_genre, f)

    with open('billboard.pickle', 'wb') as f:
        pickle.dump(billboard, f)

    with open('artist_check.pickle', 'wb') as f:
        pickle.dump(artist_check, f)


def get_billboard_info(to_year, from_year=2020):
    for year in range(from_year, to_year - 1, -1):
        get_billboard_data(year)


def load_data_pickle():
    import pickle
    global artists_dict, song_dict, genre_dict, song_performers, artist_genre, song_genre, billboard, artist_check
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

    with open('artist_check.pickle', 'rb') as f:
        artist_check = pickle.load(f)


def date_normalise(date: str, year):
    # 2011
    # September 20, 2011
    nums = list(str(x) for x in range(10))
    if date == '':
        date = str(year)
    date_ = date.split()
    date_new = date
    if date[0] in nums:
        if len(date_) == 3:
            date_new = date_[1] + ' ' + date_[0] + ', ' + date_[2]
        elif len(date_) == 1:
            date_new = date_[0]
    elif len(date_) == 2:
        date_new = date_[0] + ', ' + date_[1]
    elif len(date_) == 1:
        date_new = date_[0] + ', ' + year
    return date_new


def other():
    # get_billboard_data(2018)
    # get_billboard_data(2017)
    # get_billboard_data(1964) 1990
    get_billboard_info(1990)
    writing_data(1990)


def two_elems():
    get_billboard_data(2019)
    print(all_data[13])
    print(all_data[82])
    id_song = set_song_and_get_current_true_id(13)
    id_artist = set_artists_and_get_current_true_id(13)
    set_song_performers(id_song, id_artist)
    set_billboard(13, id_song)
    id_song = set_song_and_get_current_true_id(82)
    id_artist = set_artists_and_get_current_true_id(82)
    set_song_performers(id_song, id_artist)
    set_billboard(82, id_song)
    print_all_data()


def one_elem():
    get_billboard_data(1959)
    id_elem = 84
    print(all_data[id_elem])
    id_song = set_song_and_get_current_true_id(id_elem)
    id_artist = set_artists_and_get_current_true_id(id_elem)
    set_song_performers(id_song, id_artist)
    set_billboard(id_elem, id_song)
    print_all_data()
# //////////////////////////main


#one_elem()
# from datetime import datetime
# print(datetime.strptime('April 16, 2012', '%B %d, %Y'))
# print(date_normalise('/n20 September 2011'))
#other()
load_data_pickle()
#one_elem()
main(1959, 1946)
#saving_data_pickle()
#print_all_data()
# class_ = 'fn'
