import toml
import sqlite3
import os
import subprocess

# Go
config = toml.load('config.toml')

with sqlite3.connect(config['database']['file']) as conn:
    cursor = conn.cursor()

    cursor.execute('SELECT id, title, longitude, latitude FROM pages WHERE longitude IS NOT NULL AND posted = 0 ORDER BY loaded ASC')
    record = cursor.fetchone()
    print(record)

    cwd = os.path.dirname(os.path.realpath(__file__))
    os.chdir(config['post']['path'])
    command = ['python', 'aerialbot.py', f'-p={record[3]},{record[2]}', '-t', f'{record[1]}\nhttps://en.wikipedia.org/wiki/{record[0]}\n\n{{point_fancy}}']

    try:
        subprocess.run(command)
    except:
        pass

    os.chdir(cwd)

    cursor.execute('UPDATE pages SET posted=1 WHERE id=?', (record[0],))

    # Delete old records with no position info
    cursor.execute('DELETE FROM pages WHERE longitude IS NULL AND loaded < (SELECT loaded FROM pages WHERE id = ?)', (record[0], ))