from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    student_number = db.Column(db.String(9), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    project_ratings = db.relationship('ProjectRating', backref='student', lazy=True)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(50), nullable=False)
    average_rating = db.Column(db.Float, default=0.0)
    images = db.relationship('Image', backref='project', lazy=True)
    ratings = db.relationship('ProjectRating', backref='project', lazy=True)

    def update_average_rating(self):
        # todo fonksiyon adını değiş
        if self.ratings:
            total_ratings = sum([rating.rating for rating in self.ratings])
            self.average_rating = total_ratings
        else:
            self.average_rating = 0.0

        db.session.commit()


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)


class ProjectRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def update_project_average_rating(self):
        project = Project.query.get(self.project_id)
        project.update_average_rating()
