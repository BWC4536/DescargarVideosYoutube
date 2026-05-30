import sys
path = '/home/tuusuario/mi_youtube_downloader'
if path not in sys.path:
    sys.path.append(path)

from flask_app import app as application