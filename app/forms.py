from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, BooleanField, FieldList, FormField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed
from .extensions import is_number
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class EditAccountForm(FlaskForm):
    name = StringField('Name')
    profile_pic = FileField('Profile Picture', validators=[
        FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Images only!')
    ])
    bio = StringField('Bio')
    submit = SubmitField('Save Changes')

class MCQOptionForm(FlaskForm):
    is_correct = BooleanField("Correct")
    option_text = StringField("Option")

class PostProblemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    topic = SelectField('Topic', choices=[
        ('Algebra', 'Algebra')
        ,('Geometry', 'Geometry')
        ,('Number Theory', 'Number Theory')
        ,('Calculus', 'Calculus')
        ,('Logic', 'Logic')
        ,('Classical Mechanics', 'Classical Mechanics')
        ,('Electricity and Magnetism', 'Electricity and Magnetism')
        ,('Computer Science', 'Computer Science')
        ,('Quantitative Finance', 'Quantitative Finance')
        ,('Chemistry', 'Chemistry')
        ,('Probability', 'Probability')
        ], validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    expected_answer = StringField('Expected Answer')
    submit = SubmitField('Post')

    def validate(self, extra_validators=None):
        if extra_validators is None:
            extra_validators = {}
        if not super().validate():
           #("Super validation failed")
            return False
            
        if not self.expected_answer.data:
            self.expected_answer.errors.append("Please provide an expected answer.")
           #("Please provide an expected answer.")
            return False
        if not is_number(self.expected_answer.data):
            self.expected_answer.errors.append("Expected answer must be a valid number.")
           #("Expected answer must be a valid number.")
            return False

        return True
    
class SubmissionForm(FlaskForm):
    answer = StringField('Answer', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SolutionForm(FlaskForm):
    solution = TextAreaField('Solution', validators=[DataRequired()])
    submit = SubmitField('Submit')

class PostDiscussionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class ReportForm(FlaskForm):
    reason = TextAreaField('Reason', validators=[DataRequired(), Length(min=10, max=225)])
    submit = SubmitField('Submit')

class ModNotes(FlaskForm):
    notes = TextAreaField('Notes', validators=[DataRequired()])
    submit = SubmitField('Submit')

class UpdateEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')