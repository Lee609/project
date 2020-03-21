import click

from project import app, db

from project.models import User, Plan, Standard


# 设置flask命令"flask initdb"创建数据库
# 设置flask命令"flask initdb --drop"重新创建数据库
@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')
