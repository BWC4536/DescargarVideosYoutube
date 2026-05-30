from flask import Flask, render_template, request, jsonify
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

COBALT_API = "https://api.cobalt.tools/api/json"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def info():
    url = request.json.get('url')
    tipo = request.json.get('tipo', 'video')
    
    logger.info(f"Solicitud recibida: URL={url}, tipo={tipo}")
    
    if not url:
        return jsonify({'success': False, 'error': 'URL requerida'}), 400
    
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        data = {
            "url": url,
            "isAudioOnly": tipo == 'audio',  # Corregido: isAudioOnly, no isAudio
            "filenamePattern": "basic",
            "downloadMode": "auto"
        }
        
        logger.info(f"Enviando a cobalt: {data}")
        
        response = requests.post(
            COBALT_API, 
            json=data, 
            headers=headers, 
            timeout=30
        )
        
        logger.info(f"Respuesta status: {response.status_code}")
        logger.info(f"Respuesta body: {response.text}")
        
        result = response.json()
        
        if result.get('status') == 'stream':
            return jsonify({
                'success': True,
                'url': result['url'],
                'filename': result.get('filename', 'download')
            })
        elif result.get('status') == 'error':
            error_info = result.get('error', {})
            error_text = error_info.get('code') or error_info.get('text') or 'Error desconocido'
            return jsonify({
                'success': False, 
                'error': error_text,
                'full_response': result  # Para debug
            }), 400
        else:
            return jsonify({
                'success': False, 
                'error': f'Status inesperado: {result.get("status")}',
                'full_response': result
            }), 400
            
    except requests.Timeout:
        logger.error("Timeout")
        return jsonify({'success': False, 'error': 'Timeout - API muy lenta'}), 504
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)