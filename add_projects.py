import os
from flask import Flask
from models import db, Student, Project, Image

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'gizli_anahtar'

db.init_app(app)

def add_projects_to_database():
    projects_dir = os.path.join('static', 'projects')  # projects klasörünün tam yolunu belirtiyoruz


    for student_folder in os.listdir(projects_dir):
        student_folder_path = os.path.join(projects_dir, student_folder)

        if os.path.isdir(student_folder_path):
            # Check if the project already exists in the database
            existing_project = Project.query.filter_by(owner_name=student_folder).first()

            if not existing_project:
                new_project = Project(owner_name=student_folder)
                db.session.add(new_project)
                db.session.commit()

                project_id = new_project.id

                # Add images to the database
                for image_filename in os.listdir(student_folder_path):
                    image_path = os.path.join(student_folder_path, image_filename)

                    if os.path.isfile(image_path) and image_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        new_image = Image(project_id=project_id, filename=image_filename)
                        db.session.add(new_image)

                db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        add_projects_to_database()
