from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)
users = []

@app.route('/')
def home():
    return 'регестрация по ссылке:/regestrazia, а вход: /vhod'


@app.route('/vhod', methods=['GET', 'POST'])
def vhod():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users.append({'username': username, 'password': password})
        return redirect(url_for('success'))
    return render_template('vhod.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users.append({'username': username, 'password': password})
        return redirect(url_for('success'))
    return render_template('registraz.html')

@app.route('/end')
def success():
    return 'Вы зарегистрировались!'


if __name__ == '__main__':
    app.run(debug=True)

