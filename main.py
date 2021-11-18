from flask import Flask, render_template, request, session, flash, redirect
from flask.helpers import url_for
import pymysql
from datetime import datetime
import json
from flask_mail import Mail
from werkzeug.utils import secure_filename
import os
import math

UPLOAD_FOLDER = '/Users/gtanuj7987/Documents/Flask/proj2/static/assets/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

params = ""
val = 0

def changelogin():
    global val
    val = 1

def changelogout():
    global val
    val = 0

with open("/Users/gtanuj7987/Documents/Flask/proj2/config.json") as file:
    params = json.load(file)["params"]
    print(params['no_of_post'])
    print(params['user_name'])

app = Flask(__name__)
app.secret_key = "super-secret-key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail_user'],
    MAIL_PASSWORD=  params['gmail_password']
)

mail = Mail(app)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/logout')
def logout():
    session.pop('user')
    changelogout()
    print("logout", val)
    return render_template('index.html', params = params, val = val)

@app.route('/samplepost', methods = ['GET'])
def samplepost():
    print("samplepost", val)
    return render_template('sampleposts.html', params = params, val = val)

@app.route('/editexistedpost/<post_slug>', methods = ['GET', 'POST'])
def updatepost(post_slug):

    if request.method == 'POST':
        name = request.form.get('user_name')
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        message = request.form.get('user_message')   

        try:
            connection = pymysql.connect(host=params['local_uri']['local_host'],
                                user=params['local_uri']['local_user'],
                                password=params['local_uri']['local_psd'],
                                database=params['local_uri']['local_database'])

            cursor = connection.cursor()

            filename = ""

            if 'filename' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['filename']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            print(name, title, message, filename, post_slug, subtitle)

            sqlite_select_query = f"UPDATE posts SET name = '{name}', title = '{title}', details = '{message}', dates = '{datetime.now()}', subtitle = '{subtitle}', img_file = '{filename}' WHERE slug = '{post_slug}'"
            cursor.execute(sqlite_select_query)
            connection.commit()
            connection.close()

        except Exception as e:
            print(e)

    print("edit", val)
    return render_template('dashboard.html', params = params, val = val)

@app.route('/update/<post_slug>', methods = ['GET', 'POST'])
def update(post_slug):
    return render_template('editform.html', params = params, post_slug = post_slug, val = val)    


@app.route('/del/<post_slug>', methods = ['GET', 'POST'])
def delt(post_slug):

    try:
        connection = pymysql.connect(host=params['local_uri']['local_host'],
                             user=params['local_uri']['local_user'],
                             password=params['local_uri']['local_psd'],
                             database=params['local_uri']['local_database'])

        cursor = connection.cursor()

        sqlite_select_query = f"DELETE FROM posts WHERE slug = '{post_slug}'"
        cursor.execute(sqlite_select_query)
        connection.commit()
        connection.close()

    except Exception as e:
        print(e)

    print("delete", val)
    return render_template('dashboard.html', params = params, val = val)

@app.route('/edit', methods = ['GET', 'POST'])
def editpost():

    try:
        connection = pymysql.connect(host=params['local_uri']['local_host'],
                             user=params['local_uri']['local_user'],
                             password=params['local_uri']['local_psd'],
                             database=params['local_uri']['local_database'])

        cursor = connection.cursor()

        sqlite_select_query = f"SELECT * FROM posts"
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        connection.close()

    except Exception as e:
        print(e)
    
    if 'user' in session and session['user'] == params['user_name']:    
        return render_template('edit.html', params = params, content = records, val = val)

    print("editsimple", val)
    return render_template('edit.html', params = params, val = val)

@app.route('/delete', methods = ['GET', 'POST'])
def deletepost():

    try:
        connection = pymysql.connect(host=params['local_uri']['local_host'],
                             user=params['local_uri']['local_user'],
                             password=params['local_uri']['local_psd'],
                             database=params['local_uri']['local_database'])

        cursor = connection.cursor()

        sqlite_select_query = f"SELECT * FROM posts"
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        connection.close()

    except Exception as e:
        print(e)
    
    if 'user' in session and session['user'] == params['user_name']:    
        return render_template('delete.html', params = params, content = records, val = val)

    print("deletesimple", val)
    return render_template('dashboard.html', params = params, val = val)

