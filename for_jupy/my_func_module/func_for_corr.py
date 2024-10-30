import pandas as pd
import numpy as np


"""
Удаление выбросов с использованием межквартильного размаха (IQR)
"""
def get_filter_df(df, col):
    # Определяем Q1 и Q3 квартили
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    
    # Вычисляем IQR
    IQR = Q3 - Q1
    
    # Определяем границы для определения выбросов
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Фильтруем выбросы
    return df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]


"""
Создание матрицы расстояний и произведение значений
"""
def get_corr(points, values, max_h, start=0, step=1, normal=False):
    def matrix_distance_and_value(points, values):

        l = len(points)
        D = np.zeros((l, l))
        V = np.zeros((l, l))
        M = np.mean(values)
        var = np.var(values)

        for i in range(l):
            for j in range(i, l):
                distance = np.linalg.norm(points[i] - points[j])
                D[i, j] = distance

                if normal:
                    V[i, j] = (values[i]-M)*(values[j]-M) / var
                else:
                    V[i, j] = (values[i]-M)*(values[j]-M)
        return D, V
    
    
    corr_list, h_list = [], []
    D, V = matrix_distance_and_value(points, values)
    
    for h in range(start, max_h, step):
        """
        Суммарная корреляция в диапазоне (h-step, h-step]
        """
        sum_V = np.sum(np.where((D <= h) & (D > h-step), V, 0))

        """
        количество элементов в диапазоне (h-step, h-step]
        """
        D_list = D.reshape(-1)
        num_V = np.where((D_list <= h) & (D_list > h-step))[0].shape[0]

        if h == 0:
            """
            Частный случай корр. в точки 0
            """
            num_V = len(points)

        h_list.append(h)
        corr_list.append(sum_V/num_V)
    
    return np.array(h_list), np.array(corr_list)
	