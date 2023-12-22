from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from models import Student


class RegistrationForm(FlaskForm):
    first_name = StringField('Adı', validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Soyadı', validators=[DataRequired(), Length(min=2, max=30)])
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    student_number = StringField('Öğrenci Numarası', validators=[DataRequired(), Length(min=9, max=9)], render_kw={'aria-describedby': 'student_number_help'})
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Şifreyi Onayla', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Kayıt Ol')

    def validate_username(self, username):
        student = Student.query.filter_by(username=username.data).first()
        if student:
            raise ValidationError('Bu kullanıcı adı zaten alınmış. Lütfen başka bir kullanıcı adı seçin.')

    def validate_email(self, email):
        student = Student.query.filter_by(email=email.data).first()
        if student:
            raise ValidationError('Bu e-posta adresi zaten kullanılıyor. Lütfen başka bir e-posta adresi seçin.')

    def validate_student_number(self, student_number):
        student = Student.query.filter_by(student_number=student_number.data).first()
        if student:
            raise ValidationError('Bu öğrenci numarası zaten kullanılıyor. Lütfen başka bir numara seçin.')


class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Giriş Yap')
