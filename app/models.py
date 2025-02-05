from .extensions import db, UserMixin, bcrypt
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import CheckConstraint
import os
load_dotenv()
class User(db.Model, UserMixin): # create a User class to store user information
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}  # Allow modifications to the table

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        user_profile = Profile.query.filter_by(username=self.username).first()
        if user_profile == None:
            user_profile = Profile(username=self.username)
            db.session.add(user_profile)
            db.session.commit()
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        # print out the username each time a user is created
        return '<User %r>' % self.username

class Profile(db.Model):
    __tablename__ = "profile"
    __table_args__ = {"extend_existing": True}

    username = db.Column(db.String(80), db.ForeignKey('user.username'), primary_key=True)  # Primary + Foreign Key
    user = db.relationship('User', backref=db.backref('profile', uselist=False, cascade="all, delete-orphan"))
    
    profile_pic = db.Column(db.String(255), default="/images/default-profile.jpg")  
    bio = db.Column(db.Text, default="This user has not set a bio yet.")
    
    problems_posted = db.Column(db.Integer, default=0)
    solutions = db.Column(db.Integer, default=0)
    discussions = db.Column(db.Integer, default=0)
    upvotes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Profile for {self.username}>"
    
    @property
    def name(self):
        return self.user.name if self.user else None
    
class Problem(db.Model):
    __tablename__ = "problem"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(30), nullable=False)
    attempts = db.Column(db.Integer, default=0)
    solved = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    author = db.Column(db.String(80), db.ForeignKey('user.username'))
    user = db.relationship('User', backref=db.backref('problems', cascade="all, delete-orphan"))

    content = db.Column(db.Text, nullable=False)
    encrypted_answer = db.Column(db.Text, nullable=False)
    
    __table_args__ = (
        CheckConstraint("topic IN ('Algebra', 'Geometry', 'Number Theory', 'Calculus', 'Logic', 'Classical Mechanics', 'Electricity and Magnetism', 'Computer Science', 'Quantitative Finance', 'Chemistry', 'Probability')", name="valid_topic_check"),
    )

    def __repr__(self):
        return f"<Problem {self.title}>"
    '''@property
    def content(self):
        path = os.getenv('UPLOAD_FOLDER')+f"/{self.author}/Problems/{self.id}.txt"
        with open(path, 'r') as file:
            content = file.read()
        for line in content.split("\n"):
            if "<<Answer: " in line:
                return content.replace(line, "")
    '''
    @property
    def reducedContent(self):
        FullContent = self.content
        if len(FullContent) > 500:
            return FullContent[:500] + "..."
        return FullContent
            
    '''@property
    def encrypted_answer(self):
        path = os.getenv('UPLOAD_FOLDER')+f"/{self.author}/Problems/{self.id}.txt"
        with open(path, 'r') as file:
            content = file.read()
        for line in content.split("\n"):
            if "<<Answer: " in line:
                return line.replace("<<Answer: ", "").replace(">>", "")
    '''        
class UserStats(db.Model):
    __tablename__ = "user_stats"
    __table_args__ = {"extend_existing": True}

    username = db.Column(db.String(80), db.ForeignKey('user.username'), primary_key=True)
    user = db.relationship('User', backref=db.backref('stats', uselist=False, cascade="all, delete-orphan"))

    problems_posted = db.Column(db.Integer, default=0)
    solutions = db.Column(db.Integer, default=0)
    discussions = db.Column(db.Integer, default=0)
    upvotes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f"<Stats for {self.username}>"

class ProblemAttempts(db.Model):
    __tablename__ = "problem_attempts"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    
    username = db.Column(db.String(80), db.ForeignKey('user.username'))
    user = db.relationship('User', backref=db.backref('attempts', cascade="all, delete-orphan"))

    is_correct = db.Column(db.Boolean, default=False)

    attemptedAt = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Attempt on Problem {self.problem_id}>"

class Solutions(db.Model):
    __tablename__ = "solutions"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    username = db.Column(db.String(80), db.ForeignKey('user.username'))
    user = db.relationship('User', backref=db.backref('solutions', cascade="all, delete-orphan"))
    solution = db.Column(db.Text, nullable=False)
    upvotes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Solution for Problem {self.problem_id}>"