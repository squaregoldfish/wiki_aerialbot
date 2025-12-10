import socket
import toml
import sqlite3

def get_size_count(db_file):
    try:
        with sqlite3.connect(db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM pages WHERE longitude IS NOT NULL AND human_width IS NULL')
                records = cursor.fetchall()
                return records[0][0]
    except:
        return None

def start_server(port, db_file):
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Bind the socket to the address and port
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen()  # Enable the server to accept connections

        while True:
            # Wait for a connection
            conn, addr = server_socket.accept()
            with conn:
                response = f'{get_size_count(db_file)}'
                conn.sendall(response.encode('utf-8'))

if __name__ == "__main__":
    with open('config.toml') as f:
        config = toml.load(f)

    start_server(config['size_server']['port'], config['database']['file'])

