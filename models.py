from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

meeting_organizers = db.Table('meeting_organizers',
    db.Column('meeting_id', db.Integer, db.ForeignKey('meetings.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('students.id'), primary_key=True)
)

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Club(db.Model):
    __tablename__ = 'clubs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Meeting(db.Model):
    __tablename__ = 'meetings'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    description = db.Column(db.String(200))
    duration = db.Column(db.Integer, nullable=False)
    attendees = db.Column(db.Integer, default=0)
    invited_students = db.Column(db.Integer, default=0)  # Total invited
    accepted_invitations = db.Column(db.Integer, default=0)  # Total accepted

    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'))

    room = db.relationship('Room', backref='meetings')
    club = db.relationship('Club', backref='meetings')

    # Define the many-to-many relationship with Student through meeting_organizers table
    organizers = db.relationship('Student', secondary=meeting_organizers, backref='meetings')
