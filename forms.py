from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, \
    IntegerField, DecimalField, FloatField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from models import User, Tovar, Mater
from wtforms.ext.sqlalchemy.fields import QuerySelectField


# Этот класс вводит новую форму, для нормального приема ',' and '.'
class MyFloatField(FloatField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(',', '.'))
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid float value'))


class EditProfileForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    about_me = TextAreaField('Обо мне', validators=[Length(min=0, max=140)])
    submit = SubmitField('Подтвердить')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Используйте другое имя')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Выберите другое имя')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Выберите другой email')


# Добавление нового вида товара
class TovarNewForm(FlaskForm):
    type = StringField('Тип', validators=[DataRequired()])
    obj = MyFloatField('Объем 1 шт. в куб.м.', validators=[DataRequired()])
    submit = SubmitField('Добавить')


    # Функция должна быть подключена в случае, если 2 товара не могут иметь 1 название!!!!!
    def validate_type(self, type):
        type = Tovar.query.filter_by(type=type.data).first()
        if type is not None:
            raise ValidationError('Этот тип товара уже добавлен')



# Добавление товара
class TovarAdd(FlaskForm):
    type = QuerySelectField('Тип товара', query_factory=lambda: Tovar.query.order_by(Tovar.type).all(),
                            get_label="type")
    pcs = IntegerField('Количество', validators=[DataRequired()])
    submit = SubmitField('Добавить')


# Удаление типа товара
class TovarTypeDel(FlaskForm):
    type = QuerySelectField('Тип товара', query_factory=lambda: Tovar.query.order_by(Tovar.type).all(),
                            get_label="type")
    ja_ne_debil_i_ponial = BooleanField('Я осознаю, что тип товара, складские остатки этого типа товара, будут безвозвратно удалены')
    submit = SubmitField('Добавить')


# Функция отгрузки товара
class TovarSell(FlaskForm):
    type = QuerySelectField('Тип товара', query_factory=lambda: Tovar.query.order_by(Tovar.type).all(),
                            get_label="type")
    pcs = IntegerField('Количество', validators=[DataRequired()])
    # text=TextAreaField('Обоснование продажи', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Продать')


# Добавление нового типа материала с возможностью ввода начального значения
class MaterNewForm(FlaskForm):
    type = StringField('Тип', validators=[DataRequired()])
    obj = MyFloatField('Объем в куб.м.', default=0)
    submit = SubmitField('Добавить')

    def validate_type(self, type):
        type = Mater.query.filter_by(type=type.data).first()
        if type is not None:
            raise ValidationError('Этот тип материала уже добавлен')


# Добавление материала
class MaterAdd(FlaskForm):
    type = QuerySelectField('Тип материала', query_factory=lambda: Mater.query.order_by(Mater.type).all(),
                            get_label="type")
    obj = MyFloatField('Объем в куб.м.', validators=[DataRequired()])
    submit = SubmitField('Добавить')


# Списание материала
class MaterDel(FlaskForm):
    type = QuerySelectField('Тип материала', query_factory=lambda: Mater.query.order_by(Mater.type).all(),
                            get_label="type")
    obj = MyFloatField('Объем в куб.м.', validators=[DataRequired()])
    # text=TextAreaField('Обоснование списания', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Списать')


# Функция производства товара
class FactAdd(FlaskForm):
    type = QuerySelectField('Тип товара', query_factory=lambda: Tovar.query.order_by(Tovar.type).all(),
                            get_label="type")
    pcs = IntegerField('Количество', validators=[DataRequired()])
    # text=TextAreaField('Обоснование продажи', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Добавить')


# Функция производства БРАКА
class BrakAdd(FlaskForm):
    type = QuerySelectField('Тип товара', query_factory=lambda: Tovar.query.order_by(Tovar.type).all(),
                            get_label="type")
    pcs_brak = IntegerField('Количество испорченного', validators=[DataRequired()])
    # text=TextAreaField('Обоснование продажи', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Добавить')

# Функция списания БРАКА
class BrakDel(FlaskForm):
    type = QuerySelectField('Тип товара', query_factory=lambda: Tovar.query.order_by(Tovar.type).all(),
                            get_label="type")
    pcs_brak = IntegerField('Количество', validators=[DataRequired()])
    # text=TextAreaField('Обоснование продажи', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Списать')