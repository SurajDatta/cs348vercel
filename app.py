# app.py
from flask import Flask, render_template, request, redirect, url_for
from models import db, Student, Meeting, Room, Club, meeting_organizers
from datetime import datetime
from sqlalchemy import func
import traceback

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    meetings = Meeting.query.all()
    students = Student.query.all()  # Fetch all students
    return render_template('index.html', meetings=meetings, students=students)


@app.route('/add_meeting', methods=['GET', 'POST'])
def add_meeting():
    if request.method == 'POST':
        try:
            date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            time = datetime.strptime(request.form['time'], '%H:%M').time()
            description = request.form['description']
            duration = request.form['duration']
            organizer_ids = request.form.getlist('organizers')  # Retrieve selected organizer IDs

            # Create the meeting and add organizers
            meeting = Meeting(date=date, time=time, description=description, duration=duration)
            meeting.organizers = [Student.query.get(id) for id in organizer_ids]
            
            db.session.add(meeting)
            db.session.commit()
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()  # Roll back in case of error
            print(f"Error occurred: {e}")  # Print error to console for debugging
            return "An error occurred while adding the meeting."

    # Fetch all students for the organizers dropdown
    students = Student.query.all()
    return render_template('add_meeting.html', students=students)

# Edit meeting route in app.py
@app.route('/edit_meeting/<int:meeting_id>', methods=['GET', 'POST'])
def edit_meeting(meeting_id):
    meeting = Meeting.query.get(meeting_id)
    if request.method == 'POST':
        try:
            # Update meeting fields
            meeting.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            meeting.time = datetime.strptime(request.form['time'], '%H:%M').time()  # Adjusted to '%H:%M'

            meeting.description = request.form['description']
            meeting.duration = int(request.form['duration'])

            # Get selected organizers
            organizer_ids = request.form.getlist('organizers')
            meeting.organizers = [Student.query.get(id) for id in organizer_ids]

            db.session.commit()
            return redirect(url_for('index'))
        
        except Exception as e:
            db.session.rollback()
            print("Error occurred while editing the meeting:")
            print(e)
            return f"An error occurred while editing the meeting: {str(e)}"
    
    students = Student.query.all()
    return render_template('edit_meeting.html', meeting=meeting, students=students)


@app.route('/delete_meeting/<int:meeting_id>')
def delete_meeting(meeting_id):
    meeting = Meeting.query.get(meeting_id)
    db.session.delete(meeting)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        new_student = Student(name=name)
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('add_student.html')

@app.route('/report', methods=['GET'])
def report():
    # Retrieve query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    room_id = request.args.get('room')
    club_id = request.args.get('club')

    # Initialize statistics
    avg_duration = avg_invited = avg_accepted = avg_attendance_rate = 0

    # Build query
    query = Meeting.query

    # Apply date filters if start_date and end_date are provided
    if start_date:
        query = query.filter(Meeting.date >= start_date)
    if end_date:
        query = query.filter(Meeting.date <= end_date)
    
    # Apply room and club filters if provided
    if room_id:
        query = query.filter(Meeting.room_id == room_id)
    if club_id:
        query = query.filter(Meeting.club_id == club_id)

    # Execute the query
    meetings = query.all()

    # Calculate statistics if there are results
    if meetings:
        total_duration = sum(meeting.duration for meeting in meetings)
        total_invited = sum(meeting.invited_students for meeting in meetings)
        total_accepted = sum(meeting.accepted_invitations for meeting in meetings)

        avg_duration = total_duration / len(meetings)
        avg_invited = total_invited / len(meetings)
        avg_accepted = total_accepted / len(meetings)
        avg_attendance_rate = (total_accepted / total_invited * 100) if total_invited > 0 else 0

    # Fetch all rooms and clubs for the dropdowns
    rooms = Room.query.all()
    clubs = Club.query.all()

    return render_template(
        'report.html',
        meetings=meetings,
        avg_duration=avg_duration,
        avg_invited=avg_invited,
        avg_accepted=avg_accepted,
        avg_attendance_rate=avg_attendance_rate,
        rooms=rooms,
        clubs=clubs
    )

@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
