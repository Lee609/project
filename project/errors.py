from flask import render_template
from flask_login import current_user

from project import app


@app.errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html', user=current_user), 400

# @app.errorhandler(400)
# def bad_request(e):
#     return render_template('index.html', user=current_user), 400


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html', user=current_user), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html', user=current_user), 500

