from flask import Flask, render_template_string, request, redirect, url_for
import pandas as pd
import zipfile, os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
QSL_FOLDER = 'qsl'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QSL_FOLDER, exist_ok=True)

HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>RadioLog & QSL Manager</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">
<div class="max-w-5xl mx-auto p-6">
<h1 class="text-4xl font-bold mb-6 text-center">📡 RadioLog & QSL Manager</h1>

<div class="grid md:grid-cols-2 gap-6">
<div class="bg-white p-6 rounded-2xl shadow">
<h2 class="text-xl font-semibold mb-4">📊 Import carnet de log</h2>
<form method="post" enctype="multipart/form-data" action="/upload_log">
<input type="file" name="logfile" accept=".xlsx" required>
<button class="bg-blue-600 text-white px-4 py-2 rounded">Importer</button>
</form>
</div>

<div class="bg-white p-6 rounded-2xl shadow">
<h2 class="text-xl font-semibold mb-4">🖼️ Import QSL</h2>
<form method="post" enctype="multipart/form-data" action="/upload_qsl">
<input type="text" name="region" placeholder="Région radio" required class="border p-2 w-full rounded">
<input type="file" name="qslfiles" multiple required>
<button class="bg-green-600 text-white px-4 py-2 rounded">Importer</button>
</form>
</div>
</div>

<div class="bg-white p-6 rounded-2xl shadow mt-6">
<h2 class="text-xl font-semibold mb-4">🗂️ Régions QSL</h2>
<ul>
{% for r in regions %}
<li>{{ r }}</li>
{% endfor %}
</ul>
</div>
</div>
</body>
</html>"""

@app.route('/')
def index():
    regions = os.listdir(QSL_FOLDER)
    return render_template_string(HTML, regions=regions)

@app.route('/upload_log', methods=['POST'])
def upload_log():
    file = request.files['logfile']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)
    df = pd.read_excel(path)
    df.to_csv(os.path.join(UPLOAD_FOLDER, 'log.csv'), index=False)
    return redirect(url_for('index'))

@app.route('/upload_qsl', methods=['POST'])
def upload_qsl():
    region = request.form['region']
    region_path = os.path.join(QSL_FOLDER, region)
    os.makedirs(region_path, exist_ok=True)
    for f in request.files.getlist('qslfiles'):
        if f.filename.endswith('.zip'):
            zip_path = os.path.join(region_path, f.filename)
            f.save(zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(region_path)
        else:
            f.save(os.path.join(region_path, f.filename))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
