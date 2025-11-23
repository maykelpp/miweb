from flask import Flask, render_template_string, request, jsonify, send_file
import yt_dlp
import requests
import os
import re
from urllib.parse import urlparse

app = Flask(__name__)

# Configuración
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# HTML Template Futurista
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediaDownloaderPRO</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            padding: 40px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            margin-bottom: 40px;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        }
        
        .header h1 {
            font-size: 3em;
            font-weight: 900;
            background: linear-gradient(45deg, #fff, #00f2ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(0, 242, 255, 0.5);
        }
        
        .platform-selector {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .platform-btn {
            padding: 15px 25px;
            border: 2px solid #667eea;
            background: rgba(102, 126, 234, 0.1);
            color: #fff;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 16px;
            font-weight: 600;
        }
        
        .platform-btn:hover {
            background: linear-gradient(135deg, #667eea, #764ba2);
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        
        .platform-btn.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            box-shadow: 0 0 30px rgba(102, 126, 234, 0.6);
        }
        
        .input-section {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .input-group {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .url-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid rgba(102, 126, 234, 0.5);
            background: rgba(0, 0, 0, 0.3);
            color: #fff;
            border-radius: 12px;
            font-size: 16px;
        }
        
        .url-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
        }
        
        .format-selector {
            display: flex;
            gap: 10px;
            justify-content: center;
        }
        
        .format-btn {
            padding: 12px 30px;
            border: 2px solid #00f2ff;
            background: rgba(0, 242, 255, 0.1);
            color: #00f2ff;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
        }
        
        .format-btn:hover {
            background: #00f2ff;
            color: #0f0c29;
        }
        
        .download-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border: none;
            border-radius: 12px;
            color: #fff;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            margin-top: 20px;
            transition: all 0.3s;
        }
        
        .download-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(245, 87, 108, 0.4);
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .preview-section {
            display: none;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            margin-top: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .preview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .preview-card {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            border-radius: 15px;
            border: 2px solid rgba(102, 126, 234, 0.3);
        }
        
        .preview-card h3 {
            color: #00f2ff;
            margin-bottom: 15px;
        }
        
        .preview-card img {
            width: 100%;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .preview-card video {
            width: 100%;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .download-link {
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #fff;
            text-decoration: none;
            border-radius: 8px;
            margin-top: 10px;
            transition: all 0.3s;
        }
        
        .download-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .info-text {
            color: #aaa;
            font-size: 14px;
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>MediaDownloaderPRO</h1>
            <p>Descarga contenido de múltiples plataformas</p>
        </div>
        
        <div class="platform-selector">
            <button class="platform-btn active" data-platform="youtube">YouTube</button>
            <button class="platform-btn" data-platform="instagram">Instagram</button>
            <button class="platform-btn" data-platform="facebook">Facebook</button>
            <button class="platform-btn" data-platform="tiktok">TikTok</button>
        </div>
        
        <div class="input-section">
            <div class="input-group">
                <input type="text" class="url-input" id="urlInput" placeholder="Pega la URL aquí...">
            </div>
            
            <div class="format-selector">
                <button class="format-btn" data-format="mp4">MP4</button>
                <button class="format-btn" data-format="mp3">MP3</button>
                <button class="format-btn" data-format="photo" id="photoBtn" style="display:none;">Fotos</button>
            </div>
            
            <button class="download-btn" onclick="processMedia()">Procesar Media</button>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 15px;">Procesando...</p>
        </div>
        
        <div class="preview-section" id="previewSection">
            <h2>Vista Previa</h2>
            <div class="preview-grid" id="previewGrid"></div>
        </div>
    </div>
    
    <script>
        let selectedPlatform = 'youtube';
        let selectedFormat = 'mp4';
        
        // Platform selection
        document.querySelectorAll('.platform-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.platform-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                selectedPlatform = this.dataset.platform;
                
                // Show photo option only for TikTok
                document.getElementById('photoBtn').style.display = 
                    selectedPlatform === 'tiktok' ? 'inline-block' : 'none';
            });
        });
        
        // Format selection
        document.querySelectorAll('.format-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                selectedFormat = this.dataset.format;
                this.style.background = '#00f2ff';
                this.style.color = '#0f0c29';
                setTimeout(() => {
                    this.style.background = 'rgba(0, 242, 255, 0.1)';
                    this.style.color = '#00f2ff';
                }, 200);
            });
        });
        
        async function processMedia() {
            const url = document.getElementById('urlInput').value;
            if (!url) {
                alert('Por favor ingresa una URL');
                return;
            }
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('previewSection').style.display = 'none';
            
            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        url: url,
                        platform: selectedPlatform,
                        format: selectedFormat
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayPreview(data);
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error de conexión: ' + error);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        function displayPreview(data) {
            const previewSection = document.getElementById('previewSection');
            const previewGrid = document.getElementById('previewGrid');
            previewGrid.innerHTML = '';
            
            if (data.platform === 'tiktok') {
                // TikTok preview with separate blocks
                if (data.video) {
                    previewGrid.innerHTML += `
                        <div class="preview-card">
                            <h3>🎥 Video</h3>
                            <video controls src="${data.video}"></video>
                            <p class="info-text">Duración: ${data.duration || 'N/A'}</p>
                            <p class="info-text">Calidad: ${data.quality || 'N/A'}</p>
                            <a href="${data.video}" class="download-link" download>Descargar Video</a>
                        </div>
                    `;
                }
                
                if (data.audio) {
                    previewGrid.innerHTML += `
                        <div class="preview-card">
                            <h3>🎵 Audio</h3>
                            <audio controls src="${data.audio}"></audio>
                            <a href="${data.audio}" class="download-link" download>Descargar Audio</a>
                        </div>
                    `;
                }
                
                if (data.images && data.images.length > 0) {
                    data.images.forEach((img, idx) => {
                        previewGrid.innerHTML += `
                            <div class="preview-card">
                                <h3>📷 Foto ${idx + 1}</h3>
                                <img src="${img}" alt="Image ${idx + 1}">
                                <a href="${img}" class="download-link" download>Descargar</a>
                            </div>
                        `;
                    });
                }
            } else {
                // Other platforms
                if (data.thumbnail) {
                    previewGrid.innerHTML += `
                        <div class="preview-card">
                            <h3>Vista Previa</h3>
                            <img src="${data.thumbnail}" alt="Thumbnail">
                            <p class="info-text">${data.title || 'Sin título'}</p>
                        </div>
                    `;
                }
                
                previewGrid.innerHTML += `
                    <div class="preview-card">
                        <h3>Información</h3>
                        <p class="info-text">Formato: ${data.format || 'N/A'}</p>
                        <p class="info-text">Duración: ${data.duration || 'N/A'}</p>
                        <p class="info-text">Calidad: ${data.quality || 'N/A'}</p>
                        <a href="${data.download_url}" class="download-link" download>Descargar</a>
                    </div>
                `;
            }
            
            previewSection.style.display = 'block';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process_media():
    data = request.json
    url = data.get('url')
    platform = data.get('platform')
    format_type = data.get('format')
    
    try:
        if platform == 'tiktok':
            return process_tiktok(url, format_type)
        else:
            return process_ytdlp(url, platform, format_type)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def process_tiktok(url, format_type):
    """Procesa TikTok usando TIKWM API"""
    try:
        # TIKWM API endpoint
        api_url = 'https://www.tikwm.com/api/'
        response = requests.post(api_url, data={'url': url, 'hd': 1})
        result = response.json()
        
        if result.get('code') != 0:
            return jsonify({'success': False, 'error': 'Error al obtener datos de TikTok'})
        
        data = result.get('data', {})
        
        response_data = {
            'success': True,
            'platform': 'tiktok',
            'title': data.get('title', ''),
            'duration': f"{data.get('duration', 0)}s",
            'quality': 'HD' if data.get('hdplay') else 'SD'
        }
        
        # Video
        if format_type == 'mp4':
            response_data['video'] = data.get('hdplay') or data.get('play')
        
        # Audio
        if format_type == 'mp3':
            response_data['audio'] = data.get('music')
        
        # Fotos (carrusel)
        if format_type == 'photo' and data.get('images'):
            response_data['images'] = data.get('images', [])
        
        # Incluir todo para preview completo
        response_data['video'] = data.get('hdplay') or data.get('play')
        response_data['audio'] = data.get('music')
        response_data['images'] = data.get('images', [])
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def process_ytdlp(url, platform, format_type):
    """Procesa YouTube, Instagram, Facebook con yt-dlp"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        if format_type == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
            })
        else:
            ydl_opts.update({
                'format': 'best',
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
            })
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            response_data = {
                'success': True,
                'platform': platform,
                'title': info.get('title', 'Sin título'),
                'thumbnail': info.get('thumbnail'),
                'duration': f"{info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}",
                'quality': info.get('resolution', 'N/A'),
                'format': format_type.upper(),
                'download_url': info.get('url')
            }
            
            return jsonify(response_data)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Para Termux usar 0.0.0.0 y puerto 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
