import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# recommend_standards = [(1, '离我距离'),
#                        (2, '前往方式'),
#                        (3, '当地景色'),
#                        (4, '住宿费用'),
#                        (5, '消费水平'),
#                        (6, '小吃美食')]
#
# cursor.executemany('''insert into Recommend_standard values(?, ?)''', recommend_standards)
# conn.commit()
#
#
#
#
# recommend_plans = [(1, '长沙'), (2, '重庆'), (3, '成都'), (4, '南京'),
#                    (5, '桂林'), (6, '三亚'), (7, '北京'), (8, '深圳'),
#                    (9, '上海'), (10, '厦门'), (11, '天津'), (12, '海口'),
#                    (13, '杭州'), (14, '苏州'), (15, '青岛'), (16, '丽江'),
#                    (17, '武汉'), (18, '郑州'), (19, '洛阳'), (20, '广州')]
# cursor.executemany('''insert into Recommend_plan values(?, ?)''', recommend_plans)
# conn.commit()

# cursor.execute('''insert into user values(0, '管理员', 'admin', 'pbkdf2:sha256:150000$H1SymrhC$920b9068ab632d03d64ed5977694c19227a9ba5f72e1784478bacc74a2ea2b45', 'admin')''')
# conn.commit()
# delete_sql = '''delete from user_load_time where out_time is null'''
# cursor.execute(delete_sql)
# conn.commit()

query_sql = '''select * from feedback_history'''
query_result = cursor.execute(query_sql).fetchall()
for qr in query_result:
    print(qr)



# import datetime
# time_list = []
# for q in query_result:
#     if q[3]:
#         time_list.append('{}:00'.format(q[2][0:16]))
# print(time_list)
#
#
# def get_list(date):
#     return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp()
#
#
# ls = sorted(time_list, key=lambda date: get_list(date))
# print(ls)






# import sqlite3
#
# conn = sqlite3.connect('data.db')
# cu = conn.cursor()
#
# # 获取表名，保存在tab_name列表
# cu.execute("select name from sqlite_master where type='table'")
# tab_name = cu.fetchall()
# tab_name = [line[0] for line in tab_name]
#
# # 获取表的列名（字段名），保存在col_names列表,每个表的字段名集为一个元组
# col_names = []
# for line in tab_name:
#     cu.execute('pragma table_info({})'.format(line))
#     col_name = cu.fetchall()
#     col_name = [x[1] for x in col_name]
#     col_names.append(col_name)
#     col_name = tuple(col_name)
#
# for c in col_names:
#     print(c)

