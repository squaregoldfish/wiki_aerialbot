import sqlite3
import toml


# Here we go
config = toml.load('config.toml')

with sqlite3.connect(config['database']['file']) as conn:
    cursor = conn.cursor()

    finished = False

    while not finished:
        cursor.execute('SELECT COUNT(*) FROM pages WHERE longitude IS NOT NULL AND human_width IS NULL')

        count = cursor.fetchall()[0][0]
        if count == 0:
            finished = True
            continue

        print(cursor.fetchall()[0][0])

        cursor.execute('SELECT id, title, longitude, latitude FROM pages WHERE longitude IS NOT NULL AND human_width IS NULL ORDER BY loaded DESC')
        record = cursor.fetchone()

        if record is None:
            finished = False
            continue

        lon = float(record[2])
        lon_h = 'E' if lon >= 0 else 'W'
        if lon < 0:
            lon = lon * -1

        lat = float(record[3])
        lat_h = 'N' if lat >= 0 else 'S'
        if lat < 0:
            lat = lat * -1

        print()

        url = f'https://en.wikipedia.org/wiki/{record[0]}'
        print(record[1])
        print(url)
        print()
        
        print(f'{lon}{lon_h} {lat}{lat_h}')
        print()

        input_valid = False
        metres = None

        while not input_valid:
            user_input = input("Enter size: ")

            if user_input == 'q':
                input_valid = True
                finished = True
            else:
                try:
                    metres = int(user_input)
                    if metres < 50:
                        metres = 50
                    input_valid = True
                except:
                    pass

        if metres is not None:
            cursor.execute('UPDATE pages SET human_width = ? WHERE id=?', (metres, record[0]))
            conn.commit()

