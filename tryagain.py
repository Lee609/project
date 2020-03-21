# a = '北京,南京,天津'
# b = list(a)  # 字符串列表化
# # c = ','.join(b)  # 列表字符串化
# d = a.split(',')  # split对单词列表化不是对每个字母
# print('b is :', b)
# print('d is :', d)
#
# # print('c is:', c)
#
# for i in d:
#     print(i)

import copy
m = [34,94,35,78,45,67,23,90,1,0]
t = copy.deepcopy(m)
# 求m个最大的数值及其索引
max_number = []
max_index = []
for _ in range(2):
    number = max(t)
    index = t.index(number)
    t[index] = 0
    max_number.append(number)
    max_index.append(index)
t = []
print(max_number)
print(max_index)


