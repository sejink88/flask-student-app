from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # 마이그레이션 라이브러리 추가
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # 🚀 Flask-Migrate 활성화

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    class_number = db.Column(db.Integer, nullable=False)  # 반 추가 ✅
    points = db.Column(db.Integer, default=0)

@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students, admin=False)

@app.route('/class/<int:class_number>')
def class_students(class_number):
    students = Student.query.filter_by(class_number=class_number).all()
    return render_template('index.html', students=students, admin=False, selected_class=class_number)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get("password")
        if password == "admin123":  # 🔒 관리자 암호 (변경 가능)
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return "잘못된 비밀번호입니다. <a href='/admin-login'>다시 시도</a>"
    return render_template('admin_login.html')

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))  # 로그인 안 했으면 로그인 페이지로 이동
    students = Student.query.all()
    return render_template('index.html', students=students, admin=True, selected_class=None)

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/add-student', methods=['POST'])
def add_student():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))  # 관리자만 학생 추가 가능
    name = request.form.get("name")
    class_number = request.form.get("class_number")
    if name and class_number:
        new_student = Student(name=name, class_number=int(class_number), points=0)
        db.session.add(new_student)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/student/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify({'name': student.name, 'points': student.points, 'class_number': student.class_number})

@app.route('/student/<int:student_id>/add', methods=['POST'])
def add_points(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    data = request.get_json()
    student.points += data.get('points', 0)
    db.session.commit()
    return jsonify({'message': 'Points added successfully', 'points': student.points})

@app.route('/student/<int:student_id>/subtract', methods=['POST'])
def subtract_points(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    data = request.get_json()
    student.points -= data.get('points', 0)
    db.session.commit()
    return jsonify({'message': 'Points subtracted successfully', 'points': student.points})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        os.system("flask db upgrade")  # 🚀 서버 시작 시 자동으로 마이그레이션 실행
    app.run(debug=True)
