import os
import sys

import click

from flask import render_template, request, url_for, redirect, flash, Flask
from flask_login import login_user, login_required, logout_user, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

from ahp import get_w
import numpy as np


WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), os.getenv('DATABASE_FILE', 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'login'


data_plan = []
data_standard = []


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(40))
    plan_name = db.Column(db.String(40))


class Standard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(40))
    standard_name = db.Column(db.String(40))


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


@app.errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html', user=current_user), 400


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html', user=current_user), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html', user=current_user), 500


@app.route('/index', endpoint='index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))

        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('index'))

        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template('index.html', movies=movies, user=current_user)


@app.route('/movie/edit/<int:movie_id>', endpoint='edit', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie, user=current_user)


@app.route('/movie/delete/<int:movie_id>', endpoint='delete', methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))


@app.route('/settings',  endpoint='settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        user = User.query.filter_by(username=current_user.username).first()
        user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html', user=current_user)


@app.route('/login', endpoint='login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()

        if user.validate_password(password):
            login_user(user)
            flash('Welcome {}.'.format(current_user.name))
            return redirect(url_for('plan'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))
    return render_template('login.html', user=current_user)


@app.route('/register', endpoint='register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']

        if not name or not username or not password:
            flash('Invalid input!')
            return redirect(url_for('register'))

        user = User(name=name, username=username, password_hash=password)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', user=current_user)


@app.route('/logout', endpoint='logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('login'))


@app.route('/', methods=['POST', 'GET'])
@login_required
def plan():
    plans = Plan.query.filter_by(user_name=current_user.username).all()
    if request.method == 'POST':
        user_name = current_user.username
        plan_name = request.form['plan']
        if not plan_name:
            flash('Invalid input.')
            return redirect(url_for('plan'))
        p = Plan(user_name=user_name, plan_name=plan_name)
        db.session.add(p)
        db.session.commit()
        flash('Plan added successfully!')
        return redirect(url_for('plan'))

    return render_template('plan.html', user=current_user, plans=plans)


@app.route('/plan/delete/<int:plan_id>', endpoint='delete_plan', methods=['POST'])
@login_required
def delete_plan(plan_id):
    p = Plan.query.get_or_404(plan_id)
    db.session.delete(p)
    db.session.commit()
    flash('One plan deleted successfully.')
    return redirect(url_for('plan'))


@app.route('/plan/clear_all', endpoint='clear_all_plan', methods=['POST'])
@login_required
def clear_all_plan():
    plans = Plan.query.filter_by(user_name=current_user.username).all()
    for p in plans:
        db.session.delete(p)
    db.session.commit()
    flash('Clear successfully.')
    return redirect(url_for('plan'))


@app.route('/plan/to_standard', endpoint='plan_to_standard', methods=['POST', 'GET'])
@login_required
def plan_to_standard():
    return redirect(url_for('standard'))


@app.route('/standard', endpoint='standard', methods=['POST', 'GET'])
@login_required
def standard():
    standards = Standard.query.filter_by(user_name=current_user.username).all()
    if request.method == "POST":
        user_name = current_user.username
        standard_name = request.form['standard']
        if not standard_name:
            flash('Invalid input.')
            return redirect(url_for('plan'))
        s = Standard(user_name=user_name, standard_name=standard_name)
        db.session.add(s)
        db.session.commit()
        flash('Standard added successfully!')
        return redirect(url_for('standard'))
    return render_template('standard.html', user=current_user, standards=standards)


@app.route('/standard/delete/<int:standard_id>', endpoint='delete_standard', methods=['POST'])
@login_required
def delete_standard(standard_id):
    s = Standard.query.get_or_404(standard_id)
    db.session.delete(s)
    db.session.commit()
    flash('One standard deleted successfully.')
    return redirect(url_for('standard'))


@app.route('/standard/clear_all', endpoint='clear_all_standard', methods=['POST'])
@login_required
def clear_all_standard():
    standards = Standard.query.filter_by(user_name=current_user.username).all()
    for s in standards:
        db.session.delete(s)
    db.session.commit()
    flash('Clear successfully.')
    return redirect(url_for('standard'))


@app.route('/standard/to_matrix', endpoint='standard_to_matrix', methods=['POST', 'GET'])
@login_required
def standard_to_matrix():
    return redirect(url_for('matrix'))


@app.route('/matrix', endpoint='matrix', methods=['POST', 'GET'])
@login_required
def matrix():
    standards = Standard.query.filter_by(user_name=current_user.username).all()
    plans = Plan.query.filter_by(user_name=current_user.username).all()
    standard_list = []
    plan_list = []
    for s in standards:
        standard_list.append(s.standard_name)
    for p in plans:
        plan_list.append(p.plan_name)

    data_plan.clear()
    data_standard.clear()

    for i in range(len(standard_list)):
        data_standard.append([])

    for i in range(len(standard_list)):
        data_plan.append([])
    for i in range(len(standard_list)):
        for j in range(len(plan_list)):
            data_plan[i].append([])

    if request.method == "POST":
        # data_standard添加数据
        for i in range(len(standard_list)):
            for j in range(len(standard_list)):
                if j == i:
                    data_standard[i].append(1.0)
                elif j < i:
                    data_standard[i].append(eval(request.form[standard_list[i]+standard_list[j]]))
                else:
                    data_standard[i].append(1 / eval(request.form[standard_list[j]+standard_list[i]]))
        # data_plan添加数据
        for s in range(len(standard_list)):
            for i in range(len(plan_list)):
                for j in range(len(plan_list)):
                    if j == i:
                        data_plan[s][i].append(1.0)
                    elif j < i:
                        data_plan[s][i].append(eval(request.form[plan_list[i]+plan_list[j]+standard_list[s]]))
                    else:
                        data_plan[s][i].append(1 / eval(request.form[plan_list[j] + plan_list[i] + standard_list[s]]))
        return redirect(url_for('result'))

    return render_template('matrix.html', user=current_user, standard_list=standard_list, plan_list=plan_list)


@app.route('/result', endpoint='result')
@login_required
def result():
    plans = Plan.query.filter_by(user_name=current_user.username).all()
    matrix_s = np.array(data_standard)
    result_list = list(get_w(matrix_s))
    return render_template('result.html', user=current_user, plans=plans, result_list=result_list)


if __name__ == '__main__':
    app.run()
