from flask import render_template, request, url_for, redirect, flash, Flask
from flask_login import login_user, login_required, logout_user, current_user, UserMixin

from project.ahp import get_result
from project.models import User, Plan, Standard, Recommend_standard, Recommend_plan, Address, User_load_time
from project.models import User_history, Business_User, Plan_point, Standard_point, Plan_standard, Feedback, Feedback_history
from project import app, db

from xpinyin import Pinyin

from project.get_distance import getDistance, baiduMap_location, gaodeMap_location, getDistance_gaode, gaode_coordinate
from project.get_location import get_location_baidu, get_location_without_ip, location_yes

import logging
from datetime import datetime
import copy

from jinja2 import Markup
from pyecharts import options as opts
from pyecharts.charts import Bar, Grid, Line, Scatter, Pie, Geo
from pyecharts.faker import Faker
from pyecharts.globals import ChartType, SymbolType, ThemeType
from pyecharts.globals import CurrentConfig


CurrentConfig.ONLINE_HOST = 'http://127.0.0.8000/assets'


data_plan = []      # 保存各个方案的成对比较矩阵
data_standard = []  # 保存准则的成对比较矩阵

address_range = ['国家', '省', '城市', '区县', '乡镇', '村庄', '市', '开发区']


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == "POST":
#         return redirect(url_for('get_location'))    # 重定向到plan()
#     return render_template('index.html', user=current_user)


@app.route('/get_location/person_user', methods=['GET', 'POST'])
@login_required
def get_location():
    return render_template('get_location.html', user=current_user)


@app.route('/get_location_yes', methods=['GET', 'POST'])
@login_required
def get_location_yes():
    ip = request.remote_addr
    logging.debug(ip)
    try:
        address_name = get_location_baidu(ip)
        address_name_bak = location_yes(ip)
    except:
        address_name = get_location_without_ip()
        address_name_bak = location_yes(ip)

    user_name = current_user.username
    try:
        add = Address(user_name=user_name, address_name=address_name)
        db.session.add(add)
        db.session.commit()
        flash('成功获取地理位置')
        return redirect(url_for('plan'))
    except:
        add = Address(user_name=user_name, address_name=address_name_bak)
        db.session.add(add)
        db.session.commit()
        flash('成功获取地理位置')
        return redirect(url_for('plan'))


@app.route('/get_location_no', methods=['GET', 'POST'])
@login_required
def get_location_no():
    return redirect(url_for('location'))


@app.route('/location', methods=['GET', 'POST'])
@login_required
def location():
    # address_record = Address.query.filter_by(user_name=current_user.username).order_by(Address.id.desc()).first()
    # address_name = address_record.address_name
    if request.method == 'POST':
        user_name = current_user.username
        address_name = request.form['address']
        try:
            is_address = baiduMap_location(address_name)
            if is_address['status'] == 1 or (is_address['result']['level'] not in address_range):
                flash('请输入正确的国内地址')
                return redirect(url_for('location'))
        except:
            is_address = gaodeMap_location(address_name)
            if is_address['status'] != 1 or (is_address['geocodes'][0]['level'] not in address_range):
                flash('请输入正确的国内地址')
                return redirect(url_for('location'))
        if not address_name:
            flash('无效的输入')
            return redirect(url_for('location'))
        add = Address(user_name=user_name, address_name=address_name)
        db.session.add(add)
        db.session.commit()
        flash('成功设置地理位置')
        return redirect(url_for('plan'))

    return render_template('location.html', user=current_user)


