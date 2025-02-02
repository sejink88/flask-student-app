from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, default=0)


with app.app_context():
    db.create_all()


# 학생 점수 조회 + HTML 페이지 렌더링
@app.route('/')
def index():
    students = Student.query.all()  # 모든 학생 불러오기
    return render_template('index.html', students=students)


# 학생 점수 변경 (폼에서 POST 요청 받기)
@app.route('/update_points', methods=['POST'])
def update_points():
    student_id = int(request.form['student_id'])
    points = int(request.form['points'])

    student = Student.query.get(student_id)
    if student:
        student.points += points
        db.session.commit()

    return redirect(url_for('index'))  # 변경 후 다시 메인 페이지로 이동


# 새로운 학생 추가
@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    new_student = Student(name=name, points=0)
    db.session.add(new_student)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
