from flask import Flask, render_template, request, jsonify
import requests
import re

app = Flask(__name__)

def obtener_y2mate(url):
    """API no oficial de y2mate"""
    try:
        # Extraer ID del video
        if 'youtu.be' in url:
            video_id = url.split('/')[-1].split('?')[0]
        else:
            match = re.search(r'[?&]v=([^&]+)', url)
            video_id = match.group(1) if match else None
        
        if not video_id:
            return None, "No se pudo extraer ID del video"
        
        # Obtener info del video
        info_url = "https://www.y2mate.com/mates/analyzeV2/ajax"
        data = {
            'k_query': f'https://www.youtube.com/watch?v={video_id}',
            'k_page': 'home',
            'hl': 'es',
            'q_auto': '0'
        }
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        
        resp = requests.post(info_url, data=data, headers=headers, timeout=30)
        result = resp.json()
        
        if result.get('status') == 'ok':
            links = result.get('links', {}).get('mp4', {})
            if links:
                # Tomar la mejor calidad
                best = list(links.values())[-1]
                return best.get('k'), result.get('title', 'video')
        
        return None, "No se encontraron enlaces"
        
    except Exception as e:
        return None, str(e)

@app.route('/api/info', methods=['POST'])
def info():
    url = request.json.get('url')
    tipo = request.json.get('tipo', 'video')
    
    if tipo == 'audio':
        # Para audio usar cobalt si funciona, o indicar que no está disponible
        return jsonify({'success': False, 'error': 'Audio no disponible en esta alternativa'})
    
    link, titulo = obtener_y2mate(url)
    
    if link:
        return jsonify({
            'success': True,
            'url': link,
            'filename': f'{titulo}.mp4'
        })
    else:
        return jsonify({'success': False, 'error': titulo}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)