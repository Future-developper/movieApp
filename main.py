from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import requests
API_KEY = "73fae39fe9ff5e126071ad4137d56201"
URL = "https://api.themoviedb.org/3/search/movie"
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3M2ZhZTM5ZmU5ZmY1ZTEyNjA3MWFkNDEzN2Q1NjIwMSIsIm5iZiI6MTcyMzYxODM2Ni44ODIxNTMsInN1YiI6IjY2YmM0YzdlMjY2YmFmZWYxNDhjN2U0MyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.ivc2tDb-m7EqAA_MD-MGL95c_ilim0mBnWPaYbUGJo0"
}
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///10-favourite-movies-database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

class RateMovieForm(FlaskForm):
    rating = DecimalField('Your Rating Out of 10 e.g. 7.5', validators=[DataRequired(), NumberRange(min=0, max=10)])
    review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Done')

class FindMovieForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


@app.route("/")
def home():
    all_movies = Movie.query.all()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    form = RateMovieForm()
    movie_id = request.args.get('id')
    movie_to_update = Movie.query.get(movie_id)
    if form.validate_on_submit():

        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie_to_update, form=form)


@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = FindMovieForm()
    if form.validate_on_submit():
        query_params = {'query': form.title.data, 'include_adult': True, 'language': 'en-US', 'page': 1}
        response = requests.get(URL, headers=headers, params=query_params)
        data = response.json()['results']
        movies = [(movie["original_title"], movie["release_date"]) for movie in data]
        return render_template('select.html', movies=movies)
    return render_template('add.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
