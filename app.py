from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
login = LoginManager(app)
login.login_view = 'login'
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
static_folder = 'static'


# =======================================================
# ROUTES
# =======================================================


from datetime import datetime

from flask import render_template, redirect, flash, url_for, request, jsonify
from forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from models import User, Tovar, Mater, Change
from werkzeug.urls import url_parse
from forms import RegistrationForm, EditProfileForm, TovarNewForm, MaterNewForm, \
    MaterAdd, TovarAdd, MaterDel, TovarSell, FactAdd, BrakAdd, BrakDel, TovarTypeDel



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# Эта функция позволит создать новый материал и сохранить его в базе данных.
@app.route('/addtypemat', methods=['GET', 'POST'])
def addtypemat():
    form = MaterNewForm()
    if form.validate_on_submit():
        newmat = Mater(type=form.type.data, obj=form.obj.data)
        db.session.add(newmat)
        db.session.commit()
        return redirect(url_for('mat'))
    else:
        return render_template('addtypemat.html', form=form)


# Эта функция добавляет материалы в склад.
@app.route('/addmat', methods=['GET', 'POST'])
def addmat():
    form = MaterAdd()
    if form.validate_on_submit():
        z = form.type.data
        z.obj += float(form.obj.data)
        db.session.commit()
        return redirect(url_for('mat'))
    else:
        return render_template('addmat.html', form=form)


# Эта функция выводит остатки материала на складе.
@app.route('/mat')
def mat():
    return render_template('mat.html', items=Mater.query.order_by(Mater.type).all())


# Эта функция выполняет списание материала, проверку наличия такого количества
@app.route('/delmat', methods=['GET', 'POST'])
def delmat():
    form = MaterDel()
    if form.validate_on_submit():
        z = form.type.data
        if float(form.obj.data) <= z.obj:
            z.obj -= float(form.obj.data)
            db.session.commit()
            return redirect(url_for('mat'))
        else:
            x = 'Нельзя списать больше наличия - ' + str(z.obj) + ' куб.м.'
            flash(x)
            return render_template('delmat.html', form=form)

    else:
        return render_template('delmat.html', form=form)


# Эта функция позволит создать новый товар/тип и сохранить ее в базе данных.
@app.route('/addtypetov', methods=['GET', 'POST'])
def addtypetov():
    form = TovarNewForm()
    if form.validate_on_submit():
        newtov = Tovar(type=form.type.data, obj=form.obj.data)
        db.session.add(newtov)
        db.session.commit()
        return redirect(url_for('tov'))
    else:
        return render_template('addtypetov.html', form=form)


# Эта функция удаляет тип товара!!!
@app.route('/deltypetov', methods=['GET', 'POST'])
def deltypetov():
    form = TovarTypeDel()
    if form.validate_on_submit():
        if form.ja_ne_debil_i_ponial.data is True:
            x=form.type.data
            z=x.type
            ob = Tovar.query.filter_by(type=z).first()
            db.session.delete(ob)
            db.session.commit()
            return redirect(url_for('tov'))
        else:
            flash('Подтвердите что вы поняли смысл операции!')
            return render_template('deltypetov.html', form=form)
    else:
        return render_template('deltypetov.html', form=form)


# Эта функция позволит добавить товар сохранить его в базе данных.
@app.route('/addtov', methods=['GET', 'POST'])
def addtov():
    form = TovarAdd()
    if form.validate_on_submit():
        z = form.type.data
        z.pcs += form.pcs.data
        db.session.commit()
        return redirect(url_for('tov'))
    else:
        return render_template('addtov.html', form=form)


# Эта функция выполняет отгрузку товара, проверку наличия такого количества
@app.route('/selltov', methods=['GET', 'POST'])
def selltov():
    form = TovarSell()
    if form.validate_on_submit():
        z = form.type.data
        if form.pcs.data <= z.pcs:
            z.pcs -= form.pcs.data
            db.session.commit()
            return redirect(url_for('tov'))
        else:
            x = 'Нельзя отгрузить больше наличия - ' + str(z.pcs) + ' шт.'
            flash(x)
            return render_template('selltov.html', form=form)

    else:
        return render_template('selltov.html', form=form)


# Эта функция выводит остатки товара на складе.
@app.route('/tov')
def tov():
    return render_template('tov.html', items=Tovar.query.order_by(Tovar.type).all())


# Эта функция выводит остатки товара и материала на складе.
@app.route('/skl')
def skl():
    return render_template('skl.html', items=Tovar.query.order_by(Tovar.type).all(), items2=Mater.query.order_by(Mater.type).all())


# Эта функция выполняет производство товара, проверку наличия такого количества
# материала, добавление на склад и списание материала
@app.route('/factadd', methods=['GET', 'POST'])
def factadd():
    form = FactAdd()
    if form.validate_on_submit():
        x = form.type.data

        z = x.obj

        # получаем объем изделия
        z1 = round(z, 7) * form.pcs.data

        # получаем объем партии
        d = Mater.query.filter_by(type='Лес столярный').first()
        # Получаем наличие материала
        if d.obj >= z1:
            d.obj = round((d.obj - z1), 7)
            x.pcs += form.pcs.data
            db.session.commit()
            return redirect(url_for('skl'))
        else:
            x = 'Нельзя произвести больше чем есть материала, добавьте материал'
            flash(x)
            return render_template('addmat.html', form=form)
    else:
        return render_template('factadd.html', form=form)


# Эта функция выполняет производство БРАКА, проверку наличия такого количества
# материала, добавление на склад и списание материала
@app.route('/brakadd', methods=['GET', 'POST'])
def brakadd():
    form = BrakAdd()
    if form.validate_on_submit():
        x = form.type.data
        z = x.obj
        # получаем объем изделия
        z1 = round(z, 7) * form.pcs_brak.data
        # получаем объем партии
        d = Mater.query.filter_by(type='Лес столярный').first()
        # Получаем наличие материала
        if d.obj >= z1:
            d.obj = round((d.obj - z1), 7)
            x.pcs_brak += form.pcs_brak.data
            db.session.commit()
            return redirect(url_for('skl'))
        else:
            x = 'Нельзя произвести больше чем есть материала'
            flash(x)
            return render_template('brakadd.html', form=form)
    else:
        return render_template('brakadd.html', form=form)



@app.route('/delbrak', methods=['GET', 'POST'])
def delbrak():
    form = BrakDel()
    if form.validate_on_submit():
        z = form.type.data
        if form.pcs_brak.data <= z.pcs_brak:
            z.pcs_brak -= form.pcs_brak.data
            db.session.commit()
            return redirect(url_for('skl'))
        else:
            x = 'Нельзя отгрузить больше наличия - ' + str(z.pcs) + ' шт.'
            flash(x)
            return render_template('delbrak.html', form=form)

    else:
        return render_template('delbrak.html', form=form)



# Дальше идут функции авторизации и тд
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html", title='Home Page')


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    return render_template('user.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