@app.route('/settings', methods=['GET', 'POST'])
@login_required     # @login_required表示需要登录才可见
def settings():
    address_record = Address.query.filter_by(user_name=current_user.username).order_by(Address.id.desc()).first()
    address_name = address_record.address_name
    if request.method == 'POST':
        now_address_name = request.form['address']
        user_name = current_user.username
        is_address = baiduMap_location(now_address_name)
        try:
            if is_address['status'] == 1 or (is_address['result']['level'] not in address_range):
                flash('请输入正确的国内地址')
                return redirect(url_for('settings'))
        except:
            is_address = gaodeMap_location(address_name)
            if is_address['status'] != 1 or (is_address['geocodes'][0]['level'] not in address_range):
                flash('请输入正确的国内地址')
                return redirect(url_for('location'))
        if not now_address_name:
            flash('无效的输入')
            return redirect(url_for('settings'))

        add = Address(user_name=user_name, address_name=now_address_name)
        db.session.add(add)
        db.session.commit()
        flash('位置修改成功.')
        return redirect(url_for('plan'))
    return render_template('settings.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        identity = request.form['identity']

        if identity == 'person':
            if not username or not password:
                flash('无效的输入')
                return redirect(url_for('login'))
            try:
                user = User.query.filter_by(username=username, identity='person').first()
                if user.validate_password(password):
                    login_user(user)

                    time = datetime.now()
                    in_time = datetime.strftime(time, '%Y-%m-%d %H:%M:%S')
                    user_name = current_user.username
                    load_time = User_load_time(user_name=user_name, in_time=in_time, out_time='NULL')
                    db.session.add(load_time)
                    db.session.commit()

                    flash('你好,{}.'.format(current_user.name))
                    return redirect(url_for('get_location'))

                flash('无效的用户名或密码')
                return redirect(url_for('login'))
            except:
                flash('无效的用户名或密码')
        elif identity == 'business':
            if not username or not password:
                flash('无效的输入')
                return redirect(url_for('login'))
            try:
                user = User.query.filter_by(username=username, identity='business').first()
                if user.validate_password(password):
                    login_user(user)
                    time = datetime.now()
                    in_time = datetime.strftime(time, '%Y-%m-%d %H:%M:%S')
                    user_name = current_user.username
                    load_time = User_load_time(user_name=user_name, in_time=in_time, out_time='NULL')
                    db.session.add(load_time)
                    db.session.commit()

                    flash('你好,{}.'.format(current_user.name))
                    return redirect(url_for('business_index'))

                flash('无效的用户名或密码')
                return redirect(url_for('login'))
            except:
                flash('无效的用户名或密码')
        else:
            if not username or not password:
                flash('无效的输入')
                return redirect(url_for('login'))
            try:
                user = User.query.filter_by(username=username, identity='admin').first()
                if user.validate_password(password):
                    login_user(user)
                    flash('你好,{}.'.format(current_user.name))
                    return redirect(url_for('admin_index'))

                flash('无效的用户名或密码')
                return redirect(url_for('login'))
            except:
                flash('无效的用户名或密码')

    return render_template('login.html', user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        identity = request.form['identity']
        if identity == 'person':
            return redirect(url_for('person_register'))
        else:
            return redirect(url_for('business_register'))
    return render_template('register.html', user=current_user)


@app.route('/register/person_register', methods=['POST', 'GET'])
def person_register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        identity = 'person'

        if not name or not username or not password:
            flash('无效的输入')
            return redirect(url_for('person_register'))
        if password != password_confirm:
            flash('前后密码不一致！')
            return redirect(url_for('person_register'))
        try:
            user = User(name=name, username=username, password_hash=password, identity=identity)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            flash('该用户名已存在')
            return redirect(url_for('person_register'))
    return render_template('person_register.html', user=current_user)


@app.route('/register/business_register', methods=['POST', 'GET'])
def business_register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['business_name']
        business_name = request.form['business_name']
        business_address = request.form['business_address']
        business_type = request.form['business_type']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        identity = 'business'

        if not name or not username or not password:
            flash('无效的输入')
            return redirect(url_for('business_register'))
        if password != password_confirm:
            flash('前后密码不一致！')
            return redirect(url_for('business_register'))

        try:
            business_user = Business_User(username=username, business_name=business_name,
                                          business_address=business_address, business_type=business_type)
            user = User(name=name, username=username, password_hash=password, identity=identity)
            user.set_password(password)
            db.session.add(user)
            db.session.add(business_user)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            flash('该用户名已存在')
            return redirect(url_for('business_register'))
    return render_template('business_register.html', user=current_user)


@app.route('/change_name', methods=['GET', 'POST'])
@login_required
def change_name():
    if request.method == 'POST':
        user = User.query.filter_by(username=current_user.username).first()
        now_name = request.form['name']
        user.name = now_name
        db.session.commit()
        flash('昵称修改成功')
        return redirect(request.referrer)


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        user = User.query.filter_by(username=current_user.username).first()
        before_password = request.form['before_password']
        now_password = request.form['now_password']
        now_password_confirm = request.form['now_password_confirm']

        if user.validate_password(before_password):
            if now_password == now_password_confirm:
                user.password_hash = now_password
                user.set_password(now_password)
                db.session.commit()
                flash('密码修改成功')
                return redirect(request.referrer)
            else:
                flash('前后密码不一致')
                return redirect(request.referrer)
        else:
            flash('原密码输入错误')
            return redirect(request.referrer)


@app.route('/logout')
@login_required
def logout():
    if current_user.identity != 'admin':
        time = datetime.now()
        # in_time_record = User_load_time.query.filter_by(user_name=current_user.username).order_by(User_load_time.id.desc()).first()
        in_time_record = User_load_time.query.filter_by(
            user_name=current_user.username, out_time='NULL').order_by(User_load_time.id.desc()).first()
        in_time = in_time_record.in_time
        out_time = datetime.strftime(time, '%Y-%m-%d %H:%M:%S')
        user_name = current_user.username
        load_time = User_load_time(user_name=user_name, in_time=in_time, out_time=out_time)
        db.session.add(load_time)
        db.session.delete(in_time_record)
        db.session.commit()

    logout_user()
    flash('期待与您的下一次相遇,再见')
    return redirect(url_for('login'))


@app.route('/plan', methods=['POST', 'GET'])
@login_required
def plan():
    address_record = Address.query.filter_by(user_name=current_user.username).order_by(Address.id.desc()).first()
    address_name = address_record.address_name
    plans = Plan.query.filter_by(user_name=current_user.username).all()
    recommend_plans = Recommend_plan.query.all()

    if request.method == 'POST':
        user_name = current_user.username
        plan_name = request.form['plan']


        try:
            is_address = baiduMap_location(plan_name)
            if is_address['status'] == 1 or (is_address['result']['level'] not in address_range):
                flash('请输入正确的国内地址')
                return redirect(url_for('plan'))
        except:
            is_address = gaodeMap_location(plan_name)
            if is_address['status'] != 1 or (is_address['geocodes'][0]['level'] not in address_range):
                flash('请输入正确的国内地址')
                return redirect(url_for('plan'))
        if not plan_name:
            flash('无效的输入')
            return redirect(url_for('plan'))
        try:
            p = Plan(user_name=user_name, plan_name=plan_name)
            db.session.add(p)
            db.session.commit()
            flash('备选方案添加成功')
            return redirect(url_for('plan'))
        except:
            flash('已存在该备选方案')
            return redirect(url_for('plan'))

    return render_template('plan.html', user=current_user, plans=plans,
                           address=address_name, recommend_plans=recommend_plans)


@app.route('/plan/get_recommend_plan/<int:recommend_plan_id>', methods=['GET', 'POST'])
@login_required
def get_recommend_plan(recommend_plan_id):
    select_plan = db.session.query(Recommend_plan).get(recommend_plan_id)
    # select_standard = Recommend_standard.query.get_or_404(recommend_standard_id)
    try:
        add_plan = Plan(user_name=current_user.username, plan_name=select_plan.recommend_plan_name)
        db.session.add(add_plan)
        db.session.commit()
        return redirect(url_for('plan'))
    except:
        flash('已存在该备选方案')
        return redirect(url_for('plan'))


@app.route('/plan/delete/<int:plan_id>', methods=['POST'])
@login_required
def delete_plan(plan_id):
    del_p = Plan.query.get_or_404(plan_id)
    db.session.delete(del_p)
    db.session.commit()
    flash('一个备选方案删除成功')
    return redirect(url_for('plan'))


@app.route('/plan/clear_all', methods=['POST'])
@login_required
def clear_all_plan():
    plans = Plan.query.filter_by(user_name=current_user.username).all()
    try:
        for del_p in plans:
            db.session.delete(del_p)
    except:
        pass
    db.session.commit()
    flash('成功删除所有备选方案')
    return redirect(url_for('plan'))


@app.route('/plan/to_standard', methods=['POST', 'GET'])
@login_required
def plan_to_standard():
    plans = Plan.query.filter_by(user_name=current_user.username).all()
    if len(plans) > 2:
        return redirect(url_for('standard'))
    else:
        flash("备选方案应至少3个")
        return redirect(url_for('plan'))


@app.route('/standard', methods=['POST', 'GET'])
@login_required
def standard():
    address_record = Address.query.filter_by(user_name=current_user.username).order_by(Address.id.desc()).first()
    address_name = address_record.address_name
    standards = Standard.query.filter_by(user_name=current_user.username).all()
    recommend_standards = Recommend_standard.query.all()

    if request.method == "POST":
        user_name = current_user.username
        standard_name = request.form['standard']

        if not standard_name:
            flash('无效的输入')
            return redirect(url_for('standard'))
        try:
            s = Standard(user_name=user_name, standard_name=standard_name)
            db.session.add(s)
            db.session.commit()
            flash('评价准则添加成功')
            return redirect(url_for('standard'))
        except:
            flash('已存在该评价准则')
            return redirect(url_for('standard'))
    return render_template('standard.html', user=current_user, standards=standards,
                           address=address_name, recommend_standards=recommend_standards)


@app.route('/standard/get_recommend_standard/<int:recommend_standard_id>', methods=['GET', 'POST'])
@login_required
def get_recommend_standard(recommend_standard_id):
    select_standard = db.session.query(Recommend_standard).get(recommend_standard_id)
    # select_standard = Recommend_standard.query.get_or_404(recommend_standard_id)
    try:
        add_standard = Standard(user_name=current_user.username, standard_name=select_standard.recommend_standard_name)
        db.session.add(add_standard)
        db.session.commit()
        return redirect(url_for('standard'))
    except:
        flash('已存在该评价准则')
        return redirect(url_for('standard'))


@app.route('/standard/delete/<int:standard_id>', methods=['POST'])
@login_required
def delete_standard(standard_id):
    s = db.session.query(Standard).get(standard_id)
    # s = Standard.query.get_or_404(standard_id)

    db.session.delete(s)
    db.session.commit()
    flash('一个评价准则删除成功')
    return redirect(url_for('standard'))


@app.route('/standard/clear_all', methods=['POST'])
@login_required
def clear_all_standard():
    standards = Standard.query.filter_by(user_name=current_user.username).all()
    for s in standards:
        db.session.delete(s)
    db.session.commit()
    flash('成功删除所有评价准则')
    return redirect(url_for('standard'))


@app.route('/standard/to_matrix', methods=['POST', 'GET'])
@login_required
def standard_to_matrix():
    standards = Standard.query.filter_by(user_name=current_user.username).all()
    if len(standards) > 2:
        return redirect(url_for('matrix'))
    else:
        flash("评价准则应至少3个")
        return redirect(url_for('standard'))


@app.route('/matrix', methods=['POST', 'GET'])
@login_required
def matrix():
    global data_plan
    global data_standard
    standards = Standard.query.filter_by(user_name=current_user.username).all()
    plans = Plan.query.filter_by(user_name=current_user.username).all()
    recommend_standards = Recommend_standard.query.all()
    recommend_standards_list = []
    standard_list = []
    plan_list = []
    for s in standards:
        standard_list.append(s.standard_name)
    for p in plans:
        plan_list.append(p.plan_name)
    for rs in recommend_standards:
        recommend_standards_list.append(rs.recommend_standard_name)

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
        # return redirect(url_for('charts'))

    address_record = Address.query.filter_by(user_name=current_user.username).order_by(Address.id.desc()).first()
    address_name = address_record.address_name
    distance_list = []
    for p in plan_list:
        try:
            distance_list.append(getDistance(address_name, p))
        except:
            distance_list.append(getDistance_gaode(address_name, p))

    pinyin_plan_list = []
    pin = Pinyin()
    for p in plan_list:
        pinyin_plan_list.append(pin.get_pinyin(p, ''))

    return render_template('matrix.html', user=current_user,
                           standard_list=standard_list, plan_list=plan_list,
                           distance_list=distance_list, pinyin_plan_list=pinyin_plan_list,
                           address=address_name)


# @app.route('/attraction', methods=['POST', 'GET'])
# @login_required
# def attraction():
#     plans = Plan.query.filter_by(user_name=current_user.username).all()
#     plan_list = []
#     attraction_list = []
#     for p in plans:
#         plan_list.append(p.plan_name)
#     try:
#         for add in plan_list:
#             attraction_list.append(get_attraction(add))
#         return render_template('attraction.html', user=current_user,
#                                plan_list=plan_list, attraction_list=attraction_list)
#     except:
#         return redirect(url_for('matrix'))


@app.route('/recursion_error', methods=['POST', 'GET'])
@login_required
def recursion_error():
    if request.method == "POST":
        return redirect(url_for('matrix'))
    return render_template('recursion_error.html', user=current_user)


@app.route('/result')
@login_required
def result():
    global data_standard
    global data_plan

    p_list = ''
    s_list = ''

    address_record = Address.query.filter_by(user_name=current_user.username).order_by(Address.id.desc()).first()
    address_name = address_record.address_name
    standards = Standard.query.filter_by(user_name=current_user.username).all()
    plans = Plan.query.filter_by(user_name=current_user.username).all()

    for i in range(len(plans)):
        if i != (len(plans) - 1):
            p_list = p_list + "{},".format(plans[i].plan_name)
        else:
            p_list = p_list + "{}".format(plans[i].plan_name)
    for i in range(len(standards)):
        if i != (len(standards) - 1):
            s_list = s_list + "{},".format(standards[i].standard_name)
        else:
            s_list = s_list + "{}".format(standards[i].standard_name)

    try:
        result_list_tuple = get_result(data_standard, data_plan)
        result_list = result_list_tuple[0]
        standard_point_list = result_list_tuple[2]

        user_history = User_history(begin_address_name=address_name, plan_list=p_list, standard_list=s_list)
        db.session.add(user_history)
        db.session.commit()

        for i in range(len(plans)):
            plan_name = plans[i].plan_name
            plan_point = result_list[i]
            plan_p = Plan_point(plan_name=plan_name, plan_point=plan_point)
            db.session.add(plan_p)
            db.session.commit()

        for i in range(len(standards)):
            standard_name = standards[i].standard_name
            standard_point = standard_point_list[i]
            standard_p = Standard_point(standard_name=standard_name, standard_point=standard_point)
            db.session.add(standard_p)
            db.session.commit()

        for i in range(len(plans)):
            for j in range(len(standards)):
                begin_address_name = address_name
                plan_name = plans[i].plan_name
                standard_name = standards[j].standard_name
                standard_point = standard_point_list[j]
                p_s = Plan_standard(begin_address_name=begin_address_name, plan_name=plan_name, standard_name=standard_name, standard_point=standard_point)
                db.session.add(p_s)
                db.session.commit()
    except:
        return redirect(url_for('recursion_error'))     # python默认递归深度为1000,超过则会报错
    return render_template('result.html', user=current_user, plans=plans, result_list=result_list)


def global_plan_charts() -> Grid:
    global data_standard
    global data_plan

    p_list = ''
    s_list = ''

    address_record = Address.query.filter_by(user_name=current_user.username).order_by(Address.id.desc()).first()
    address_name = address_record.address_name
    standards = Standard.query.filter_by(user_name=current_user.username).all()
    plans = Plan.query.filter_by(user_name=current_user.username).all()

    plan_list = []
    standard_list = []
    for p in plans:
        plan_list.append(p.plan_name)
    for s in standards:
        standard_list.append(s.standard_name)

    for i in range(len(plans)):
        if i != (len(plans) - 1):
            p_list = p_list + "{},".format(plans[i].plan_name)
        else:
            p_list = p_list + "{}".format(plans[i].plan_name)
    for i in range(len(standards)):
        if i != (len(standards) - 1):
            s_list = s_list + "{},".format(standards[i].standard_name)
        else:
            s_list = s_list + "{}".format(standards[i].standard_name)

    try:
        result_list_tuple = get_result(data_standard, data_plan)
        result_list = result_list_tuple[0]
        w_each_plan = result_list_tuple[1]
        w_standard = result_list_tuple[2]

        user_history = User_history(begin_address_name=address_name, plan_list=p_list, standard_list=s_list)
        db.session.add(user_history)
        db.session.commit()
    except:
        return redirect(url_for('recursion_error'))

    bar = Bar()
    bar.add_xaxis(standard_list)
    for i in range(len(plan_list)):
        bar.add_yaxis(plan_list[i], w_each_plan[i])
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="各评价准则上的推荐指数",
                                  subtitle="by {}".format(current_user.username)),
        legend_opts=opts.LegendOpts(is_show=False)
    )

    line = Line()
    line.add_xaxis(standard_list)
    line.add_yaxis('评价准则权重', w_standard)

    # bar.overlap(line)

    pie_data_list = []
    for i in range(len(plan_list)):
        pie_data_list.append((plan_list[i], result_list[i]))

    pie = Pie()
    pie.add(series_name="",
            data_pair=pie_data_list,
            radius=["10%", "40%"],
            rosetype="area",)
    pie.set_global_opts(title_opts=opts.TitleOpts(title="各备选方案推荐指数",
                                                  subtitle="by {}".format(current_user.username),
                                                  pos_bottom="20%", pos_left="40%"))
    pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))

    grid = Grid()
    grid.add(bar.overlap(line), grid_opts=opts.GridOpts(pos_right="65%"))
    grid.add(pie, grid_opts=opts.GridOpts(pos_left="75%"))

    return grid


