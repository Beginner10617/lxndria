from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, BooleanField, FieldList, FormField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed
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
    answer_type = SelectField('Answer Type', choices=[
        ('mcq', 'mcq')
        ,('input ', 'input')
        ], default='mcq', validators=[DataRequired()])
    options = FieldList(FormField(MCQOptionForm), min_entries=2)
    expected_answer = StringField('Expected Answer')
    submit = SubmitField('Post')

    def validate(self, extra_validators=None):
        if extra_validators is None:
            extra_validators = {}
        if not super().validate():
            print("Super validation failed")
            return False

        if self.answer_type.data == "mcq":
            correct_answers = [opt.is_correct.data for opt in self.options if opt.is_correct.data]
            if len(correct_answers) != 1:
                self.answer_type.errors.append("MCQ must have exactly one correct answer.")
                print("MCQ must have exactly one correct answer.")
                return False
            
        if self.answer_type.data == "input":
            if not self.expected_answer.data:
                self.expected_answer.errors.append("Please provide an expected answer.")
                print("Please provide an expected answer.")
                return False
            if not is_number(self.expected_answer.data):
                self.expected_answer.errors.append("Expected answer must be a valid number.")
                print("Expected answer must be a valid number.")
                return False

        return True
    

def is_number(s):
    try:
        float(s)  # Convert to float; works for int and float values
        return True
    except ValueError:
        return False