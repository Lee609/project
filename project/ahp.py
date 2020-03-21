import numpy as np
import random


RI = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}


def transpose(matrix):
    n = len(matrix)
    matrix_transpose = []
    for i in range(n):
        list0 = [x[i] for x in matrix]
        matrix_transpose.append(list0)
    return matrix_transpose


def get_w_before(matrix):
    n = len(matrix)
    col_matrix = []
    w_before = []
    w = []

    col_matrix_before = transpose(matrix)

    for i in range(n):
        col_matrix.append([])

    for i in range(len(col_matrix_before)):
        sum_col_ls = sum(col_matrix_before[i])
        for x in col_matrix_before[i]:
            col_matrix[i].append(round(x / sum_col_ls, 2))

    matrix_row = transpose(col_matrix)

    for row_ls in matrix_row:
        sum_row = sum(row_ls)
        w_before.append(sum_row)

    sum_w = sum(w_before)
    for x in w_before:
        w.append(round(x / sum_w, 2))
    w = np.array(w)
    w = w.reshape((w.shape[0], 1))
    return w


def get_lamda(matrix):
    w = get_w_before(matrix)
    A = np.array(matrix)
    Aw = np.matmul(A, w)
    n = len(matrix)
    sum_l = 0
    for i in range(n):
        sum_l += Aw[i] / w[i]
    sum_l = sum_l[0]
    lamd = sum_l / n
    return round(lamd, 2)


def modify_matrix(matrix):
    a_len = len(matrix)
    modify_pos_row = random.randint(0, a_len - 1)
    modify_pos_col = random.randint(0, a_len - 1)
    if matrix[modify_pos_row][modify_pos_col] >= 1:
        if 1 <= matrix[modify_pos_row][modify_pos_col] < 3:
            matrix[modify_pos_row][modify_pos_col] = matrix[modify_pos_row][modify_pos_col] + 1
            matrix[modify_pos_col][modify_pos_row] = 1 / matrix[modify_pos_row][modify_pos_col]
        elif 3 <= matrix[modify_pos_row][modify_pos_col] < 5:
            matrix[modify_pos_row][modify_pos_col] = matrix[modify_pos_row][modify_pos_col] + 1
            matrix[modify_pos_col][modify_pos_row] = 1 / matrix[modify_pos_row][modify_pos_col]
        elif 5 <= matrix[modify_pos_row][modify_pos_col] < 7:
            matrix[modify_pos_row][modify_pos_col] = matrix[modify_pos_row][modify_pos_col] + 1
            matrix[modify_pos_col][modify_pos_row] = 1 / matrix[modify_pos_row][modify_pos_col]
        elif 7 <= matrix[modify_pos_row][modify_pos_col] < 9:
            matrix[modify_pos_row][modify_pos_col] = matrix[modify_pos_row][modify_pos_col] + 1
            matrix[modify_pos_col][modify_pos_row] = 1 / matrix[modify_pos_row][modify_pos_col]
    else:
        if 1 <= matrix[modify_pos_col][modify_pos_row] < 3:
            matrix[modify_pos_col][modify_pos_row] = matrix[modify_pos_col][modify_pos_row] + 1
            matrix[modify_pos_row][modify_pos_col] = 1 / matrix[modify_pos_col][modify_pos_row]
        elif 3 <= matrix[modify_pos_col][modify_pos_row] < 5:
            matrix[modify_pos_col][modify_pos_row] = matrix[modify_pos_col][modify_pos_row] + 1
            matrix[modify_pos_row][modify_pos_col] = 1 / matrix[modify_pos_col][modify_pos_row]
        elif 5 <= matrix[modify_pos_col][modify_pos_row] < 7:
            matrix[modify_pos_col][modify_pos_row] = matrix[modify_pos_col][modify_pos_row] + 1
            matrix[modify_pos_row][modify_pos_col] = 1 / matrix[modify_pos_col][modify_pos_row]
        elif 7 <= matrix[modify_pos_col][modify_pos_row] < 9:
            matrix[modify_pos_col][modify_pos_row] = matrix[modify_pos_col][modify_pos_row] + 1
            matrix[modify_pos_row][modify_pos_col] = 1 / matrix[modify_pos_col][modify_pos_row]

    return matrix


def get_CR(matrix):
    lamd = get_lamda(matrix)
    n = len(matrix)
    CI = (lamd - n) / (n - 1)
    CR = round((CI / RI[n]), 2)
    return CR


def get_w(matrix):
    w = get_w_before(matrix)
    w_list = []
    for l in w:
        w_list.append(list(l)[0])
    CR = get_CR(matrix)
    if CR < 0.1:
        return w_list
    else:
        matrix = modify_matrix(matrix)
        return get_w(matrix)


def get_result(data_standard, data_plan):
    n_standard = len(data_standard)
    score_each_standard = []
    for dp in data_plan:
        score_each_standard.append(get_w(dp))

    n_plan = len(data_plan[0])

    w_each_plan = []
    for i in range(n_plan):
        w_each_plan.append([])
    for i in range(n_plan):
        w_each_plan[i] = [x[i] for x in score_each_standard]

    w_standard = get_w(data_standard)

    result_before = []
    for i in range(n_plan):
        sum_score = 0
        for j in range(n_standard):
            sum_score += w_each_plan[i][j] * w_standard[j]
        result_before.append(round(sum_score, 2))

    result = []
    sum_result = sum(result_before)
    for i in range(n_plan):
        result.append(round(result_before[i] / sum_result, 2))

    return result, w_each_plan, w_standard


if __name__ == '__main__':
    data_standard = [[1, 2, 7, 5, 5],
                     [1 / 2, 1, 4, 3, 3],
                     [1 / 7, 1 / 4, 1, 1 / 2, 1 / 3],
                     [1 / 5, 1 / 3, 2, 1, 1],
                     [1 / 5, 1 / 3, 3, 1, 1]]
    data_plan = [[[1, 1 / 3, 1 / 8],
                  [3, 1, 1 / 3],
                  [8, 3, 1]],
                 [[1, 2, 5],
                  [1 / 2, 1, 2],
                  [1 / 5, 1 / 2, 1]],
                 [[1, 1, 3],
                  [1, 1, 3],
                  [1 / 3, 1 / 3, 1]],
                 [[1, 3, 4],
                  [1 / 3, 1, 1],
                  [1 / 4, 1, 1]],
                 [[1, 4, 1 / 2],
                  [1 / 4, 1, 1 / 4],
                  [2, 4, 1]]]
    result = get_result(data_standard, data_plan)
    print(result[0])
    print(result[1])
    print(result[2])



