from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import Student


class RegistrationForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=2, max=20)])
    student_number = StringField('Öğrenci Numarası', validators=[DataRequired(), Length(min=9, max=9)])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Şifreyi Onayla', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Kayıt Ol')

    def validate_username(self, username):
        student = Student.query.filter_by(username=username.data).first()
        if student:
            raise ValidationError('Bu kullanıcı adı zaten alınmış. Lütfen başka bir kullanıcı adı seçin.')

    def validate_student_number(self, student_number):
        student = Student.query.filter_by(student_number=student_number.data).first()
        if student:
            raise ValidationError('Bu öğrenci numarası zaten kullanılıyor. Lütfen başka bir numara seçin.')


class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Giriş Yap')
