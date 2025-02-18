from .extensions import db, UserMixin, bcrypt
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property
import os, math
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
        ## out the username each time a user is created
        return '<User %r>' % self.username

class Profile(db.Model):
    __tablename__ = "profile"
    __table_args__ = {"extend_existing": True}

    username = db.Column(db.String(80), db.ForeignKey('user.username'), primary_key=True)  # Primary + Foreign Key
    user = db.relationship('User', backref=db.backref('profile', uselist=False, cascade="all, delete-orphan"))
    
    profile_pic = db.Column(db.String(255), default="/images/default-profile.jpg")  
    bio = db.Column(db.Text, default="This user has not set a bio yet.")
    upvotes = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Profile for {self.username}>"
    @property
    def problems_posted(self):
        return Problem.query.filter_by(author=self.username).count()
    @property
    def solutions(self):
        return Solutions.query.filter_by(username=self.username).count()
    @property
    def comments(self):
        return Comments.query.filter_by(username=self.username).count()
    @property
    def discussions(self):
        return Discussion.query.filter_by(author=self.username).count()
    @property
    def name(self):
        return self.user.name if self.user else None
    @property
    def is_moderator(self):
        return Moderators.query.filter_by(username=self.username).count() != 0
    
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
    views = db.Column(db.Integer, default=0)
    
    author = db.Column(db.String(80), db.ForeignKey('user.username'))
    user = db.relationship('User', backref=db.backref('problems', cascade="all, delete-orphan"))

    content = db.Column(db.Text, nullable=False)
    encrypted_answer = db.Column(db.Text, nullable=False)
    
    __table_args__ = (
        CheckConstraint("topic IN ('Algebra', 'Geometry', 'Number Theory', 'Calculus', 'Logic', 'Classical Mechanics', 'Electricity and Magnetism', 'Computer Science', 'Quantitative Finance', 'Chemistry', 'Probability')", name="valid_topic_check"),
    )

    def __repr__(self):
        return f"<Problem {self.title}>"
    
    @hybrid_property
    def flagged(self):
        return Flagged_Content.query.filter_by(parent_id='P' + str(self.id)).count() != 0

    @flagged.expression
    def flagged(cls):
        return db.session.query(Flagged_Content.id).filter(Flagged_Content.parent_id == db.func.concat('P', cls.id)).exists()
    
    @property
    def reducedContent(self):
        FullContent = self.content
        if len(FullContent) > 500:
            return FullContent[:500] + "..."
        return FullContent

    @hybrid_property
    def difficulty_value(self):
        if self.attempts == 0:
            return 0
        return 1-self.solved/self.attempts

    @property
    def difficulty(self):
        if self.attempts == 0:
            return "TBD"
        elif self.solved/self.attempts > os.getenv('EASY_THRESHOLD', 0.7):
            return "Easy"
        elif self.solved/self.attempts > os.getenv('MEDIUM_THRESHOLD', 0.3):
            return "Medium"
        else:
            return "Hard"

    @hybrid_property
    def popularity_value(self):
        views_weight = os.getenv('VIEWS_WEIGHT', 0.5)
        attempts_weight = os.getenv('ATTEMPTS_WEIGHT', 1.5)
        bookmarks_weight = os.getenv('BOOKMARKS_WEIGHT', 3)

        views = self.views
        attempts = self.attempts
        bookmarks = Bookmarks.query.filter_by(problem_id=self.id).count()

        return views_weight*views + attempts_weight*attempts + bookmarks_weight*bookmarks

    @property
    def popularity(self):
        popularity_value = self.popularity_value
        if popularity_value > os.getenv('POPULAR_THRESHOLD', 1000):
            return "Popular"
        elif popularity_value > os.getenv('TRENDING_THRESHOLD', 500):
            return "Trending"
        elif popularity_value > os.getenv('ACTIVE_THRESHOLD', 100):
            return "Active"
        else:
            return "Hot"
        
    @hybrid_property
    def needs_solution(self):
        solutions = Solutions.query.filter_by(problem_id=self.id).count()
        if solutions == 0:
            return True
        return False

    @needs_solution.expression
    def needs_solution(cls):
        return ~db.session.query(Solutions.id).filter(Solutions.problem_id == cls.id).exists()
           

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
    problem = db.relationship('Problem', backref=db.backref('solutions', cascade="all, delete-orphan"))
    username = db.Column(db.String(80), db.ForeignKey('user.username'))
    user = db.relationship('User', backref=db.backref('solutions', cascade="all, delete-orphan"))
    solution = db.Column(db.Text, nullable=False)
    upvotes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    @property
    def content(self):
        return self.solution

    @hybrid_property
    def flagged(self):
        return Flagged_Content.query.filter_by(parent_id='S' + str(self.id)).count() != 0

    @flagged.expression
    def flagged(cls):
        """Database-side expression"""
        return db.session.query(Flagged_Content.id).filter(Flagged_Content.parent_id == db.func.concat('S', cls.id)).exists()
    
    def __repr__(self):
        return f"<Solution for Problem {self.problem_id}>"