@app.route("/charts")
@login_required
def charts():
    plans = Plan.query.filter_by(user_name=current_user.username).all()
    result_list_tuple = get_result(data_standard, data_plan)
    result_list = result_list_tuple[0]
    return render_template("charts.html", user=current_user, plans=plans, result_list=result_list)


@app.route("/barChart")
def get_bar_chart():
    c = global_plan_charts()
    return c.dump_options_with_quotes()


@app.route('/business/history', methods=['POST', 'GET'])
@login_required
def history_list():
    business_user = Business_User.query.filter_by(username=current_user.username).first()
    user_history = User_history.query.all()
    user_plan_list = []
    for uh in user_history:
        user_plan_list.append(uh.plan_list.split(','))

    user_standard_list = []
    for uh in user_history:
        user_standard_list.append(uh.standard_list.split(','))

    return render_template('history_list.html', user=current_user, business_user=business_user,
                           user_history=user_history, user_plan_list=user_plan_list,
                           user_standard_list=user_standard_list)


def local_data_charts() -> Grid:
    time = datetime.now()
    time_str = datetime.strftime(time, '%Y-%m-%d %H:%M:%S')

    user_history = User_history.query.all()
    user_plan_list = []
    for uh in user_history:
        user_plan_list.append(uh.plan_list.split(','))

    end_address_dict = dict()
    for user_plan in user_plan_list:
        for end_address in user_plan:
            if end_address_dict.get(end_address):
                end_address_dict[end_address] += 1
            else:
                end_address_dict[end_address] = 1

    end_address_count = []
    address_list = list(end_address_dict.keys())
    count_list = list(end_address_dict.values())
    sum_count = sum(count_list)
    per_count_list = []
    for c in count_list:
        per_count_list.append(round(c / sum_count, 3))
    for i in range(len(end_address_dict)):
        end_address_count.append((address_list[i], per_count_list[i]))
    if len(address_list) <= 8:
        pie = Pie()
        pie.add(series_name="",
                data_pair=end_address_count,
                radius=["5%", "40%"],
                rosetype="area",
                )
        pie.set_global_opts(title_opts=opts.TitleOpts(title="各备选方案出现次数占比",
                                                      subtitle="更新时间:{}(每30秒自动更新一次)".format(time_str),
                                                      pos_left="40%", pos_bottom="20%"))
        pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    else:
        per_count_list_copy = copy.deepcopy(per_count_list)
        per_count_list_max8 = []
        per_count_list_max8_index = []
        for _ in range(8):
            number = max(per_count_list_copy)
            index = per_count_list_copy.index(number)
            per_count_list_copy[index] = 0
            per_count_list_max8.append(number)
            per_count_list_max8_index.append(index)
        max8_address_list = []
        for i in per_count_list_max8_index:
            max8_address_list.append(address_list[i])
        max8_address_list.append('其他')
        others_per_count = round(1 - sum(per_count_list_max8), 3)
        per_count_list_max8.append(others_per_count)
        end_address_count_max8 = []
        for i in range(len(max8_address_list)):
            end_address_count_max8.append((max8_address_list[i], per_count_list_max8[i]))

        pie = Pie()
        pie.add(series_name="",
                data_pair=end_address_count_max8,
                radius=["5%", "40%"],
                rosetype="area",
                )
        pie.set_global_opts(title_opts=opts.TitleOpts(title="各备选方案出现次数占比",
                                                      subtitle="更新时间:{}(每30秒自动更新一次)".format(time_str),
                                                      pos_left="40%", pos_bottom="20%"))
        pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))

    plan_points = Plan_point.query.all()
    plan_point_dict = dict()
    plan_point_list = []
    for plan_point in plan_points:
        if plan_point_dict.get(plan_point.plan_name):
            plan_point_dict[plan_point.plan_name] += plan_point.plan_point
        else:
            plan_point_dict[plan_point.plan_name] = plan_point.plan_point
    plan_sum_point_list = list(plan_point_dict.values())
    for i in range(len(plan_sum_point_list)):
        plan_point_per = plan_sum_point_list[i] / count_list[i]
        plan_point_list.append(round(plan_point_per, 2))
    if len(plan_point_list) <= 8:
        bar = Bar()
        bar.add_xaxis(address_list)
        bar.add_yaxis("", plan_point_list)
        bar.set_global_opts(title_opts=opts.TitleOpts(title="各备选方案平均推荐指数(TOP8)",
                                                      subtitle="更新时间:{}(每30秒自动更新一次)".format(time_str)))
    else:
        plan_point_list_copy = copy.deepcopy(plan_point_list)
        plan_point_list_max8 = []
        plan_point_list_max8_index = []
        for _ in range(8):
            number = max(plan_point_list_copy)
            index = plan_point_list_copy.index(number)
            plan_point_list_copy[index] = 0
            plan_point_list_max8.append(number)
            plan_point_list_max8_index.append(index)
        max8_address_list = []
        for i in plan_point_list_max8_index:
            max8_address_list.append(address_list[i])
        bar = Bar()
        bar.add_xaxis(max8_address_list)
        bar.add_yaxis("", plan_point_list_max8)
        bar.set_global_opts(title_opts=opts.TitleOpts(title="各备选方案平均推荐指数(TOP8)",
                                                      subtitle="更新时间:{}(每30秒自动更新一次)".format(time_str)))

    grid = Grid()
    grid.add(bar, grid_opts=opts.GridOpts(pos_right="65%"))
    grid.add(pie, grid_opts=opts.GridOpts(pos_left="80%"))

    return grid


