from flask import Flask, request, jsonify
from flask_cors import CORS
from ytmusicapi import YTMusic
import yt_dlp

# Developed by Supun Dilshan
app = Flask(__name__)
CORS(app) # Web Player එකෙන් Request කරන්න දෙනවා
yt = YTMusic()

@app.route('/')
def home():
    return jsonify({"status": "Supun's Music API is Running 24/7!"})

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Please provide a query"}), 400
    
    try:
        # සින්දුව Search කිරීම
        results = yt.search(query, filter="songs", limit=1)
        if not results:
            return jsonify({"error": "No results found"}), 404
            
        video_id = results[0]['videoId']
        title = results[0]['title']
        
        # ඊළඟට Play වෙන්න සමාන සින්දු හොයාගැනීම
        watch_playlist = yt.get_watch_playlist(videoId=video_id, limit=6)
        related_tracks = [{"id": track['videoId'], "title": track['title']} for track in watch_playlist['tracks'][1:] if 'videoId' in track]

        return jsonify({
            "videoId": video_id,
            "title": title,
            "related": related_tracks
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stream')
def stream():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "No video id provided"}), 400
        
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'skip_download': True,
    }
    
    try:
        # Video ID එකෙන් Direct Audio Link එක ගැනීම
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return jsonify({"url": info['url']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
