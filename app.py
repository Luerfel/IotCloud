from flask import Flask, request, jsonify, render_template, send_file, url_for
from werkzeug.utils import secure_filename
import os
import cv2
import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Certifique-se de que a pasta de uploads existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/image/<filename>')
def uploaded_file(filename):
    file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(f"Servindo o arquivo: {file}")
    return send_file(file, mimetype='image/png')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhum arquivo de imagem enviado'}), 400

    # Salva a imagem original
    file = request.files['image']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    print(f"Imagem original salva em: {file_path}")

    # Processa a imagem com o filtro de Canny
    image = cv2.imread(file_path)
    if image is None:
        print("Erro ao ler a imagem.")
        return jsonify({'error': 'Erro ao ler a imagem.'}), 500

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    # Salva a imagem processada
    processed_filename = 'processed_' + filename
    processed_file_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
    cv2.imwrite(processed_file_path, edges)
    print(f"Imagem processada salva em: {processed_file_path}")

    # Retorna os dados no formato JSON solicitado
    return jsonify({
        'datetime': datetime.datetime.now().isoformat(),
        'image': url_for('uploaded_file', filename=filename, _external=True),
        'image_proc': url_for('uploaded_file', filename=processed_filename, _external=True),
        'ip': request.remote_addr
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)