@app.route("/getChart")
@login_required
def get_chart():
    c = local_data_charts()
    return c.dump_options_with_quotes()


@app.route('/global_data', methods=['POST', 'GET'])
@login_required
def global_data():
    user_history = User_history.query.all()
    user_plan_list = []
    for uh in user_history:
        user_plan_list.append(uh.plan_list.split(','))

    end_address_dict = dict()
    for user_plan in user_plan_list:
        for end_address in user_plan:
            if end_address_dict.get(end_address):
                end_address_dict[end_address] += 1
            else:
                end_address_dict[end_address] = 1

    business_user = Business_User.query.filter_by(username=current_user.username).first()
    business_address = business_user.business_address
    if end_address_dict.get(business_address):
        business_address_count = end_address_dict.get(business_address)
    else:
        business_address_count = 0
    return render_template('business_charts.html', user=current_user, business_user=business_user,
                           business_address=business_address, business_address_count=business_address_count)


def index_charts() -> Geo:
    time = datetime.now()
    time_str = datetime.strftime(time, '%Y-%m-%d %H:%M:%S')

    business_user = Business_User.query.filter_by(username=current_user.username).first()
    business_address = business_user.business_address
    user_history = User_history.query.all()
    user_plan_list = []
    for uh in user_history:
        user_plan_list.append(uh.plan_list.split(','))

    end_address_dict = dict()
    for user_plan in user_plan_list:
        for end_address in user_plan:
            if end_address_dict.get(end_address):
                end_address_dict[end_address] += 1
            else:
                end_address_dict[end_address] = 1
    end_address_list = list(end_address_dict.keys())
    end_address_count_list = list(end_address_dict.values())
    geo_address_count = []
    for i in range(len(end_address_list)):
        geo_address_count.append((end_address_list[i], end_address_count_list[i]))

    geo = (
        Geo()
        .add_schema(maptype="china", is_roam=False)
        .add(
            "",
            geo_address_count,
            type_=ChartType.HEATMAP,
        )
        .add("",
             [(business_address, 0)],
             type_=ChartType.EFFECT_SCATTER)
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(min_=0, max_=50, is_show=False),
            title_opts=opts.TitleOpts(title="各地区旅游热点图",
                                      subtitle="数据来源于本系统\n更新时间:{}".format(time_str),
                                      pos_left="10%"),
            tooltip_opts=opts.TooltipOpts(formatter="{b}"),
        )
    )
    return geo


@app.route("/indexCharts")
def get_index_chart():
    c = index_charts()
    return c.dump_options_with_quotes()


@app.route("/business_index")
@login_required
def business_index():
    business_user = Business_User.query.filter_by(username=current_user.username).first()
    return render_template('business_index.html', user=current_user, business_user=business_user)


def global_standard_charts() -> Grid:
    time = datetime.now()
    time_str = datetime.strftime(time, '%Y-%m-%d %H:%M:%S')

    user_history = User_history.query.all()
    user_standard_list = []
    for uh in user_history:
        user_standard_list.append(uh.standard_list.split(','))

    standard_dict = dict()
    for user_standard in user_standard_list:
        for end_address in user_standard:
            if standard_dict.get(end_address):
                standard_dict[end_address] += 1
            else:
                standard_dict[end_address] = 1

    standard_count = []
    standard_list = list(standard_dict.keys())
    count_list = list(standard_dict.values())
    sum_count = sum(count_list)
    per_count_list = []
    for c in count_list:
        per_count_list.append(round(c / sum_count, 3))
    for i in range(len(standard_dict)):
        standard_count.append((standard_list[i], per_count_list[i]))
    if len(standard_list) <= 8:
        pie = Pie()
        pie.add(series_name="",
                data_pair=standard_count,
                radius=["5%", "40%"],
                rosetype="area",
                )
        pie.set_global_opts(title_opts=opts.TitleOpts(title="各评价准则出现次数占比",
                                                      subtitle="更新时间:{}(每30秒自动更新一次)".format(time_str),
                                                      pos_left="40%", pos_bottom="20%"))
        pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    else:
        per_count_list_copy = copy.deepcopy(per_count_list)
        per_count_list_max8 = []
        per_count_list_max8_index = []
        for _ in range(8):
            number = max(per_count_list_copy)
            index = per_count_list_copy.index(number)
            per_count_list_copy[index] = 0
            per_count_list_max8.append(number)
            per_count_list_max8_index.append(index)
        max8_standard_list = []
        for i in per_count_list_max8_index:
            max8_standard_list.append(standard_count[i])
        max8_standard_list.append('其他')
        others_per_count = round(1 - sum(per_count_list_max8), 3)
        per_count_list_max8.append(others_per_count)
        standard_count_max8 = []
        for i in range(len(max8_standard_list)):
            standard_count_max8.append((max8_standard_list[i], per_count_list_max8[i]))

        pie = Pie()
        pie.add(series_name="",
                data_pair=standard_count_max8,
                radius=["5%", "40%"],
                rosetype="area",
                )
        pie.set_global_opts(title_opts=opts.TitleOpts(title="各评价标准出现次数占比",
                                                      subtitle="更新时间:{}(每30秒自动更新一次)".format(time_str),
                                                      pos_left="40%", pos_bottom="20%"))
        pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))

    standard_points = Standard_point.query.all()
    standard_point_dict = dict()
    standard_point_list = []
    for standard_point in standard_points:
        if standard_point_dict.get(standard_point.standard_name):
            standard_point_dict[standard_point.standard_name] += standard_point.standard_point
        else:
            standard_point_dict[standard_point.standard_name] = standard_point.standard_point
    standard_sum_point_list = list(standard_point_dict.values())
    for i in range(len(standard_sum_point_list)):
        standard_point_per = standard_sum_point_list[i] / count_list[i]
        standard_point_list.append(round(standard_point_per, 2))
    if len(standard_point_list) <= 8:
        bar = Bar()
        bar.add_xaxis(standard_list)
        bar.add_yaxis("", standard_point_list)
        bar.set_global_opts(title_opts=opts.TitleOpts(title="各评价准则在用户心中占比(TOP8)",
                                                      subtitle="更新时间:{}(每30秒自动更新一次)".format(time_str)))
    else:
        standard_point_list_copy = copy.deepcopy(standard_point_list)
        standard_point_list_max8 = []
        standard_point_list_max8_index = []
        for _ in range(8):
            number = max(standard_point_list_copy)
            index = standard_point_list_copy.index(number)
            standard_point_list_copy[index] = 0
            standard_point_list_max8.append(number)
            standard_point_list_max8_index.append(index)
        max8_standard_list = []
        for i in standard_point_list_max8_index:
            max8_standard_list.append(standard_list[i])
        bar = Bar()
        bar.add_xaxis(max8_standard_list)
        bar.add_yaxis("", standard_point_list_max8)
        bar.set_global_opts(title_opts=opts.TitleOpts(title="各评价准则在用户心中占比(TOP8)",
                                                      subtitle="更新时间:{}(每30秒自动更新一次)".format(time_str)))

    grid = Grid()
    grid.add(bar, grid_opts=opts.GridOpts(pos_right="65%"))
    grid.add(pie, grid_opts=opts.GridOpts(pos_left="80%"))

    return grid


