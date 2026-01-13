
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import pandas as pd
import zipfile, os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
QSL_FOLDER = 'qsl'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QSL_FOLDER, exist_ok=True)

HOME_HTML = '''
<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>RadioLog & QSL</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
<div class="max-w-6xl mx-auto p-6">
<h1 class="text-4xl font-bold mb-6">📡 RadioLog & QSL Manager</h1>

<div class="grid md:grid-cols-3 gap-6">
<div class="bg-white p-5 rounded shadow">
<h2 class="font-semibold text-lg mb-2">📊 Carnet de log</h2>
<p class="text-sm text-gray-500">Stockage : /uploads</p>
<form method="post" enctype="multipart/form-data" action="/upload_log">
<input type="file" name="logfile" accept=".xlsx" required>
<button class="mt-3 bg-blue-600 text-white px-4 py-2 rounded">Importer</button>
</form>
<a href="/log" class="block mt-4 text-blue-700 underline">Voir le carnet</a>
</div>

<div class="bg-white p-5 rounded shadow">
<h2 class="font-semibold text-lg mb-2">🖼️ Import QSL</h2>
<p class="text-sm text-gray-500">Stockage : /qsl/REGION</p>
<form method="post" enctype="multipart/form-data" action="/upload_qsl">
<input name="region" placeholder="Région radio" class="border p-2 w-full mb-2" required>
<input type="file" name="qslfiles" multiple required>
<button class="mt-3 bg-green-600 text-white px-4 py-2 rounded">Importer</button>
</form>
</div>

<div class="bg-white p-5 rounded shadow">
<h2 class="font-semibold text-lg mb-2">🗂️ Régions QSL</h2>
<ul>
{% for r in regions %}
<li><a class="text-blue-700 underline" href="/qsl/{{r}}">📁 {{r}}</a></li>
{% endfor %}
</ul>
</div>
</div>
</div>
</body>
</html>
'''

@app.route("/")
def home():
    regions = os.listdir(QSL_FOLDER)
    return render_template_string(HOME_HTML, regions=regions)

@app.route("/upload_log", methods=["POST"])
def upload_log():
    f = request.files["logfile"]
    path = os.path.join(UPLOAD_FOLDER, f.filename)
    f.save(path)
    df = pd.read_excel(path)
    df.to_csv(os.path.join(UPLOAD_FOLDER, "log.csv"), index=False)
    return redirect("/")

@app.route("/log")
def view_log():
    csv_path = os.path.join(UPLOAD_FOLDER, "log.csv")
    if not os.path.exists(csv_path):
        return "Aucun carnet importé"
    df = pd.read_csv(csv_path)
    return df.to_html(classes="table-auto border", index=False)

@app.route("/upload_qsl", methods=["POST"])
def upload_qsl():
    region = request.form["region"]
    region_path = os.path.join(QSL_FOLDER, region)
    os.makedirs(region_path, exist_ok=True)

    for f in request.files.getlist("qslfiles"):
        if f.filename.endswith(".zip"):
            zp = os.path.join(region_path, f.filename)
            f.save(zp)
            with zipfile.ZipFile(zp, "r") as z:
                z.extractall(region_path)
        else:
            f.save(os.path.join(region_path, f.filename))
    return redirect("/")

@app.route("/qsl/<region>")
def qsl_region(region):
    path = os.path.join(QSL_FOLDER, region)
    if not os.path.exists(path):
        return "Région inconnue"
    files = os.listdir(path)
    links = "".join([f'<li><a href="/qsl/{region}/{f}">{f}</a></li>' for f in files])
    return f"<h2>QSL {region}</h2><ul>{links}</ul>"

@app.route("/qsl/<region>/<filename>")
def qsl_file(region, filename):
    return send_from_directory(os.path.join(QSL_FOLDER, region), filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
