from flask import Flask, render_template, request, jsonify, redirect
import requests
import os

app = Flask(__name__)

COBALT_API = "https://api.cobalt.tools/api/json"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/descargar', methods=['POST'])
def descargar():
    url = request.form.get('url')
    tipo = request.form.get('tipo', 'video')
    
    if not url:
        return "URL requerida", 400
    
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        data = {
            "url": url,
            "isAudio": tipo == 'audio',
            "filenamePattern": "basic"
        }
        
        # Llamar a API de cobalt
        response = requests.post(COBALT_API, json=data, headers=headers, timeout=30)
        result = response.json()
        
        if result.get('status') == 'stream':
            # Éxito - redirigir a URL de descarga
            return redirect(result['url'])
            
        elif result.get('status') == 'picker':
            # Múltiples calidades disponibles
            return render_template('picker.html', 
                                   urls=result.get('urls', []),
                                   audio=result.get('audio', ''))
            
        elif result.get('status') == 'error':
            error_msg = result.get('error', {}).get('code', 'Error desconocido')
            return f"Error de cobalt: {error_msg}", 400
            
        else:
            return f"Respuesta inesperada: {result}", 500
            
    except requests.Timeout:
        return "Timeout - el video es muy largo o la API está lenta", 504
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/api/info', methods=['POST'])
def info():
    """Endpoint AJAX para obtener info sin redirigir"""
    url = request.json.get('url')
    tipo = request.json.get('tipo', 'video')
    
    if not url:
        return jsonify({'error': 'URL requerida'}), 400
    
    try:
        headers = {
            "Accept": "application/json", 
            "Content-Type": "application/json"
        }
        
        data = {
            "url": url,
            "isAudio": tipo == 'audio',
            "filenamePattern": "basic"
        }
        
        response = requests.post(COBALT_API, json=data, headers=headers, timeout=30)
        result = response.json()
        
        if result.get('status') == 'stream':
            return jsonify({
                'success': True,
                'url': result['url'],
                'filename': result.get('filename', 'download')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', {}).get('code', 'Error')
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)