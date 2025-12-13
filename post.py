import toml
import sqlite3
import os
import subprocess

# Go
config = toml.load('config.toml')

with sqlite3.connect(config['database']['file']) as conn:
    cursor = conn.cursor()

    cursor.execute('SELECT id, title, longitude, latitude, human_width FROM pages WHERE longitude IS NOT NULL AND human_width IS NOT NULL AND posted = 0 AND loaded >= datetime("now", "-7 days") ORDER BY RANDOM()')
    record = cursor.fetchone()

    if record is None:
        cursor.execute('SELECT id, title, longitude, latitude, human_width FROM pages WHERE longitude IS NOT NULL AND human_width IS NOT NULL AND posted = 0 ORDER BY RANDOM()')
        record = cursor.fetchone()

    print(record)

    if record is not None:
            cwd = os.path.dirname(os.path.realpath(__file__))
            os.chdir(config['post']['path'])
            command = ['python', 'aerialbot.py', f'-p={record[3]},{record[2]}', '-t', f'{record[1]}\nhttps://en.wikipedia.org/wiki/{record[0]}\n\n{{point_fancy}}']

            width = None
            if record[4] is not None:
                width = record[4]

            if width is not None:
                command = command + [f'-w={width}', f'-h={width}']

            try:
                subprocess.run(command)
            except:
                pass

            os.chdir(cwd)

            cursor.execute('UPDATE pages SET posted=1 WHERE id=?', (record[0],))

    # Delete old records with no position info
    cursor.execute('DELETE FROM pages WHERE longitude IS NULL AND loaded < (SELECT loaded FROM pages WHERE id = ?)', (record[0], ))
