from flask import Flask, request, jsonify, render_template
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

# 📌 학생 목록 조회 (웹 페이지)
@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)

# 📌 특정 학생 점수 조회 (API)
@app.route('/student/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify({'name': student.name, 'points': student.points})

# 📌 점수 추가 (API)
@app.route('/student/<int:student_id>/add', methods=['POST'])
def add_points(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    data = request.get_json()
    student.points += data.get('points', 0)
    db.session.commit()
    return jsonify({'message': 'Points added successfully', 'points': student.points})

# 📌 점수 차감 (API)
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
    app.run(debug=True)
