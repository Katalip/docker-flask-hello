from flask import Flask, request, jsonify, abort, redirect, url_for, render_template, send_file, flash
app = Flask(__name__)

from joblib import load
import numpy as np
import pandas as pd

knn = load('knn.joblib')

@app.route('/')
def hello_world():
    print(1+8)
    return '<p style="color: green">Hello World! My Friend!</p>'

@app.route('/badreq')
def bad_request():
    abort(400)


@app.route('/age/<ag>')
def age(ag):
    return 'Your age: %s' % ag

@app.route('/go/<direction>')
def dir(direction):
    return f'Go {direction}'

@app.route('/mean/<nums>')
def get_mean(nums):
    nums = [float(i) for i in nums.split(',')]
    return str(sum(nums)/(len(nums)))

@app.route('/iris/<params>')
def get_prediction(params):
    params = [float(i) for i in params.split(',')]
    params = np.array(params).reshape(1,-1)
    pred = knn.predict(params)
    return str(pred)

@app.route('/show_image')
def show_img():
    return '<img src="/static/versi.jpg">'

@app.route('/iris_post', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        params = [float(i) for i in data['flower'].split(',')]
        params = np.array(params).reshape(1,-1)
        pred = {'class':str(knn.predict(params)[0])}
    except:
        return redirect(url_for('bad_request'))

    return jsonify(pred)

from flask_wtf import FlaskForm
from wtforms import StringField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired

class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    file = FileField('file', validators=[FileRequired()])

app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

from werkzeug.utils import secure_filename
import os

@app.route('/submit', methods=('GET', 'POST'))
def submit():
    form = MyForm()
    if form.validate_on_submit():
        f = form.file.data
        filename = form.name.data + '.csv'
        # filename = secure_filename(f.filename)
        # f.save(os.path.join(
        #     filename
        #     #app.instance_path, 'root/files', filename
        # ))

        df = pd.read_csv(f, header=None)
        predict = knn.predict(df)

        res = pd.DataFrame(predict)
        res.to_csv('predict_' + filename, index=False)

        out = 'predict_' + filename
        # print(df.head())
        return send_file(out,
                     mimetype='text/csv',
                     attachment_filename=out,
                     as_attachment=True)
    return render_template('submit.html', form=form)

@app.route('/success')
def success():
    return 'Success!'


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'upl_' + filename))
            return 'file uploaded'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''