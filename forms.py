from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email, URL
from models import Student
from flask_login import current_user


class RegistrationForm(FlaskForm):
    first_name = StringField('Adı', validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Soyadı', validators=[DataRequired(), Length(min=2, max=30)])
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    student_number = StringField('Öğrenci Numarası', validators=[DataRequired(), Length(min=9, max=9)],
                                 render_kw={'aria-describedby': 'student_number_help'})
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


class ProfileForm(FlaskForm):
    first_name = StringField('Adı', validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Soyadı', validators=[DataRequired(), Length(min=2, max=30)])
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    student_number = StringField('Öğrenci Numarası', validators=[DataRequired(), Length(min=9, max=9)],
                                 render_kw={'aria-describedby': 'student_number_help'})
    password = PasswordField('Şifre')
    confirm_password = PasswordField('Şifreyi Onayla', validators=[EqualTo('password')])
    vize_project_upload_1 = FileField('Vize Projesi (Görsel)')
    vize_project_upload_2 = FileField('Vize Projesi (Cevap)')
    final_project_youtube_link = StringField('Final Projesi YouTube Linki')
    submit = SubmitField('Kaydet')

    def validate_password(self, password):
        # Eğer şifre alanı boşsa validasyonu geç
        if not password.data:
            return

        # Eğer şifre alanı doluysa ve değişmişse kontrol yap
        if password.data and password.data != current_user.password:
            # Length(min=6) validasyonu
            if len(password.data) < 6:
                raise ValidationError('Şifre en az 6 karakter olmalıdır.')

    def validate_username(self, username):
        # Sadece kullanıcı adı değişmişse kontrol yap
        if username.data != current_user.username:
            student = Student.query.filter_by(username=username.data).first()
            if student:
                raise ValidationError('Bu kullanıcı adı zaten alınmış. Lütfen başka bir kullanıcı adı seçin.')

    def validate_email(self, email):
        if email.data != current_user.email:
            student = Student.query.filter_by(email=email.data).first()
            if student:
                raise ValidationError('Bu e-posta adresi zaten kullanılıyor. Lütfen başka bir e-posta adresi seçin.')

    def validate_student_number(self, student_number):
        if student_number.data != current_user.student_number:
            student = Student.query.filter_by(student_number=student_number.data).first()
            if student:
                raise ValidationError('Bu öğrenci numarası zaten kullanılıyor. Lütfen başka bir numara seçin.')

    def validate_final_project_youtube_link(self, final_project_youtube_link):
        # Eğer final_project_youtube_link boş değilse URL validasyonu yap
        if final_project_youtube_link.data:
            if not URL(None, final_project_youtube_link):
                raise ValidationError('Geçerli bir YouTube URL girin.')
