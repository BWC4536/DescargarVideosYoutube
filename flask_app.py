from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import tempfile

app = Flask(__name__)

# PythonAnywhere permite escribir en /tmp sin problemas
TEMP_DIR = '/tmp/youtube_downloads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/descargar', methods=['POST'])
def descargar():
    url = request.form.get('url')  # PythonAnywhere maneja mejor form-data
    tipo = request.form.get('tipo', 'video')
    
    if not url:
        return "Error: URL requerida", 400
    
    # Crear directorio temporal si no existe
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    
    # Limpiar archivos viejos (opcional, para no llenar disco)
    limpiar_archivos_viejos()
    
    try:
        # Generar nombre único
        import uuid
        session_id = str(uuid.uuid4())[:8]
        
        opciones = {
            'format': 'bestaudio/best' if tipo == 'audio' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{TEMP_DIR}/%(title)s_{session_id}.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
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
            
            # Encontrar el archivo descargado
            ext = 'mp3' if tipo == 'audio' else 'mp4'
            filename = f"{titulo}_{session_id}.{ext}"
            filepath = os.path.join(TEMP_DIR, filename)
            
            # Si no existe con ese nombre, buscar el archivo reciente
            if not os.path.exists(filepath):
                archivos = os.listdir(TEMP_DIR)
                archivos.sort(key=lambda x: os.path.getmtime(os.path.join(TEMP_DIR, x)))
                for f in archivos:
                    if session_id in f:
                        filepath = os.path.join(TEMP_DIR, f)
                        filename = f
                        break
            
            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename.replace(f'_{session_id}', ''),
                mimetype='audio/mpeg' if tipo == 'audio' else 'video/mp4'
            )
            
    except Exception as e:
        return f"Error: {str(e)}", 500

def limpiar_archivos_viejos():
    """Elimina archivos temporales con más de 1 hora"""
    try:
        ahora = os.path.getmtime
        for f in os.listdir(TEMP_DIR):
            path = os.path.join(TEMP_DIR, f)
            if os.path.isfile(path):
                # Eliminar si tiene más de 1 hora
                import time
                if time.time() - os.path.getmtime(path) > 3600:
                    os.remove(path)
    except:
        pass

if __name__ == '__main__':
    app.run(debug=True)