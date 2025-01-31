from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.forms import PostProblemForm, MCQOptionForm

contributions_bp = Blueprint('contributions', __name__)

@contributions_bp.route('/account/contribute/problem', methods=['GET', 'POST'])
@login_required
def contribute():
    form = PostProblemForm(request.form)
    # Ensure opt is not needed anymore; it's handled in PostProblemForm options.
    if form.validate_on_submit():
        title = form.title.data
        topic = form.topic.data
        content = form.content.data
        answer_type = form.answer_type.data
        expected_answer = form.expected_answer.data if answer_type == "input" else []
        options = []
        if answer_type == "mcq":
            # Collect options only for MCQ
            options = [
                {"text": option.option_text.data, "correct": option.is_correct.data}
                for option in form.options if option.option_text.data
            ]
            expected_answer = [opt["text"] for opt in options if opt["correct"]][0]
        print(expected_answer)
        return redirect(url_for('routes.main.index'))

    return render_template('contribute.html', form=form)
