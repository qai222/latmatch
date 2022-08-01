import math

import pandas as pd
from shapely.geometry.polygon import Polygon

'''
read csv generated by grep2csv.py

for each entry, calculate value M based on a given triplet (a, b, gamma) which stands for the periodicity of
substrate surface

0 < asub < bsub, gammasub <= 90

let S and T (top layer) be the sets of points in two parallelograms defined by triplets (a, b, gamma), 
we define a similarity measure M as: M = union(S-T, T-S).area/S.area

notice for T the triplet can also be (a, c, beta) or (b, c, alpha), here we just take the smallest m 
'''


def cos(a):
    a = math.radians(a)
    return round(math.cos(a), 6)  # shapely intersection does weird things if not rounded


def sin(a):
    a = math.radians(a)
    return round(math.sin(a), 6)


def get_polygon(triplet):
    a, b, g = triplet
    if g > 90:
        g = 180 - g
    p = Polygon(
        [
            (0, 0),
            (b * cos(g), b * sin(g)),
            (a + b * cos(g), b * sin(g)),
            (a, 0)
        ]
    )
    return p


def cal_m_triplet(S, T):
    ps = get_polygon(S)
    pt = get_polygon(T)
    m1 = abs((ps.area + pt.area - 2 * ps.intersection(pt).area) / ps.area)
    T[0], T[1] = T[1], T[0]
    pt = get_polygon(T)
    m2 = abs((ps.area + pt.area - 2 * ps.intersection(pt).area) / ps.area)
    return min(m1, m2)


def cal_m_params(S, params):
    a, b, c, alpha, beta, gamma = params
    triplets = [[a, b, gamma], [a, c, beta], [b, c, alpha]]
    return min([cal_m_triplet(S, t) for t in triplets])


if __name__ == '__main__':
    S = [7.175, 14.435, 90]  # this is from rubrene

    df = pd.read_csv('latdata.csv', sep=";;;", engine="python")
    allparams = df.values[:, 2:8]
    ms = pd.Series([cal_m_params(S, params) for params in allparams], index=df.index)
    df = df.assign(m=ms)
    print('matching against', S)
    df.to_excel('match_results.xlsx')