@app.route("/globalCharts")
def get_global_standard():
    c = global_standard_charts()
    return c.dump_options_with_quotes()


@app.route("/global_standard", methods=['POST', 'GET'])
@login_required
def global_standard():
    business_user = Business_User.query.filter_by(username=current_user.username).first()
    return render_template("global_standard.html", user=current_user, business_user=business_user)


def local_source_charts() -> Grid:
    time = datetime.now()
    time_str = datetime.strftime(time, '%Y-%m-%d %H:%M:%S')

    business_user = Business_User.query.filter_by(username=current_user.username).first()
    plan_standards = Plan_standard.query.filter_by(plan_name=business_user.business_address).all()

    begin_address_list = []
    for plan_standard in plan_standards:
        begin_address_list.append(plan_standard.begin_address_name)
    begin_address_dot_list = []
    for begin_address in begin_address_list:
        begin_address_dot_list.append((begin_address, 0))

    line_list = []
    for begin_address in begin_address_list:
        line_list.append((begin_address, business_user.business_address))

    geo = Geo()
    geo.add_schema(maptype="china", is_roam=False)
    geo.add("",
            begin_address_dot_list,
            type_=ChartType.EFFECT_SCATTER,
            color="red",)
    geo.add("",
            [(business_user.business_address, 0)],
            type_=ChartType.EFFECT_SCATTER,
            color="blue",)
    geo.add("",
            line_list,
            type_=ChartType.LINES,
            effect_opts=opts.EffectOpts(
                symbol=SymbolType.ARROW, symbol_size=6, color="blue"
            ),
            linestyle_opts=opts.LineStyleOpts(curve=0.2),)
    geo.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    geo.set_global_opts(title_opts=opts.TitleOpts(title="游客来源图", subtitle="点击关闭中间tips可查看地图\n更新时间:{}".format(time_str)),
                        tooltip_opts=opts.TooltipOpts(formatter="{b}"))

    begin_address_count_dict = dict()
    for ba in begin_address_list:
        if begin_address_count_dict.get(ba):
            begin_address_count_dict[ba] += 1
        else:
            begin_address_count_dict[ba] = 1
    address_count_list = list(begin_address_count_dict.values())
    begin_address_list = list(begin_address_count_dict.keys())
    sum_count = sum(address_count_list)
    per_begin_address_count = []
    for bac in address_count_list:
        per_begin_address_count.append(round(bac / sum_count, 3))
    begin_address_count = []
    for i in range(len(begin_address_list)):
        begin_address_count.append((begin_address_list[i], per_begin_address_count[i]))
    if len(begin_address_list) <= 8:
        pie = Pie()
        pie.add(series_name="",
                data_pair=begin_address_count,
                radius=["5%", "40%"],
                rosetype="area",)
        pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    else:
        per_begin_address_count_copy = copy.deepcopy(per_begin_address_count)
        per_begin_address_count_list_max8 = []
        per_begin_address_count_list_max8_index = []
        for _ in range(8):
            number = max(per_begin_address_count_copy)
            index = per_begin_address_count_copy.index(number)
            per_begin_address_count_copy[index] = 0
            per_begin_address_count_list_max8.append(number)
            per_begin_address_count_list_max8_index.append(index)
        max8_begin_address_list = []
        for i in per_begin_address_count_list_max8_index:
            max8_begin_address_list.append(begin_address_list[i])
        max8_begin_address_list.append('其他')
        others_per_count = round(1 - sum(per_begin_address_count_list_max8), 3)
        per_begin_address_count_list_max8.append(others_per_count)
        begin_address_count_max8 = []
        for i in range(len(max8_begin_address_list)):
            begin_address_count_max8.append((max8_begin_address_list[i], per_begin_address_count_list_max8[i]))

        pie = Pie()
        pie.add(series_name="",
                data_pair=begin_address_count_max8,
                radius=["5%", "40%"],
                rosetype="area", )
        pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))

    grid = Grid()
    grid.add(geo, grid_opts=opts.GridOpts(pos_top="20%"))
    grid.add(pie, grid_opts=opts.GridOpts(pos_bottom="70%"))

    return grid


@app.route("/sourceCharts")
def get_source_charts():
    c = local_source_charts()
    return c.dump_options_with_quotes()


@app.route("/local_source_data")
@login_required
def local_source_data():
    business_user = Business_User.query.filter_by(username=current_user.username).first()
    return render_template("local_source_data.html", user=current_user, business_user=business_user)


def local_standard_charts() -> Grid:
    time = datetime.now()
    time_str = datetime.strftime(time, '%Y-%m-%d %H:%M:%S')

    business_user = Business_User.query.filter_by(username=current_user.username).first()
    plan_standards = Plan_standard.query.filter_by(plan_name=business_user.business_address).all()

    standard_list = []
    standard_point_list = []
    for plan_standard in plan_standards:
        standard_list.append(plan_standard.standard_name)
        standard_point_list.append(plan_standard.standard_point)

    standard_count_dict = dict()
    for s in standard_list:
        if standard_count_dict.get(s):
            standard_count_dict[s] += 1
        else:
            standard_count_dict[s] = 1
    standard_count_list = list(standard_count_dict.values())
    standard_list = list(standard_count_dict.keys())
    sum_count = sum(standard_count_list)
    per_standard_count = []
    for sc in standard_count_list:
        per_standard_count.append(round(sc / sum_count, 3))
    standard_count = []
    for i in range(len(standard_list)):
        standard_count.append((standard_list[i], per_standard_count[i]))
    if len(standard_list) <= 8:
        pie = Pie()
        pie.add(series_name="",
                data_pair=standard_count,
                radius=["5%", "40%"],
                rosetype="area", )
        pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        pie.set_global_opts(title_opts=opts.TitleOpts(title="游客主要需求", subtitle="更新时间:{}".format(time_str),
                                                      pos_left="40%", pos_bottom="20%"))
    else:
        per_standard_count_copy = copy.deepcopy(per_standard_count)
        per_standard_count_list_max8 = []
        per_standard_count_list_max8_index = []
        for _ in range(8):
            number = max(per_standard_count_copy)
            index = per_standard_count_copy.index(number)
            per_standard_count_copy[index] = 0
            per_standard_count_list_max8.append(number)
            per_standard_count_list_max8_index.append(index)
        max8_standard_list = []
        for i in per_standard_count_list_max8_index:
            max8_standard_list.append(standard_list[i])
        max8_standard_list.append('其他')
        others_per_count = round(1 - sum(per_standard_count_list_max8), 3)
        per_standard_count_list_max8.append(others_per_count)
        standard_count_max8 = []
        for i in range(len(max8_standard_list)):
            standard_count_max8.append((max8_standard_list[i], per_standard_count_list_max8[i]))

        pie = Pie()
        pie.add(series_name="",
                data_pair=standard_count_max8,
                radius=["5%", "40%"],
                rosetype="area", )
        pie.set_global_opts(title_opts=opts.TitleOpts(title="游客主要需求", subtitle="更新时间:{}".format(time_str),
                                                      pos_left="40%", pos_bottom="20%"))
        pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))

    standard_point_dict = dict()
    for i in range(len(standard_list)):
        if standard_point_dict.get(standard_list[i]):
            standard_point_dict[standard_list[i]] += standard_point_list[i]
        else:
            standard_point_dict[standard_list[i]] = standard_point_list[i]
    standard_sum_point_list = list(standard_point_dict.values())
    standard_point_per_list = []
    for i in range(len(standard_sum_point_list)):
        standard_point_per = standard_sum_point_list[i] / standard_count_list[i]
        standard_point_per_list.append(round(standard_point_per, 2))
    if len(standard_point_per_list) <= 8:
        bar = Bar()
        bar.add_xaxis(standard_list)
        bar.add_yaxis("", standard_point_per_list)
        bar.set_global_opts(title_opts=opts.TitleOpts(title="各需求在用户心中占比(TOP8)",
                                                      subtitle="更新时间:{}(每30秒自动更新一次)".format(time_str),
                                                      ))

    else:
        standard_point_list_copy = copy.deepcopy(standard_point_per_list)
        standard_point_list_max8 = []
        standard_point_list_max8_index = []
        for _ in range(8):
            number = max(standard_point_list_copy)
            index = standard_point_list_copy.index(number)
            standard_point_list_copy[index] = 0
            standard_point_list_max8.append(number)
            standard_point_list_max8_index.append(index)
        max8_standard_list = []
        for i in standard_point_list_max8_index:
            max8_standard_list.append(standard_list[i])
        bar = Bar()
        bar.add_xaxis(max8_standard_list)
        bar.add_yaxis("", standard_point_list_max8)
        bar.set_global_opts(title_opts=opts.TitleOpts(title="各需求在用户心中占比(TOP8)",
                                                      subtitle="更新时间:{}(每30秒自动更新一次)".format(time_str)))

    grid = Grid()
    grid.add(bar, grid_opts=opts.GridOpts(pos_right="65%"))
    grid.add(pie, grid_opts=opts.GridOpts(pos_left="80%"))

    return grid


