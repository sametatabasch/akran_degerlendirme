import json

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import RegistrationForm, LoginForm, ProfileForm
from models import db, Student, Project, ProjectRating
from sqlalchemy import text
from tinify import tinify
from werkzeug.utils import secure_filename
import os
import helper

app = Flask(__name__)
app.config.from_pyfile('config.py')
# Tinify API anahtarını ayarlayın
tinify.key = app.config['TINIFY_KEY']

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Student, int(user_id))


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    if current_user.is_authenticated:

        return render_template('home.html')

    else:
        return redirect(url_for('login'))


@app.route('/rate_final_projects/')
def rate_final_projects():
    if current_user.is_authenticated:

        # Öğrencinin verdiği puanları ve projeleri al
        student_ratings = ProjectRating.query.filter_by(student_id=current_user.id).all()

        # Projeleri al
        projects = Project.query.filter_by(tag="final").all()

        # Projelerle ilişkilendirilmiş puanları içeren bir sözlük oluştur
        project_ratings = {rating.project_id: rating.ratings for rating in student_ratings}

        # Projeleri ve öğrencinin verdiği puanları template'e geçir
        return render_template('final.html', projects=projects, project_ratings=project_ratings)

    else:
        return redirect(url_for('login'))


def compress_and_save_image(file, username):
    try:
        # Güvenli dosya adını oluştur
        filename = secure_filename(file.filename)

        # Kullanıcı adında bir dizin oluştur
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
        os.makedirs(user_folder, exist_ok=True)

        # Resmi sıkıştır ve dosyayı kaydet
        source = tinify.from_buffer(file.read())
        source.to_file(os.path.join(user_folder, filename))

        print(f"Resim sıkıştırma başarılı. Yeni dosya: {filename}")
        return filename
    except tinify.AccountError as e:
        flash(f'Hesap hatası: {e}', 'danger')
        return False
    except tinify.ClientError as e:
        flash(f'Geçersiz istek hatası: {e}', 'danger')
        return False
    except tinify.ServerError as e:
        flash(f'Sunucu hatası: {e}', 'danger')
        return False
    except tinify.ConnectionError as e:
        flash(f'İletişim hatası: {e}', 'danger')
        return False
    except Exception as e:
        flash(f'İşlem hatası: {e}', 'danger')
        return False


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()

    if form.validate_on_submit():
        # Formdan gelen bilgileri kullanarak öğrenci bilgilerini güncelle
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.student_number = form.student_number.data

        # Eğer yeni şifre girilmişse, şifreyi güncelle
        if form.password.data:
            current_user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Eğer vize projesi dosyaları yüklenmişse, projeleri kaydet
        if form.vize_project_upload_1.data and form.vize_project_upload_2.data:
            vize_project_file_1 = form.vize_project_upload_1.data
            vize_project_file_2 = form.vize_project_upload_2.data

            filename_1 = compress_and_save_image(vize_project_file_1, current_user.username)
            filename_2 = compress_and_save_image(vize_project_file_2, current_user.username)

            if not filename_1 and not filename_2:
                return redirect(url_for('profile'))
            # Kontrol etmek için öğrencinin aynı tag'deki projelerini al
            existing_project = Project.query.filter_by(student_id=current_user.id, tag='vize').first()

            if existing_project:
                # Öğrencinin zaten aynı tag'deki bir projesi varsa, ilk projeyi güncelle
                existing_project.data = json.dumps({
                    'image': f"{app.config['UPLOAD_FOLDER']}/{current_user.username}/{filename_1}",
                    'image_answer': f"{app.config['UPLOAD_FOLDER']}/{current_user.username}/{filename_2}"})
            else:
                # Veritabanına vize projelerini kaydet
                new_vize_project = Project(
                    student_id=current_user.id,
                    data=json.dumps({
                        'image': f"{app.config['UPLOAD_FOLDER']}/{current_user.username}/{filename_1}",
                        'image_answer': f"{app.config['UPLOAD_FOLDER']}/{current_user.username}/{filename_2}"}),
                    tag='vize'
                )
                db.session.add(new_vize_project)

        # Eğer final projesi YouTube linki verilmişse, linki kaydet
        if form.final_project_youtube_link.data:
            # Kontrol etmek için öğrencinin aynı tag'deki projelerini al
            existing_project = Project.query.filter_by(student_id=current_user.id, tag='final').first()
            if existing_project:
                print("proje var güncellenecek")
                # Öğrencinin zaten aynı tag'deki bir projesi varsa, ilk projeyi güncelle
                video_id = helper.get_youtube_id(form.final_project_youtube_link.data)
                existing_project.data = json.dumps({
                    'youtube_video_id': video_id
                })
            else:
                print("proje yok eklenecek")
                # Eğer öğrencinin aynı tag'de bir projesi yoksa, yeni bir proje oluştur
                video_id = helper.get_youtube_id(form.final_project_youtube_link.data)
                print("Video id:", video_id)
                new_final_project = Project(
                    student_id=current_user.id,
                    data=json.dumps({
                        'youtube_video_id': video_id
                    }),
                    tag='final'
                )
                db.session.add(new_final_project)

        # Veritabanına yapılan değişiklikleri kaydet
        db.session.commit()

        flash('Profil başarıyla güncellendi!', 'success')
        return redirect(url_for('profile'))

    if form.errors:
        flash('Formda hatalı veri var Form hatalarını kontrol edin', 'danger')

    # Formun ilk defa gösterilmesi veya geçersiz bir durumda
    return render_template('profile.html', form=form)


