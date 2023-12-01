from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import RegistrationForm, LoginForm
from models import db, Student, Project, Image, ProjectRating

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'gizli_anahtar'

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    if current_user.is_authenticated:
        projects = Project.query.all()
        return render_template('home.html', projects=projects)
    else:
        return redirect(url_for('login'))


@app.route('/rate_project/<int:project_id>', methods=['POST'])
@login_required
def rate_project(project_id):
    rating = int(request.form.get('rating'))

    # Öğrencinin daha önce bu projeye puan verip vermediğini kontrol et
    existing_rating = ProjectRating.query.filter_by(student_id=current_user.id, project_id=project_id).first()

    if existing_rating:
        existing_rating.rating = rating
    else:
        new_rating = ProjectRating(student_id=current_user.id, project_id=project_id, rating=rating)
        db.session.add(new_rating)

    db.session.commit()

    # Proje ortalama puanını güncelle
    project = Project.query.get(project_id)
    project.update_average_rating()

    return jsonify({'success': True})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        student = Student.query.filter_by(username=form.username.data).first()

        if student and bcrypt.check_password_hash(student.password, form.password.data):
            login_user(student)
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Giriş başarısız. Lütfen kullanıcı adı ve şifrenizi kontrol edin.', 'danger')

    return render_template('login.html', title='Giriş Yap', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        student = Student(username=form.username.data, student_number=form.student_number.data,
                          password=hashed_password)
        db.session.add(student)
        db.session.commit()

        flash('Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.capitalize()}: {error}', 'danger')

    return render_template('register.html', title='Kayıt Ol', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)