@app.route("/standardCharts")
def get_local_standard_charts():
    c = local_standard_charts()
    return c.dump_options_with_quotes()


@app.route("/local_standard_data")
@login_required
def local_standard_data():
    business_user = Business_User.query.filter_by(username=current_user.username).first()
    return render_template("local_standard_data.html", user=current_user, business_user=business_user)


@app.route("/get_city_name", methods=["POST", "GET"])
@login_required
def get_city_name():
    business_user = Business_User.query.filter_by(username=current_user.username).first()
    business_address = business_user.business_address
    if request.method == 'POST':
        user_name = current_user.username
        address_name = request.form['address']
        is_address = baiduMap_location(address_name)
        try:
            if is_address['status'] == 1 or (is_address['result']['level'] not in address_range):
                flash('请输入正确的国内地址')
                return redirect(url_for('get_city_name'))
        except:
            is_address = gaodeMap_location(address_name)
            if is_address['status'] != 1 or (is_address['geocodes'][0]['level'] not in address_range):
                flash('请输入正确的国内地址')
                return redirect(url_for('location'))
        if not address_name:
            flash('无效的输入')
            return redirect(url_for('get_city_name'))
        add = Address(user_name=user_name, address_name=address_name)
        db.session.add(add)
        db.session.commit()
        return redirect(url_for('other_source_data'))
    return render_template('get_city_name.html', user=current_user,
                           business_user=business_user, business_address=business_address)


def other_source_charts() -> Grid:
    address_record = Address.query.filter_by(user_name=current_user.username).order_by(Address.id.desc()).first()
    address_name = address_record.address_name

    time = datetime.now()
    time_str = datetime.strftime(time, '%Y-%m-%d %H:%M:%S')

    plan_standards = Plan_standard.query.filter_by(plan_name=address_name).all()

    begin_address_list = []
    for plan_standard in plan_standards:
        begin_address_list.append(plan_standard.begin_address_name)
    begin_address_dot_list = []
    for begin_address in begin_address_list:
        begin_address_dot_list.append((begin_address, 0))

    line_list = []
    for begin_address in begin_address_list:
        line_list.append((begin_address, address_name))

    geo = Geo()
    geo.add_schema(maptype="china", is_roam=False)
    geo.add("",
            begin_address_dot_list,
            type_=ChartType.EFFECT_SCATTER,
            color="red", )
    geo.add("",
            [(address_name, 0)],
            type_=ChartType.EFFECT_SCATTER,
            color="blue", )
    geo.add("",
            line_list,
            type_=ChartType.LINES,
            effect_opts=opts.EffectOpts(
                symbol=SymbolType.ARROW, symbol_size=6, color="blue"
            ),
            linestyle_opts=opts.LineStyleOpts(curve=0.2), )
    geo.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    geo.set_global_opts(title_opts=opts.TitleOpts(title="游客来源图({a})".format(a=address_name),
                                                  subtitle="点击关闭中间tips可查看地图\n更新时间:{}".format(time_str)),
                        tooltip_opts=opts.TooltipOpts(formatter="{b}"))

    begin_address_count_dict = dict()
    for ba in begin_address_list:
        if begin_address_count_dict.get(ba):
            begin_address_count_dict[ba] += 1
        else:
            begin_address_count_dict[ba] = 1
    address_count_list = list(begin_address_count_dict.values())
    begin_address_list = list(begin_address_count_dict.keys())
    sum_count = sum(address_count_list)
    per_begin_address_count = []
    for bac in address_count_list:
        per_begin_address_count.append(round(bac / sum_count, 3))
    begin_address_count = []
    for i in range(len(begin_address_list)):
        begin_address_count.append((begin_address_list[i], per_begin_address_count[i]))
    if len(begin_address_list) <= 8:
        pie = Pie()
        pie.add(series_name="",
                data_pair=begin_address_count,
                radius=["5%", "40%"],
                rosetype="area", )
        pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    else:
        per_begin_address_count_copy = copy.deepcopy(per_begin_address_count)
        per_begin_address_count_list_max8 = []
        per_begin_address_count_list_max8_index = []
        for _ in range(8):
            number = max(per_begin_address_count_copy)
            index = per_begin_address_count_copy.index(number)
            per_begin_address_count_copy[index] = 0
            per_begin_address_count_list_max8.append(number)
            per_begin_address_count_list_max8_index.append(index)
        max8_begin_address_list = []
        for i in per_begin_address_count_list_max8_index:
            max8_begin_address_list.append(begin_address_list[i])
        max8_begin_address_list.append('其他')
        others_per_count = round(1 - sum(per_begin_address_count_list_max8), 3)
        per_begin_address_count_list_max8.append(others_per_count)
        begin_address_count_max8 = []
        for i in range(len(max8_begin_address_list)):
            begin_address_count_max8.append((max8_begin_address_list[i], per_begin_address_count_list_max8[i]))

        pie = Pie()
        pie.add(series_name="",
                data_pair=begin_address_count_max8,
                radius=["5%", "40%"],
                rosetype="area", )
        pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))

    grid = Grid()
    grid.add(geo, grid_opts=opts.GridOpts(pos_top="20%"))
    grid.add(pie, grid_opts=opts.GridOpts(pos_bottom="70%"))

    return grid


@app.route("/othersourceCharts")
def get_other_source_charts():
    c = other_source_charts()
    return c.dump_options_with_quotes()


@app.route("/other_source_data")
@login_required
def other_source_data():
    business_user = Business_User.query.filter_by(username=current_user.username).first()
    return render_template("other_source_data.html", user=current_user, business_user=business_user)


