from .extensions import db, UserMixin, bcrypt
from datetime import datetime

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