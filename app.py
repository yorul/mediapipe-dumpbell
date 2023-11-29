import os
import subprocess

from flask import Flask, request, render_template, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['video']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join('.', filename))
            uuid = filename.split('.')[0]
            file_path = os.path.join('.', filename)
            file_path_out = os.path.join('static', uuid + '.mp4')  # 出力パスをstaticフォルダに変更
            subprocess.run(['python', 'dumbbell.py', file_path, file_path_out])
            return {'status': 'OK', 'output_url': url_for('static', filename=uuid + '.mp4')}
    return {'status': 'FAIL'}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
