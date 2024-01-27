from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import json

db = SQLAlchemy()


class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    student_number = db.Column(db.String(9), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    projects = db.relationship('Project', backref='student', lazy=True, cascade='all, delete-orphan')
    project_ratings = db.relationship('ProjectRating', backref='student', lazy=True, cascade='all, delete-orphan')

    def get_projects_by_tag(self, tag):
        if tag == 'vize':
            return Project.query.filter_by(student_id=self.id, tag='vize').first()
        elif tag == 'final':
            return Project.query.filter_by(student_id=self.id, tag='final').first()
        else:
            return []


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    sum_rating = db.Column(db.Float, default=0.0)
    data = db.Column(db.Text, nullable=False)
    tag = db.Column(db.String(10), nullable=False)
    ratings = db.relationship('ProjectRating', backref='project', lazy=True, cascade='all, delete-orphan')

    def update_rating(self):
        """
                Her bir projeye verilmiş alt oyların ortalamalarını alıp toplayarak projenin puanını hesaplar
                :return:
        """
        ratings = self.ratings

        if ratings:
            total_ratings = 0
            for rat in ratings:
                ratings_values = json.loads(rat.ratings).values()
                sum = 0
                for r in ratings_values:
                    sum += float(r)
                total_ratings += sum / len(ratings_values)

            self.sum_rating = total_ratings
        else:
            self.sum_rating = 0.0

        db.session.commit()


class ProjectRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    ratings = db.Column(db.Text, nullable=False)

    def update_project_rating(self):
        project = Project.query.get(self.project_id)
        project.update_rating()
