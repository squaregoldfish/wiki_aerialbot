import sqlite3
import toml

def process_metres(conn, cursor, id, input):
    result = False

    metres = None

    try:
        metres = int(input)
        if metres < 50:
            metres = 50
        result = True
    except:
        pass

    if metres is not None:
        cursor.execute('UPDATE pages SET human_width = ? WHERE id = ?', (metres, id))
        conn.commit()

    return result

def get_float(prompt):
    
    result = None
    valid = False
    
    while not valid:
        float_input = input(f'{prompt}: ')
        try:
            result = float(float_input)
            valid = True
        except:
            pass

    return result


def update_coordinates(conn, cursor, id):
    print()
    north = get_float("North")
    east = get_float("East")

    cursor.execute('UPDATE pages SET longitude = ?, latitude = ? WHERE id = ?', (east, north, id))

# Here we go
config = toml.load('config.toml')

with sqlite3.connect(config['database']['file']) as conn:
    cursor = conn.cursor()

    # Print preamble information
    cursor.execute('SELECT COUNT(*) FROM pages WHERE human_width IS NOT NULL AND posted = 0')
    records = cursor.fetchone()
    print(f'Unposted articles: {records[0]}')

    cursor.execute('SELECT loaded FROM pages WHERE human_width IS NOT NULL AND posted = 0 ORDER BY loaded ASC LIMIT 1')
    records = cursor.fetchone()
    print(f'Earliest unposted article: {records[0]}')

    print('\n')


    finished = False

    while not finished:
        cursor.execute('SELECT COUNT(*) FROM pages WHERE longitude IS NOT NULL AND human_width IS NULL ORDER BY loaded ASC')

        records = cursor.fetchall()

        if records is None:
            finished = True
            continue
        
        count = records[0][0]
        if count == 0:
            finished = True
            continue

        print(count)

        cursor.execute('SELECT id, title, longitude, latitude, loaded FROM pages WHERE longitude IS NOT NULL AND human_width IS NULL ORDER BY loaded ASC')
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

        print(record[4])
        url = f'https://en.wikipedia.org/wiki/{record[0]}'
        print(record[1])
        print(url)
        print()
        
        print(f'{lon}{lon_h} {lat}{lat_h}')


        input_valid = False

        while not input_valid:
            print()
            user_input = input("Enter size: ")

            if user_input == 'q':
                input_valid = True
                finished = True
            elif user_input == 'd':
                cursor.execute('DELETE FROM pages WHERE id = ?', (record[0], ))
                conn.commit()
                input_valid = True
            elif user_input == 'c':
                # Don't set the input as valid. That way, when we come back
                # we'll be asked for the size again.
                update_coordinates(conn, cursor, record[0])
            else:
                input_valid = process_metres(conn, cursor, record[0], user_input)


