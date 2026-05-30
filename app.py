from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import tempfile
import uuid
import time

app = Flask(__name__)

# Usar /tmp en Render (ephemeral pero funciona)
TEMP_DIR = '/tmp/downloads'

def limpiar_viejos():
    try:
        if not os.path.exists(TEMP_DIR):
            return
        for f in os.listdir(TEMP_DIR):
            path = os.path.join(TEMP_DIR, f)
            if os.path.isfile(path) and time.time() - os.path.getmtime(path) > 1800:
                os.remove(path)
    except:
        pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/descargar', methods=['POST'])
def descargar():
    url = request.form.get('url')
    tipo = request.form.get('tipo', 'video')
    
    if not url:
        return "URL requerida", 400
    
    limpiar_viejos()
    
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    
    session_id = str(uuid.uuid4())[:8]
    
    try:
        opciones = {
            'format': 'bestaudio/best' if tipo == 'audio' else 'best[ext=mp4]/best',
            'outtmpl': f'{TEMP_DIR}/%(title)s_{session_id}.%(ext)s',
            'noplaylist': True,
            'quiet': True,
        }
        
        if tipo == 'audio':
            opciones['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=True)
            titulo = info.get('title', 'video')
            
            # Encontrar archivo
            ext = 'mp3' if tipo == 'audio' else 'mp4'
            filename = f"{titulo}_{session_id}.{ext}"
            
            # Buscar el archivo real
            for f in os.listdir(TEMP_DIR):
                if session_id in f:
                    filepath = os.path.join(TEMP_DIR, f)
                    clean_name = f.replace(f'_{session_id}', '')
                    return send_file(filepath, as_attachment=True, download_name=clean_name)
                    
        return "Archivo no encontrado", 404
        
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
