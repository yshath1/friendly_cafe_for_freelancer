from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
import random
from datetime import date
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os
from flask_gravatar import Gravatar
from form import CafeForm, EditCafeForm

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = "SECRET_KEY"
# app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)
##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///cafes.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONFIGURE TABLE
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))


##Cafe TABLE Configuration
class NewCafes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    cafe_price = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.String(250), nullable=False)
    has_wifi = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.String(250), nullable=False)
    can_take_calls = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    cafe_rating = db.Column(db.String(250), nullable=True)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route('/')
def home():

    cafes = db.session.query(Cafe).all()

    return render_template("index.html", cafes=cafes)


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    """Add a new entry to db"""
    form = CafeForm()
    if form.validate_on_submit():
        print(form.name.data)
        add_new = NewCafes(
            name=form.name.data,
            map_url=form.cafe_location.data,
            cafe_price=form.cafe_price.data,
            img_url=form.img_url.data,
            seats=form.seats.data,
            cafe_rating=form.cafe_rating.data,
            has_wifi=form.wifi_rating.data,
            has_sockets=form.power_socket.data,
            can_take_calls=form.can_take_calls.data,
            location=form.address.data,
            has_toilet=form.toilet.data
        )
        db.session.add(add_new)
        db.session.commit()
        return redirect(url_for("index.html"))
    return render_template('add.html', form=form)


@app.route('/edit/<num>', methods=['GET', 'POST'])
def edit(num):
    """update price of the cafe search db with the current id param"""
    to_int = int(num)
    form = EditCafeForm()
    if form.validate_on_submit():
        change = Cafe.query.filter_by(id=to_int).first()
        print(change.coffee_price)
        change.coffee_price = form.price.data
        db.session.commit()

        return redirect(url_for('home'))

    return render_template("edit.html", form=form)


@app.route("/search", methods=['Post'])
def get_cafe_at_location():
    """search db with location param"""
    query_location = request.form.get("address")

    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return render_template("cafe.html",cafe=cafe)
    else:
        flash("Location Doesn't exist yet")
        return redirect(url_for('home'))

@app.route("/listing")
def listing():
    """return all cafes in db"""
    cafes = db.session.query(Cafe).all()
    return render_template("List_cafe.html",cafes=cafes)
@app.route("/random")
def random_get():
    """return random cafe in db"""
    cafes = db.session.query(Cafe).all()

    random_cafe = random.choice(cafes)
    return render_template("Random.html",cafe=random_cafe)
@app.route("/contact")
def contact():
    """contact page"""
    return render_template("contact.html")
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
