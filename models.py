from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask_login import UserMixin
from app import login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))





class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return '<User {}>'.format(self.username)



class Tovar(db.Model):


    id= db.Column(db.Integer, primary_key=True)
    type=db.Column(db.String(20), nullable=False)
    obj=db.Column(db.Float(precision=32, decimal_return_scale=None), default=0)
    pcs=db.Column(db.Integer, default=0)
    pcs_brak=db.Column(db.Integer, default=0)
    price=db.Column(db.Integer, default=0)



class Mater(db.Model):


    id=db.Column(db.Integer, primary_key=True)
    type=db.Column(db.String(40), nullable=False)
    obj=db.Column(db.Float(precision=32, decimal_return_scale=None), nullable=True)

    def __str__(self):
        return '{}'.format(self.type)


class Change(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    where = db.Column(db.String(100))
    who = db.Column(db.Integer, db.ForeignKey("user.id"))