class Discussion(db.Model):
    __tablename__ = "discussion"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    author = db.Column(db.String(80), db.ForeignKey('user.username'))
    user = db.relationship('User', backref=db.backref('discussions', cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<Discussion {self.title}>"
    
    @hybrid_property
    def flagged(self):
        return Flagged_Content.query.filter_by(parent_id='D' + str(self.id)).count() != 0

    @flagged.expression
    def flagged(cls):
        return db.session.query(Flagged_Content.id).filter(Flagged_Content.parent_id == db.func.concat('D', cls.id)).exists()
    
    @property
    def reducedContent(self):
        FullContent = self.content
        if len(FullContent) > 500:
            return FullContent[:500] + "..."
        return FullContent
    
    @hybrid_property
    def popularity_value(self):
        views_weight = os.getenv('VIEWS_WEIGHT', 0.5)
        comments_weight = os.getenv('COMMENTS_WEIGHT', 2)
        bookmarks_weight = os.getenv('BOOKMARKS_WEIGHT', 3)
        time_constant = os.getenv('TIME_CONSTANT', 100)

        views = self.views
        comments = Comments.query.filter_by(parent_id='D'+str(self.id)).count()
        bookmarks = Bookmarks.query.filter_by(discussion_id=self.id).count()

        return views_weight*views + comments_weight*comments + bookmarks_weight*bookmarks 

    @property
    def popularity(self):
        popularity_value = self.popularity_value
        if popularity_value > os.getenv('POPULAR_THRESHOLD', 1000):
            return "Popular"
        elif popularity_value > os.getenv('TRENDING_THRESHOLD', 500):
            return "Trending"
        elif popularity_value > os.getenv('ACTIVE_THRESHOLD', 100):
            return "Active"
        else:
            return "Hot"

class Comments(db.Model):
    __tablename__ = "comments"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.VARCHAR(10), nullable=False)
    username = db.Column(db.String(80), db.ForeignKey('user.username'))
    user = db.relationship('User', backref=db.backref('comments', cascade="all, delete-orphan"))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Comment on Discussion {self.parent_id}>"
    
    @hybrid_property
    def flagged(self):
        return Flagged_Content.query.filter_by(parent_id='C' + str(self.id)).count() != 0

    @flagged.expression
    def flagged(cls):
        return db.session.query(Flagged_Content.id).filter(Flagged_Content.parent_id == db.func.concat('C', cls.id)).exists()
    
    @property
    def reducedContent(self):
        FullContent = self.content
        if len(FullContent) > 500:
            return FullContent[:500] + "..."
        return FullContent
    
class Upvotes(db.Model):
    __tablename__ = "upvotes"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username')) # Username of the user who upvoted
    user = db.relationship('User', backref=db.backref('upvotes', cascade="all, delete-orphan"))
    solution_id = db.Column(db.Integer, db.ForeignKey('solutions.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Upvote by {self.username}>"

class Bookmarks(db.Model):
    __tablename__ = "bookmarks"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username')) # Username of the user who bookmarked
    user = db.relationship('User', backref=db.backref('bookmarks', cascade="all, delete-orphan"))
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=True)
    problem = db.relationship('Problem', backref=db.backref('bookmarks', cascade="all, delete-orphan"))
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), nullable=True)
    discussion = db.relationship('Discussion', backref=db.backref('bookmarks', cascade="all, delete-orphan"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("problem_id IS NOT NULL OR discussion_id IS NOT NULL", name="valid_bookmark_check"),
    )

    def __repr__(self):
        return f"<Bookmark by {self.username}>"

class Notifications(db.Model):
    __tablename__ = "notifications"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.String(10), nullable=False)
    username = db.Column(db.String(80), db.ForeignKey('user.username')) # Username of the user who bookmarked
    user = db.relationship('User', backref=db.backref('notifications', cascade="all, delete-orphan"))
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    '''
    NOTIFICATIONS FOR:
    Sxyz: Solution id xyz to your Problem
    Cxyz: Comment id xyz on your Content
    CxyzT: Tagged in Comment id xyz 
    P/D/S/CxyzF: Problem/Discussion/Solution/Comment id xyz flagged
    '''

    @property
    def message(self):
        if self.parent_id[-1] == 'F':
            return flag_message(self.id[:-1])
        elif self.parent_id[0] == 'S':
            solution = Solutions.query.get(int(self.parent_id[1:]))
            if solution is None:
                return "404"
            problem = Problem.query.get(solution.problem_id)
            return f"{solution.user.name} posted solution to your Problem {problem.title}"
        elif self.parent_id[-1] == 'T':
            comment = Comments.query.get(int(self.parent_id[1:-1]))
            return f"{comment.user.name} tagged you in a Comment"
        elif self.parent_id[0] == 'C':
            comment = Comments.query.get(int(self.parent_id[1:]))
            content_type = comment.parent_id[0]
            if content_type == 'S':
                solution = Solutions.query.get(int(comment.parent_id[1:]))
                if solution is None:
                    return "404"
                problem = Problem.query.get(solution.problem_id)
                return f"{comment.user.name} commented on the Problem {problem.title}"
            elif content_type == 'D':
                discussion = Discussion.query.get(int(comment.parent_id[1:]))
                return f"{comment.user.name} commented on the Discussion {discussion.title}"
    @property
    def serialize(self):
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "message": self.message,
            "read": self.read,
            "created_at": self.created_at,
            "url": url_of_parent(self.parent_id)
        }
    @property
    def url(self):
        return url_of_parent(self.parent_id)
    def __repr__(self):
        return f"<Notification for {self.username}>"