@app.route('/addpost', methods = ['GET', 'POST'])
def addpost():

    if 'user' in session and session['user'] == params['user_name']:
        if request.method == 'POST':  

            name = request.form.get('user_name')
            title = request.form.get('title')
            subtitle = request.form.get('subtitle')
            slug = request.form.get('slug')
            message = request.form.get('user_message')

            # print(name, title, message, slug, subtitle, "first")

            try:
                connection = pymysql.connect(host=params['local_uri']['local_host'],
                             user=params['local_uri']['local_user'],
                             password=params['local_uri']['local_psd'],
                             database=params['local_uri']['local_database'])

                cursor = connection.cursor()

                filename = ""

                if 'filename' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                file = request.files['filename']
                if file.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    print(filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    # return redirect(url_for('download_file', name=filename))

                print(name, title, message, filename, slug, subtitle)

                sqlite_select_query = f"INSERT INTO posts(name, title, details, dates, slug, subtitle, img_file) VALUES('{name}', '{title}', '{message}', '{datetime.now()}', '{slug}', '{subtitle}', '{filename}')"
                cursor.execute(sqlite_select_query)
                connection.commit()
                connection.close()

                # print(name, title, message, filename, slug, subtitle)

            except Exception as e:
                print(e)

    print("addsimple", val)
    return render_template('addpost.html', params = params, val = val)


@app.route('/view')
def view():

    try:
        connection = pymysql.connect(host=params['local_uri']['local_host'],
                             user=params['local_uri']['local_user'],
                             password=params['local_uri']['local_psd'],
                             database=params['local_uri']['local_database'])

        cursor = connection.cursor()

        sqlite_select_query = f"SELECT * FROM posts"
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        connection.close()

    except Exception as e:
        print(e)
    
    if 'user' in session and session['user'] == params['user_name']:    
        return render_template('view.html', params = params, content = records, val = val)

    print("view", val)
    return render_template('login.html', params = params, val = val)

@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard():

    if 'user' in session and session['user'] == params['user_name']:
        return render_template('dashboard.html', params = params, val = val)

    if request.method == 'POST':
        
        duname = request.form.get('email')
        dpass = request.form.get('pass')

        if (str(duname) == params['user_name'] and str(dpass) == params['user_password']):
            session['user'] = duname
            changelogin()
            return render_template('dashboard.html', params = params, val = val)

    print("dashboard", val)
    return render_template('login.html', params = params, val = val)

@app.route("/", defaults={'page': 0})
@app.route("/page/<int:page>")
def home(page):

    records = 0
    try:

        connection = pymysql.connect(host=params['local_uri']['local_host'],
                             user=params['local_uri']['local_user'],
                             password=params['local_uri']['local_psd'],
                             database=params['local_uri']['local_database'])

        cursor = connection.cursor()

        start = int(page) * params['no_of_post']
        sqlite_select_query = f"SELECT * FROM posts limit {start}, {params['no_of_post']}"
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        records = records[0:params["no_of_post"]]
        print(records)

        connection.close()

    except Exception as e:
        print(e)    

    print("home", records)
    return render_template('index.html', params = params, val = val, page = page, content = records)

@app.route('/about')
def about():
    print("about", val)
    return render_template('about.html', params = params, val = val)

@app.route('/post/<post_slug>/', methods = ["GET", "POST"])
def post(post_slug):

    records = 0
    name = "Tanuj testing content"
    try:

        connection = pymysql.connect(host=params['local_uri']['local_host'],
                             user=params['local_uri']['local_user'],
                             password=params['local_uri']['local_psd'],
                             database=params['local_uri']['local_database'])

        cursor = connection.cursor()

        sqlite_select_query = f"SELECT * FROM posts WHERE slug = '{post_slug}'"
        cursor.execute(sqlite_select_query)
        records = cursor.fetchone()
        print(records)

        connection.close()

    except Exception as e:
        print(e)

    print("post", val)
    return render_template('post.html', name = name, params = params, content = records, val = val)

@app.route('/contact', methods = ['POST', 'GET'])
def contact():

    try:
        connection = pymysql.connect(host=params['local_uri']['local_host'],
                             user=params['local_uri']['local_user'],
                             password=params['local_uri']['local_psd'],
                             database=params['local_uri']['local_database'])

        cursor = connection.cursor()
        if request.method == 'POST':
            name = request.form.get('user_name')
            email = request.form.get('user_email')
            phone = request.form.get('user_phone')
            message = request.form.get('user_message')

            print(name, email, phone, message, datetime.now())

            insert1 = f"INSERT INTO contacts(name, emailadd, phonon, message, dates) VALUES('{name}', '{email}', '{phone}', '{message}', '{datetime.now()}');"

            cursor.execute(insert1)
            connection.commit()

            mail.send_message(
                'new message from '+ name,
                sender = email,
                recipients = [params['gmail_user']],
                body = message + "\n" + phone
            )
            connection.close()

    except Exception as e:
        print(e)

    print("contact", val)
    return render_template('contact.html', params = params, val = val)


if __name__ == '__main__':
    app.run(debug=True)

