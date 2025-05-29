from flask import Flask, request, jsonify, send_from_directory, render_template_string
import sqlite3
import os
from werkzeug.security import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'songs'

# Ensure the songs folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# HTML Template
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Spotify Clone</title>
    <style>
        body {
            background-color: #121212;
            color: white;
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        .player {
            max-width: 700px;
            margin: auto;
        }
        audio {
            width: 100%;
            margin-top: 10px;
        }
        form {
            margin-bottom: 20px;
        }
        input, button {
            margin: 5px 0;
            padding: 10px;
            width: 100%;
            box-sizing: border-box;
        }
        .song-item {
            margin-bottom: 20px;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="player">
        <h1>🎵 Spotify Clone</h1>

        <form action="/add_song" method="post" enctype="multipart/form-data">
            <input type="text" name="title" placeholder="Song Title" required>
            <input type="text" name="artist" placeholder="Artist" required>
            <input type="file" name="file" accept="audio/*" required>
            <button type="submit">Upload Song</button>
        </form>

        <h2>Music Library</h2>
        <div id="song-list">Loading songs...</div>
    </div>

    <script>
        async function loadSongs() {
            const response = await fetch('/songs');
            const songs = await response.json();
            const list = document.getElementById('song-list');
            list.innerHTML = '';
            songs.forEach(song => {
                const item = document.createElement('div');
                item.className = 'song-item';
                item.innerHTML = `
                    <p><strong>${song[1]}</strong> by ${song[2]}</p>
                    <audio controls src="/play/${song[3]}"></audio>
                `;
                list.appendChild(item);
            });
        }

        window.onload = loadSongs;
    </script>
</body>
</html>
'''

# Initialize the database
def init_db():
    with sqlite3.connect('songs.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS songs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            artist TEXT NOT NULL,
                            filename TEXT NOT NULL UNIQUE)''')
        conn.commit()

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/songs')
def get_songs():
    with sqlite3.connect('songs.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM songs')
        songs = cursor.fetchall()
    return jsonify(songs)

@app.route('/add_song', methods=['POST'])
def add_song():
    title = request.form['title']
    artist = request.form['artist']
    file = request.files['file']
    filename = secure_filename(file.filename)

    # Save file to disk
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Insert song record into DB
    try:
        with sqlite3.connect('songs.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO songs (title, artist, filename) VALUES (?, ?, ?)",
                        (title, artist, filename))
            conn.commit()
    except sqlite3.IntegrityError:
        pass  # If the song already exists, do nothing

    return ('<script>window.location.href = "/";</script>')

@app.route('/play/<filename>')
def play(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
