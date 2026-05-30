from flask import Flask, render_template, request, jsonify
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Nueva API de cobalt 10
COBALT_API = "https://api.cobalt.tools/api/json"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def info():
    url = request.json.get('url')
    tipo = request.json.get('tipo', 'video')
    
    logger.info(f"Solicitud: URL={url}, tipo={tipo}")
    
    if not url:
        return jsonify({'success': False, 'error': 'URL requerida'}), 400
    
    try:
        # Headers requeridos por la nueva API
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        # Nuevo formato de la API cobalt 10
        data = {
            "url": url,
            "downloadMode": "auto",  # "auto" o "audio"
            "filenameStyle": "basic",  # "basic", "pretty", "classic"
        }
        
        # Si es solo audio
        if tipo == 'audio':
            data["downloadMode"] = "audio"
            data["audioFormat"] = "mp3"  # mp3, ogg, wav, opus
        
        logger.info(f"Enviando: {data}")
        
        response = requests.post(
            COBALT_API, 
            json=data, 
            headers=headers, 
            timeout=60  # Más tiempo por si acaso
        )
        
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Respuesta: {response.text[:500]}")
        
        result = response.json()
        
        if result.get('status') == 'tunnel' or result.get('status') == 'stream':
            return jsonify({
                'success': True,
                'url': result['url'],
                'filename': result.get('filename', 'download')
            })
        elif result.get('status') == 'error':
            error_text = result.get('text', 'Error desconocido')
            return jsonify({
                'success': False, 
                'error': error_text
            }), 400
        else:
            return jsonify({
                'success': False, 
                'error': f'Respuesta: {result.get("status")}'
            }), 400
            
    except requests.Timeout:
        return jsonify({'success': False, 'error': 'Timeout'}), 504
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)