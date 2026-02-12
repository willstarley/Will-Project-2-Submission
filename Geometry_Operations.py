#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 11:25:01 2021

@author: kendrick shepherd
"""

import math
import numpy as np
import sys

# length of the beam
def Length(bar):
    # find a node of the bar
    bar_node = bar.init_node
    # convert the node and bar to a vector
    vector = BarNodeToVector(bar_node,bar)
    # find the length of a vector
    length = VectorTwoNorm(vector)
    # output the vector length
    return length

# Find two norm (magnitude) of a vector
def VectorTwoNorm(vector):
    norm = 0
    for i in range(0, len(vector)):
        norm += vector[i]**2
    return np.sqrt(norm)

# Find a shared node between two bars
def FindSharedNode(bar_1,bar_2):
    if(bar_1.init_node==bar_2.init_node):
        return bar_1.init_node
    elif(bar_1.init_node==bar_2.end_node):
        return bar_1.init_node
    elif(bar_2.init_node==bar_1.end_node):
        return bar_2.init_node
    elif(bar_1.end_node==bar_2.end_node):
        return bar_1.end_node
    else:
        sys.exit("The two input bars do not share a node")

# Given a bar and a node on that bar, find the other node
def FindOtherNode(node,bar):
    if(bar.init_node == node):
        return bar.end_node
    elif(bar.end_node == node):
        return bar.init_node
    else:
        sys.exit("The input node is not on the bar")

# Find a vector from input node (of the input bar) in the direction of the bar
def BarNodeToVector(origin_node,bar):
    other_node = FindOtherNode(origin_node, bar)
    origin_loc = origin_node.location
    other_loc = other_node.location
    vec = [other_loc[0]-origin_loc[0], other_loc[1]-origin_loc[1]]
    return vec

# Convert to bars that meet at a node into vectors pointing away from that node
def BarsToVectors(bar_1,bar_2):
    shared_node = FindSharedNode(bar_1,bar_2)
    vec1 = BarNodeToVector(shared_node,bar_1)
    vec2 = BarNodeToVector(shared_node,bar_2)
    return vec1
    return vec2
# ^^ There appears to be an error somewhere here

# Cross product of two vectors
def TwoDCrossProduct(vec1,vec2):
    x1 = vec1[0]
    y1 = vec1[1]
    
    x2 = vec2[0]
    y2 = vec2[1]
    
    xp = (x1 * y2) - (y1 * x2)
    return xp

# Dot product of two vectors
def DotProduct(vec1,vec2):
    dot_prod = 0
    for i in range(0, len(vec1)):
        dot_prod += vec1[i] * vec2[i]    
    return dot_prod

# Cosine of angle from local x vector direction to other vector
def CosineVectors(local_x_vec,other_vec):
    numcos = DotProduct(local_x_vec, other_vec)
    denomcos = (VectorTwoNorm(local_x_vec))*(VectorTwoNorm(other_vec))
    cos = numcos/denomcos
    return cos

# Sine of angle from local x vector direction to other vector
def SineVectors(local_x_vec,other_vec):
    numsin = TwoDCrossProduct(local_x_vec, other_vec)
    denomsin = (VectorTwoNorm(local_x_vec))*(VectorTwoNorm(other_vec))
    sin = numsin/denomsin
    return sin

# Cosine of angle from local x bar to the other bar
def CosineBars(local_x_bar,other_bar):
    vec1, vec2 = BarsToVectors(local_x_bar, other_bar)
    return CosineVectors(vec1, vec2)

# Sine of angle from local x bar to the other bar
def SineBars(local_x_bar,other_bar):
    vec1, vec2 = BarsToVectors(local_x_bar, other_bar)
    return SineVectors(vec1, vec2)