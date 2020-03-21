from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from project import db

from sqlalchemy import UniqueConstraint


class User(db.Model, UserMixin):    # 存储用户信息
    id = db.Column(db.Integer, primary_key=True)    # 用户id
    name = db.Column(db.String(20))     # 用户昵称
    username = db.Column(db.String(20), unique=True)    # 用户名
    password_hash = db.Column(db.String(128))   # 用户密码(散列值)
    identity = db.Column(db.String(10))     # 用户身份

    def set_password(self, password):   # 将密码转换为散列值
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):  # 检验密码与散列值是否对应
        return check_password_hash(self.password_hash, password)


class Business_User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    business_name = db.Column(db.String(80))
    business_address = db.Column(db.String(20))
    business_type = db.Column(db.String(20))


class Plan(db.Model):   # 存储方案
    id = db.Column(db.Integer, primary_key=True)    # 方案id
    user_name = db.Column(db.String(40))    # 方案对应用户
    plan_name = db.Column(db.String(40))    # 方案名

    UniqueConstraint(user_name, plan_name)


class Standard(db.Model):   # 存储准则
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(40))
    standard_name = db.Column(db.String(40))
    UniqueConstraint(user_name, standard_name)


class Recommend_plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recommend_plan_name = db.Column(db.String(40))


class Recommend_standard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recommend_standard_name = db.Column(db.String(40))


class Temp_recommend_standard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(40))
    temp_recommend_standard_name = db.Column(db.String(40))
    UniqueConstraint(user_name, temp_recommend_standard_name)


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(40))
    address_name = db.Column(db.String(40))


class User_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    begin_address_name = db.Column(db.String(40))
    plan_list = db.Column(db.String(200))
    standard_list = db.Column(db.String(200))


class Plan_point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(40))
    plan_point = db.Column(db.Integer)


class Standard_point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    standard_name = db.Column(db.String(40))
    standard_point = db.Column(db.Integer)


class Plan_standard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    begin_address_name = db.Column(db.String(40))
    plan_name = db.Column(db.String(40))
    standard_name = db.Column(db.String(40))
    standard_point = db.Column(db.Integer)


class User_load_time(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(40))
    in_time = db.Column(db.String(80))
    out_time = db.Column(db.String(80))


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(40))
    identity = db.Column(db.String(10))
    content = db.Column(db.String(200))


class Feedback_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(40))
    identity = db.Column(db.String(10))
    content = db.Column(db.String(200))