def other_standard_charts() -> Grid:
    address_record = Address.query.filter_by(user_name=current_user.username).order_by(Address.id.desc()).first()
    address_name = address_record.address_name

    time = datetime.now()
    time_str = datetime.strftime(time, '%Y-%m-%d %H:%M:%S')

    business_user = Business_User.query.filter_by(username=current_user.username).first()
    plan_standards = Plan_standard.query.filter_by(plan_name=address_name).all()

    standard_list = []
    standard_point_list = []
    for plan_standard in plan_standards:
        standard_list.append(plan_standard.standard_name)
        standard_point_list.append(plan_standard.standard_point)

    standard_count_dict = dict()
    for s in standard_list:
        if standard_count_dict.get(s):
            standard_count_dict[s] += 1
        else:
            standard_count_dict[s] = 1
    standard_count_list = list(standard_count_dict.values())
    standard_list = list(standard_count_dict.keys())
    sum_count = sum(standard_count_list)
    per_standard_count = []
    for sc in standard_count_list:
        per_standard_count.append(round(sc / sum_count, 3))
    standard_count = []
    for i in range(len(standard_list)):
        standard_count.append((standard_list[i], per_standard_count[i]))
    if len(standard_list) <= 8:
        pie = Pie()
        pie.add(series_name="",
                data_pair=standard_count,
                radius=["5%", "40%"],
                rosetype="area", )
        pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        pie.set_global_opts(title_opts=opts.TitleOpts(title="游客主要需求{}".format(address_name), subtitle="更新时间:{}".format(time_str),
                                                      pos_left="40%", pos_bottom="20%"))
    else:
        per_standard_count_copy = copy.deepcopy(per_standard_count)
        per_standard_count_list_max8 = []
        per_standard_count_list_max8_index = []
        for _ in range(8):
            number = max(per_standard_count_copy)
            index = per_standard_count_copy.index(number)
            per_standard_count_copy[index] = 0
            per_standard_count_list_max8.append(number)
            per_standard_count_list_max8_index.append(index)
        max8_standard_list = []
        for i in per_standard_count_list_max8_index:
            max8_standard_list.append(standard_list[i])
        max8_standard_list.append('其他')
        others_per_count = round(1 - sum(per_standard_count_list_max8), 3)
        per_standard_count_list_max8.append(others_per_count)
        standard_count_max8 = []
        for i in range(len(max8_standard_list)):
            standard_count_max8.append((max8_standard_list[i], per_standard_count_list_max8[i]))

        pie = Pie()
        pie.add(series_name="",
                data_pair=standard_count_max8,
                radius=["5%", "40%"],
                rosetype="area", )
        pie.set_global_opts(title_opts=opts.TitleOpts(title="游客主要需求", subtitle="更新时间:{}".format(time_str),
                                                      pos_left="40%", pos_bottom="20%"))
        pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))

    standard_point_dict = dict()
    for i in range(len(standard_list)):
        if standard_point_dict.get(standard_list[i]):
            standard_point_dict[standard_list[i]] += standard_point_list[i]
        else:
            standard_point_dict[standard_list[i]] = standard_point_list[i]
    standard_sum_point_list = list(standard_point_dict.values())
    standard_point_per_list = []
    for i in range(len(standard_sum_point_list)):
        standard_point_per = standard_sum_point_list[i] / standard_count_list[i]
        standard_point_per_list.append(round(standard_point_per, 2))
    if len(standard_point_per_list) <= 8:
        bar = Bar()
        bar.add_xaxis(standard_list)
        bar.add_yaxis("", standard_point_per_list)
        bar.set_global_opts(title_opts=opts.TitleOpts(title="各需求在用户心中占比(TOP8)",
                                                      subtitle="更新时间:{}(每30秒自动更新一次)".format(time_str),
                                                      ))

    else:
        standard_point_list_copy = copy.deepcopy(standard_point_per_list)
        standard_point_list_max8 = []
        standard_point_list_max8_index = []
        for _ in range(8):
            number = max(standard_point_list_copy)
            index = standard_point_list_copy.index(number)
            standard_point_list_copy[index] = 0
            standard_point_list_max8.append(number)
            standard_point_list_max8_index.append(index)
        max8_standard_list = []
        for i in standard_point_list_max8_index:
            max8_standard_list.append(standard_list[i])
        bar = Bar()
        bar.add_xaxis(max8_standard_list)
        bar.add_yaxis("", standard_point_list_max8)
        bar.set_global_opts(title_opts=opts.TitleOpts(title="各需求在用户心中占比(TOP8)",
                                                      subtitle="更新时间:{}(每30秒自动更新一次)".format(time_str)))

    grid = Grid()
    grid.add(bar, grid_opts=opts.GridOpts(pos_right="65%"))
    grid.add(pie, grid_opts=opts.GridOpts(pos_left="80%"))

    return grid


@app.route("/otherstandardCharts")
def get_other_standard_charts():
    c = other_standard_charts()
    return c.dump_options_with_quotes()


@app.route("/other_standard_data")
@login_required
def other_standard_data():
    business_user = Business_User.query.filter_by(username=current_user.username).first()
    return render_template("other_standard_data.html", user=current_user, business_user=business_user)


def admin_index_charts() -> Geo:
    time = datetime.now()
    time_str = datetime.strftime(time, '%Y-%m-%d %H:%M:%S')

    business_user = Business_User.query.filter_by(username=current_user.username).first()
    business_address = business_user.business_address
    user_history = User_history.query.all()
    user_plan_list = []
    for uh in user_history:
        user_plan_list.append(uh.plan_list.split(','))

    end_address_dict = dict()
    for user_plan in user_plan_list:
        for end_address in user_plan:
            if end_address_dict.get(end_address):
                end_address_dict[end_address] += 1
            else:
                end_address_dict[end_address] = 1
    end_address_list = list(end_address_dict.keys())
    end_address_count_list = list(end_address_dict.values())
    geo_address_count = []
    for i in range(len(end_address_list)):
        geo_address_count.append((end_address_list[i], end_address_count_list[i]))

    geo = (
        Geo()
        .add_schema(maptype="china", is_roam=False)
        .add(
            "",
            geo_address_count,
            type_=ChartType.HEATMAP,
        )
        .add("",
             [(business_address, 0)],
             type_=ChartType.EFFECT_SCATTER)
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(min_=0, max_=50, is_show=False),
            title_opts=opts.TitleOpts(title="各地区旅游热点图",
                                      subtitle="数据来源于本系统\n更新时间:{}".format(time_str),
                                      pos_left="10%"),
            tooltip_opts=opts.TooltipOpts(formatter="{b}"),
        )
    )
    return geo


@app.route("/adminindexCharts")
def get_admin_index_chart():
    c = admin_index_charts()
    return c.dump_options_with_quotes()


@app.route("/admin_index", methods=['GET', 'POST'])
@login_required
def admin_index():
    return render_template("admin_index.html", user=current_user)


@app.route("/admin/user_page", methods=['GET', 'POST'])
@login_required
def admin_change_user_page():
    recommend_plans = Recommend_plan.query.all()
    recommend_standards = Recommend_standard.query.all()

    plan_standards = Plan_standard.query.all()
    plan_count_dict = {}
    for recommend_plan in recommend_plans:
        plan_count_dict[recommend_plan.recommend_plan_name] = 0

    plan_name_list = list(plan_count_dict.keys())
    plan_count_list = list(plan_count_dict.values())

    for i in range(len(plan_standards)):
        plan_name = plan_standards[i].plan_name
        if plan_name in plan_name_list:
            index = plan_name_list.index(plan_name)
            plan_count_list[index] += 1

    sum_count = sum(plan_count_list)
    plan_count_list_per = []
    for pc in plan_count_list:
        try:
            plan_count_list_per.append(round(pc / sum_count, 2))
        except ZeroDivisionError:
            plan_count_list_per.append(0.00)

    if request.method == 'POST':
        recommend_plan_name = request.form['recommend_plan']
        try:
            is_address = baiduMap_location(recommend_plan_name)
            if is_address['status'] == 1 or (is_address['result']['level'] not in address_range):
                flash('请输入正确的国内地址')
                return redirect(url_for('admin_change_user_page'))
        except:
            is_address = gaodeMap_location(recommend_plan_name)
            if is_address['status'] != 1 or (is_address['geocodes'][0]['level'] not in address_range):
                flash('请输入正确的国内地址')
                return redirect(url_for('admin_change_user_page'))
        if not recommend_plan_name:
            flash('无效的输入')
            return redirect(url_for('admin_change_user_page'))
        try:
            p = Recommend_plan(recommend_plan_name=recommend_plan_name)
            db.session.add(p)
            db.session.commit()
            flash('备选方案添加成功')
            return redirect(url_for('admin_change_user_page'))
        except:
            flash('已存在该备选方案')
            return redirect(url_for('admin_change_user_page'))

    return render_template("admin_change_user_page.html", user=current_user,
                           recommend_plans=recommend_plans,
                           plan_name_list=plan_name_list, plan_count_list_per=plan_count_list_per)


@app.route('/admin/user_page/recommend_plan/delete/<int:recommend_plan_id>', methods=['POST'])
@login_required
def delete_recommend_plan(recommend_plan_id):
    del_p = Recommend_plan.query.get_or_404(recommend_plan_id)
    db.session.delete(del_p)
    db.session.commit()
    flash('一个备选方案删除成功')
    return redirect(url_for('admin_change_user_page'))


