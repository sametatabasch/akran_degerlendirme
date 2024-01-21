from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, HiddenField
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
    id = HiddenField("id", validators=[DataRequired()])
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

    def validate(self, extra_validators=None):
        print("Validate Çalıştı")
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        result = True
        #
        # Validate username
        #
        err = list(self.username.errors)
        student = Student.query.get(self.id.data)
        other_student = Student.query.filter_by(username=self.username.data).first()
        if other_student and student.id != other_student.id:
            err.append('Bu kullanıcı adı zaten alınmış. Lütfen başka bir kullanıcı adı seçin.')
            self.username.errors = tuple(err)
            result = False
        #
        # Validate password
        #
        err = list(self.password.errors)
        if self.password.data:
            # Eğer şifre alanı doluysa ve değişmişse kontrol yap
            if self.password.data:
                # Length(min=6) validasyonu
                if len(self.password.data) < 6:
                    err.append("'Şifre en az 6 karakter olmalıdır.'")
            self.password.errors = tuple(err)
            result = False
        #
        # Validate email
        #
        err = list(self.email.errors)
        student = Student.query.get(self.id.data)
        other_student = Student.query.filter_by(email=self.email.data).first()
        if student.id != other_student.id:
            err.append('Bu email zaten alınmış. Lütfen başka bir email seçin.')
            self.email.errors = tuple(err)
            result = False

        #
        # Validate student_number
        #
        err = list(self.student_number.errors)
        student = Student.query.get(self.id.data)
        other_student = Student.query.filter_by(student_number=self.student_number.data).first()
        if student.id != other_student.id:
            err.append('Bu öğrenci numarası zaten alınmış. Lütfen başka bir öğrenci numarası seçin.')
            self.student_number.errors = tuple(err)
            result = False
        #
        # Validate final_project_youtube_link
        #
        err = list(self.final_project_youtube_link.errors)
        # Eğer final_project_youtube_link boş değilse URL validasyonu yap
        if self.final_project_youtube_link.data:
            if not URL(None, self.final_project_youtube_link):
                err.append('Geçerli bir YouTube URL girin.')
                self.final_project_youtube_link.errors = tuple(err)
                result = False
        return result
