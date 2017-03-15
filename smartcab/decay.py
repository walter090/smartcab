import numpy as np


def linear(epsilon, a, t):
    return epsilon - a if t > 0 else epsilon


def exponential(a, t):
    return a ** t


def quadratic(t):
    return 1/float(t ** 2)


def e_ex(a, t):
    return np.exp(-a * t)


def cosine(a, t):
    return np.cos(a * t)
