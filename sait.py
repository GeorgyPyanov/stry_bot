import json
import random
from flask import Flask, url_for, render_template, redirect, request
from webdav3.client import Client

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/', methods=['POST', "GET"])
def sample_file_upload():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        r = {'name': name, 'email': email}
        with open('data.json', 'w', encoding='utf8') as cat_file:
            json.dump(r, cat_file)
        return redirect('/hero')
    return render_template('form.html')


@app.route('/hero', methods=['POST', "GET"])
def hiro():
    if request.method == 'POST':
        n = request.form.get('item1')
        c = []
        m = 2
        if n:
            while n:
                c.append(n)
                n = request.form.get(f'item{m}')
                n2 = request.form.get(f'hero{m}')
                m += 1
        with open('data.json', encoding="utf8") as cat_file:
            r = json.load(cat_file)
        r['hero'] = c
        with open('data.json', 'w') as cat_file:
            json.dump(r, cat_file)
        return redirect('/text')
    return render_template('form2.html')


@app.route('/text', methods=['POST', "GET"])
def history():
    if request.method == 'POST':
        n = request.form.get('item1')
        n2 = request.form.get('hero1')
        c = []
        m = 2
        if n:
            while n:
                c.append([n, n2])
                n = request.form.get(f'item{m}')
                n2 = request.form.get(f'hero{m}')
                m += 1
        with open('data.json', encoding="utf8") as cat_file:
            r = json.load(cat_file)
        r['text'] = c
        with open('data.json', 'w') as cat_file:
            json.dump(r, cat_file)
        return redirect('/name')
    with open('data.json', encoding="utf8") as cat_file:
        r = json.load(cat_file)
    color = {'1': r['hero']}
    return render_template('form3.html', colours=color)


@app.route('/name', methods=['POST', "GET"])
def finish():
    if request.method == 'POST':
        history = request.form.get('history')
        opis = request.form.get('opis')
        with open('data.json', encoding="utf8") as cat_file:
            r = json.load(cat_file)
        r['history'] = history
        r['apply'] = opis
        with open('data.json', 'w') as cat_file:
            json.dump(r, cat_file)
        return redirect('/finish')
    return render_template('form4.html')


@app.route('/finish')
def finished():
    data = {
        'webdav_hostname': "https://webdav.cloud.mail.ru", 'webdav_login': "georgpyanov07@mail.ru",
        'webdav_password': "CypB0tPdV6ruDiX9w7p7"}
    client = Client(data)
    a = list('0123456789')
    random.shuffle(a)
    client.upload_sync(remote_path=f"check/{''.join(a)}.json",
                       local_path='data.json')
    return render_template('finish.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')