# ============================================
# Site QSL & Carnet de Log – Version DESIGN + ONLINE READY
# Techno : Flask + TailwindCSS
# ============================================

from flask import Flask, render_template_string, request, redirect, url_for
import pandas as pd
import zipfile, os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
QSL_FOLDER = 'qsl'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QSL_FOLDER, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>RadioLog & QSL Manager</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">
<div class="max-w-6xl mx-auto p-6">
<h1 class="text-4xl font-bold mb-6 text-center">📡 RadioLog & QSL Manager</h1>

<div class="grid md:grid-cols-3 gap-6">
<div class="bg-white p-6 rounded-2xl shadow">
<h2 class="text-xl font-semibold mb-4">📊 Carnet de log</h2>
<p class="text-sm text-gray-600 mb-2">Fichiers stockés dans <b>/uploads</b></p>
<form method="post" enctype="multipart/form-data" action="/upload_log">
<input type="file" name="logfile" accept=".xlsx" required>
<button class="mt-3 bg-blue-600 text-white px-4 py-2 rounded">Importer</button>
</form>
<a href="/log" class="block mt-4 text-blue-700 underline">📄 Visualiser le carnet</a>
</div>

<div class="bg-white p-6 rounded-2xl shadow">
<h2 class="text-xl font-semibold mb-4">🖼️ Import QSL</h2>
<p class="text-sm text-gray-600 mb-2">Stockage : <b>/qsl/REGION</b></p>
<form method="post" enctype="multipart/form-data" action="/upload_qsl" class="space-y-2">
<input type="text" name="region" placeholder="Région radio" required class="border p-2 w-full rounded">
<input type="file" name="qslfiles" multiple required>
<button class="bg-green-600 text-white px-4 py-2 rounded">Importer</button>
</form>
</div>

<div class="bg-white p-6 rounded-2xl shadow">
<h2 class="text-xl font-semibold mb-4">🗂️ Régions QSL</h2>
<ul class="space-y-2">
{% for r in regions %}
<li><a class="text-blue-700 underline" href="/qsl/{{ r }}">📁 {{ r }}</a></li>
{% endfor %}
</ul>
</div>
</div>

<footer class="text-center text-gray-500 mt-10">Radioamateur Logbook – v1.1</footer>
</div>
</body>
</html>
"""

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