@app.route("/admin/user_page_standard", methods=['GET', 'POST'])
@login_required
def admin_change_user_page_s():
    recommend_standards = Recommend_standard.query.all()

    plan_standards = Plan_standard.query.all()
    standard_count_dict = {}
    for recommend_standard in recommend_standards:
        standard_count_dict[recommend_standard.recommend_standard_name] = 0

    standard_name_list = list(standard_count_dict.keys())
    standard_count_list = list(standard_count_dict.values())

    for i in range(len(plan_standards)):
        standard_name = plan_standards[i].standard_name
        if standard_name in standard_name_list:
            index = standard_name_list.index(standard_name)
            standard_count_list[index] += 1

    sum_count = sum(standard_count_list)
    standard_count_list_per = []
    for pc in standard_count_list:
        try:
            standard_count_list_per.append(round(pc / sum_count, 2))
        except ZeroDivisionError:
            standard_count_list_per.append(0.00)

    if request.method == "POST":
        recommend_standard_name = request.form['recommend_standard']

        if not recommend_standard_name:
            flash('无效的输入')
            return redirect(url_for('admin_change_user_page_s'))
        try:
            s = Recommend_standard(recommend_standard_name=recommend_standard_name)
            db.session.add(s)
            db.session.commit()
            flash('评价准则添加成功')
            return redirect(url_for('admin_change_user_page_s'))
        except:
            flash('已存在该评价准则')
            return redirect(url_for('admin_change_user_page_s'))

    return render_template("admin_change_user_page_s.html", user=current_user,
                           recommend_standards=recommend_standards,
                           standard_name_list=standard_name_list, standard_count_list_per=standard_count_list_per)


@app.route('/admin/user_page/recommend_standard/delete/<int:recommend_standard_id>', methods=['POST'])
@login_required
def delete_recommend_standard(recommend_standard_id):
    del_s = Recommend_standard.query.get_or_404(recommend_standard_id)
    db.session.delete(del_s)
    db.session.commit()
    flash('一个备选方案删除成功')
    return redirect(url_for('admin_change_user_page'))


@app.route('/admin/user_info', methods=['GET', 'POST'])
@login_required
def admin_user_info():
    person_users = User.query.filter_by(identity='person')
    length = 0
    for p in person_users:
        length += 1
    if request.method == 'POST':
        query_type = request.form['query_type']
        query_text = request.form['query_text']
        if query_type == 'username':
            person_users = User.query.filter_by(identity='person', username=query_text)
            length = 0
            for p in person_users:
                length += 1
            return render_template('admin_user_info.html', user=current_user, person_users=person_users, length=length)
        elif query_type == 'id':
            person_users = User.query.filter_by(identity='person', id=query_text)
            length = 0
            for p in person_users:
                length += 1
            return render_template('admin_user_info.html', user=current_user, person_users=person_users, length=length)
        elif query_type == 'name':
            person_users = User.query.filter_by(identity='person', name=query_text)
            length = 0
            for p in person_users:
                length += 1
            return render_template('admin_user_info.html', user=current_user, person_users=person_users, length=length)
    return render_template('admin_user_info.html', user=current_user,
                           person_users=person_users, length=length)


@app.route('/admin/user_info_business', methods=['GET', 'POST'])
@login_required
def admin_user_info_business():
    business_users = User.query.filter_by(identity='business')
    length = 0
    for p in business_users:
        length += 1
    if request.method == 'POST':
        query_type = request.form['query_type']
        query_text = request.form['query_text']
        if query_type == 'username':
            business_users = User.query.filter_by(identity='business', username=query_text)
            length = 0
            for p in business_users:
                length += 1
            return render_template('admin_user_info_business.html', user=current_user,
                                   business_users=business_users, length=length)
        elif query_type == 'id':
            business_users = User.query.filter_by(identity='business', id=query_text)
            length = 0
            for p in business_users:
                length += 1
            return render_template('admin_user_info_business.html', user=current_user,
                                   business_users=business_users, length=length)
        elif query_type == 'name':
            business_users = User.query.filter_by(identity='business', name=query_text)
            length = 0
            for p in business_users:
                length += 1
            return render_template('admin_user_info_business.html', user=current_user,
                                   business_users=business_users, length=length)
    return render_template('admin_user_info_business.html', user=current_user,
                           business_users=business_users, length=length)


@app.route('/admin/user_detail/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_detail(user_id):
    query_user = User.query.get_or_404(user_id)
    user_load_times = User_load_time.query.filter_by(user_name=query_user.username).all()
    feedbacks = Feedback_history.query.filter_by(user_name=query_user.username).all()
    feedback_list = []
    for feedback in feedbacks:
        if len(feedback.content) <= 20:
            feedback_list.append(feedback.content)
        else:
            feedback_str = feedback.content
            feedback_list.append(feedback_str[0:20])
    return render_template('user_detail.html', user=current_user, query_user=query_user,
                           user_load_times=user_load_times, feedback_list=feedback_list)


@app.route('/user/feedback', methods=['GET', 'POST'])
@login_required
def user_feedback():
    if request.method == 'POST':
        user_name = current_user.username
        identity = current_user.identity
        content = request.form['content']
        feed_back = Feedback(user_name=user_name, identity=identity, content=content)
        db.session.add(feed_back)
        db.session.commit()
        flash('提交成功,感谢您的支持！')
        if current_user.identity == 'person':
            return redirect(url_for('plan'))
        elif current_user.identity == 'business':
            return redirect(url_for('business_index'))

    if current_user.identity == 'person':
        return render_template('user_feedback.html', user=current_user)
    elif current_user.identity == 'business':
        business_user = Business_User.query.filter_by(username=current_user.username).first()
        return render_template('user_feedback.html', user=current_user, business_user=business_user)


@app.route('/admin/monitor', methods=['GET', 'POST'])
@login_required
def admin_monitor():
    feedbacks = Feedback.query.all()
    length = 0
    for f in feedbacks:
        length += 1
    if request.method == 'POST':
        text = request.form['text']
        type = request.form['type']
        if type == 'username':
            feedbacks = Feedback.query.filter_by(user_name=text).all()
            length = 0
            for f in feedbacks:
                length += 1
            return render_template('admin_monitor.html', user=current_user, feedbacks=feedbacks, length=length)
        elif type == 'identity':
            feedbacks = Feedback.query.filter_by(identity=text).all()
            length = 0
            for f in feedbacks:
                length += 1
            return render_template('admin_monitor.html', user=current_user, feedbacks=feedbacks, length=length)
    return render_template('admin_monitor.html', user=current_user, feedbacks=feedbacks, length=length)


@app.route('/admin/feedback/detail/<int:feedback_id>', methods=['GET', 'POST'])
@login_required
def feedback_detail(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    user_name = feedback.user_name
    identity = feedback.identity
    content = feedback.content
    feedback_history = Feedback_history(user_name=user_name, identity=identity, content=content)
    db.session.delete(feedback)
    db.session.commit()
    db.session.add(feedback_history)
    db.session.commit()
    return render_template('feedback_detail.html', user=current_user, feedback=feedback)


@app.route('/admin/feedback', methods=['GET', 'POST'])
@login_required
def admin_feedback():
    feedbacks = Feedback_history.query.all()
    length = 0
    contents = []
    for feedback in feedbacks:
        length += 1
        if len(feedback.content) <= 8:
            contents.append(feedback.content)
        else:
            content = feedback.content
            contents.append("{}...".format(content[0: 8]))

    if request.method == 'POST':
        text = request.form['text']
        type = request.form['type']
        if type == 'username':
            feedbacks = Feedback.query.filter_by(user_name=text).all()
            length = 0
            contents = []
            for feedback in feedbacks:
                length += 1
                if len(feedback.content) <= 8:
                    contents.append(feedback.content)
                else:
                    content = feedback.content
                    contents.append("{}...".format(content[0: 8]))
            return render_template('admin_feedback.html', user=current_user, feedbacks=feedbacks, length=length)
        elif type == 'identity':
            feedbacks = Feedback.query.filter_by(identity=text).all()
            length = 0
            contents = []
            for feedback in feedbacks:
                length += 1
                if len(feedback.content) <= 8:
                    contents.append(feedback.content)
                else:
                    content = feedback.content
                    contents.append("{}...".format(content[0: 8]))
            return render_template('admin_feedback.html', user=current_user, feedbacks=feedbacks, length=length)
    return render_template('admin_feedback.html', user=current_user, feedbacks=feedbacks, length=length, contents=contents)


@app.route('/admin/feedback_read/detail/<int:feedback_id>', methods=['GET', 'POST'])
@login_required
def feedback_read_detail(feedback_id):
    feedback = Feedback_history.query.get_or_404(feedback_id)
    return render_template('feedback_detail.html', user=current_user, feedback=feedback)
