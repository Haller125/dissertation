import math

def sigmoid(x, bias=0.0):
    return 1.0 / (1.0 + math.exp(-(bias + x)))