class Flagged_Content(db.Model):
    __tablename__ = "flagged_content"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.String(10), nullable=False)
    flagged_by = db.Column(db.String(10), db.ForeignKey('moderators.username'))
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Flagged Content {self.parent_id}>"

class Report(db.Model):
    __tablename__ = "report"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.String(10), nullable=False)
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @hybrid_property 
    def post_by(self):
        if self.parent_id[0] == 'P':
            return Problem.query.get(int(self.parent_id[1:])).author
        elif self.parent_id[0] == 'D':
            return Discussion.query.get(int(self.parent_id[1:])).author
        elif self.parent_id[0] == 'S':
            return Solutions.query.get(int(self.parent_id[1:])).username
        elif self.parent_id[0] == 'C':
            return Comments.query.get(int(self.parent_id[1:])).username

    @post_by.expression
    def post_by(cls):
        problem_subq = db.select(Problem.author).where(cls.parent_id == db.func.concat('P', Problem.id)).scalar_subquery()
        discussion_subq = db.select(Discussion.author).where(cls.parent_id == db.func.concat('D', Discussion.id)).scalar_subquery()
        solutions_subq = db.select(Solutions.username).where(cls.parent_id == db.func.concat('S', Solutions.id)).scalar_subquery()
        comments_subq = db.select(Comments.username).where(cls.parent_id == db.func.concat('C', Comments.id)).scalar_subquery()

        return db.case(
            (cls.parent_id.startswith('P'), problem_subq),
            (cls.parent_id.startswith('D'), discussion_subq),
            (cls.parent_id.startswith('S'), solutions_subq),
            (cls.parent_id.startswith('C'), comments_subq),
            else_="Unknown"
        )
    
    @property
    def url(self):
        print(self.parent_id)
        return '/mod_view/'+self.parent_id+'?report='+str(self.id)

    def __repr__(self):
        return f"<Report on {self.parent_id}>"

class Appeals(db.Model):
    __tablename__ = "appeals"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flag_id = db.Column(db.Integer, db.ForeignKey('flagged_content.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    appeal_reason = db.Column(db.Text)

    def __repr__(self):
        return f"<Appeal on #{self.flag_id}>"

class Moderators(db.Model):
    __tablename__ = "moderators"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'))
    user = db.relationship('User', backref=db.backref('moderator', cascade="all, delete-orphan"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    requests_handled = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Moderator {self.username}>"

def url_of_parent(id):
    if id[-1] == 'F':
        # Notif of flagging of content
        return "#"
    elif id[0] == 'C':
        if id[-1] == 'T':
            comment = Comments.query.get(int(id[1:-1]))
            print(comment.id)
        else:
            comment = Comments.query.get(int(id[1:]))
        content_type = comment.parent_id[0]
        if content_type == 'S':
            solution = Solutions.query.get(int(comment.parent_id[1:]))
            problem = Problem.query.get(solution.problem_id)
            return f"/problem/{problem.id}#comment-{comment.id}"
        elif content_type == 'D':
            discussion = Discussion.query.get(int(comment.parent_id[1:]))
            return f"/discussion/{discussion.id}#comment-{comment.id}"
    elif id[0] == 'S':
        solution = Solutions.query.get(int(id[1:]))
        if solution is None:
            return "404"
        problem = Problem.query.get(solution.problem_id)
        return f"/problem/{problem.id}#solution-{solution.id}"
    elif id[0] == 'P':
        problem = Problem.query.get(int(id[1:]))
        return f"/problem/{problem.id}"
    elif id[0] == 'D':
        discussion = Discussion.query.get(int(id[1:]))
        return f"/discussion/{discussion.id}"
    

def flag_message(id):
    if id[0] == 'P':
        problem = Problem.query.get(int(id[1:]))
        return f"Problem {problem.title} was flagged"
    elif id[0] == 'D':
        discussion = Discussion.query.get(int(id[1:]))
        return f"Discussion {discussion.title} was flagged"
    elif id[0] == 'S':
        solution = Solutions.query.get(int(id[1:]))
        problem = Problem.query.get(solution.problem_id)
        return f"Solution to Problem {problem.title} was flagged"
    elif id[0] == 'C':
        comment = Comments.query.get(int(id[1:]))
        content_type = comment.parent_id[0]
        if content_type == 'S':
            solution = Solutions.query.get(int(comment.parent_id[1:]))
            problem = Problem.query.get(solution.problem_id)
            return f"Comment on Solution to Problem {problem.title} was flagged"
        elif content_type == 'D':
            discussion = Discussion.query.get(int(comment.parent_id[1:]))
            return f"Comment on Discussion {discussion.title} was flagged"

