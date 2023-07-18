#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 13:36:59 2023

@author: itqs
"""
#https://stackoverflow.com/questions/68250191/how-to-calculate-object-keypoint-similarity
import numpy as np



def oks(y_true, y_pred, visibility):
    # You might want to set these global constant
    # outside the function scope
    KAPPA = np.array([1] * len(y_true))
    # The object scale
    # You might need a dynamic value for the object scale
    SCALE = 1.0

    # Compute the L2/Euclidean Distance
    distances = np.linalg.norm(y_pred - y_true, axis=-1)
    # Compute the exponential part of the equation
    exp_vector = np.exp(-(distances**2) / (2 * (SCALE**2) * (KAPPA**2)))
    # The numerator expression
    v1_m = np.ma.array(exp_vector, mask=np.isnan(exp_vector))
    v2_m = np.ma.array(visibility, mask=np.isnan(exp_vector)).astype(int)
    numerator = np.ma.dot(v1_m, v2_m)
    # The denominator expression
    denominator = np.ma.sum(v2_m)
    return numerator / denominator


def oks_score_bodypoints(obj_left,obj_right,visibility):
    oks_score=oks(obj_left.keypoint,obj_right.keypoint,visibility)
    return oks_score

# if __name__ == "__main__":
#     IMAGE_SIZE_IN_PIXEL = 50
#     gt = (np.random.random((17, 3)) * IMAGE_SIZE_IN_PIXEL).astype(int)
#     pred = (np.random.random((17, 3)) * IMAGE_SIZE_IN_PIXEL).astype(int)
#     visibility = (np.random.random((17, 1)) * 3).astype(int)

#     # On this example the value will not be correct
#     # since you need to calibrate KAPPA and SCALE
#     print("OKS", oks(gt, pred, visibility))