@app.route('/leaderboard')
@login_required
def leaderboard():
    # Öğrencinin verdiği puanları ve projeleri al
    student_ratings = ProjectRating.query.filter_by(student_id=current_user.id).all()

    # Projeleri al
    projects = Project.query.order_by(Project.sum_rating.desc()).all()

    # Projeleri ve öğrencinin verdiği puanları template'e geçir
    return render_template('leaderboard.html', projects=projects)


@app.route('/rate_project/<int:project_id>', methods=['POST'])
@login_required
def rate_project(project_id):
    ratings = json.loads(request.form.get('ratings'))

    # Öğrencinin daha önce bu projeye puan verip vermediğini kontrol et
    existing_rating = ProjectRating.query.filter_by(student_id=current_user.id, project_id=project_id).first()

    if existing_rating:
        existing_rating.ratings = json.dumps(ratings)
    else:
        new_rating = ProjectRating(student_id=current_user.id, project_id=project_id, ratings=json.dumps(ratings))
        db.session.add(new_rating)

    db.session.commit()

    # Proje ortalama puanını güncelle
    project = Project.query.get(project_id)
    project.update_rating()

    return jsonify({'success': True})


@app.route('/project_ratings')
def project_ratings():
    # Tüm projeleri ve puanları al
    projects = Project.query.order_by(Project.sum_rating.desc()).all()

    return render_template('project_ratings.html', projects=projects)


@app.route('/student_list')
def student_list():
    students = Student.query.order_by(Student.student_number).all()
    return render_template('student_list.html', students=students)


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
            return redirect(url_for('profile'))
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
        student = Student(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            student_number=form.student_number.data,
            password=hashed_password
        )
        db.session.add(student)
        db.session.commit()

        flash('Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.capitalize()}: {error}', 'danger')

    return render_template('register.html', title='Kayıt Ol', form=form)


@app.route('/project_ratings_freq')
def project_ratings_freq():
    # SQL sorgusunu doğrudan çalıştır
    query = """
            SELECT
              s.student_number,
              s.username,
              COUNT(CASE WHEN pr.rating = 1 THEN 1 END) as rating_1,
              COUNT(CASE WHEN pr.rating = 2 THEN 1 END) as rating_2,
              COUNT(CASE WHEN pr.rating = 3 THEN 1 END) as rating_3,
              COUNT(CASE WHEN pr.rating = 4 THEN 1 END) as rating_4,
              COUNT(CASE WHEN pr.rating = 5 THEN 1 END) as rating_5,
              COUNT(CASE WHEN pr.rating = 6 THEN 1 END) as rating_6,
              COUNT(CASE WHEN pr.rating = 7 THEN 1 END) as rating_7,
              COUNT(CASE WHEN pr.rating = 8 THEN 1 END) as rating_8,
              COUNT(CASE WHEN pr.rating = 9 THEN 1 END) as rating_9,
              COUNT(CASE WHEN pr.rating = 10 THEN 1 END) as rating_10
            FROM
              project_rating pr
            INNER JOIN
              student s ON s.id = pr.student_id
            GROUP BY
              pr.student_id;
        """

    # Sorguyu çalıştır ve sonuçları al
    rating_counts = db.session.execute(text(query)).fetchall()
    return render_template('project_ratings_freq.html', students=rating_counts)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.template_filter('json_decode')
def json_decode(value):
    """
    jinja2 templetelerde json_decode kullanabilmek için filtre ekliyoruz
    örnek kullanım final.html de
    {% set project_data = project.data|safe|json_decode %}
    :param value:
    :return:
    """
    return json.loads(value)


if __name__ == '__main__':
    app.run(debug=True)
