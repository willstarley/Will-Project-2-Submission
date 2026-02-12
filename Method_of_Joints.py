#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 12:37:32 2021

@author: kendrick shepherd
"""

import sys

import Geometry_Operations as geom

# Determine the unknown bars next to this node
def UnknownBars(node):
    list_of_unknown_bars = []
    for bar in node.bars:
        if bar.is_computed == False:
            list_of_unknown_bars.append(bar)
            
    return list_of_unknown_bars

# Determine if a node if "viable" or not
def NodeIsViable(node):
    if len(UnknownBars(node)) in (1,2):
        return True
    else:
        return False
    
# Compute unknown force in bar due to sum of the
# forces in the x direction
def SumOfForcesInLocalX(node, unknown_bars):

    # First unknown bar defines local x-axis
    local_x_bar = unknown_bars[0]

    # Get the other node of this bar
    if local_x_bar.init_node == node:
        other_node = local_x_bar.end_node
    else:
        other_node = local_x_bar.init_node

    # Local x direction vector (unit vector)
    dx = other_node.location[0] - node.location[0]
    dy = other_node.location[1] - node.location[1]
    L = (dx**2 + dy**2)**0.5
    ex = dx / L
    ey = dy / L

    # Start with external + reaction forces at node
    sum_local_x = node.GetNetXForce()*ex + node.GetNetYForce()*ey

    # Add contribution of already-known bars
    for bar in node.bars:
        if bar.is_computed == True:

            if bar.init_node == node:
                other = bar.end_node
            else:
                other = bar.init_node

            dx_b = other.location[0] - node.location[0]
            dy_b = other.location[1] - node.location[1]
            Lb = (dx_b**2 + dy_b**2)**0.5
            ex_b = dx_b / Lb
            ey_b = dy_b / Lb

            # Projection into THIS local-x direction
            contribution = bar.axial_load * (ex_b*ex + ey_b*ey)
            sum_local_x += contribution

    # Solve unknown force (negative equilibrium)
    local_x_bar.axial_load = -sum_local_x
    local_x_bar.is_computed = True


# Compute unknown force in bar due to sum of the 
# forces in the y direction
def SumOfForcesInLocalY(node, unknown_bars):

    # Two unknown bars
    bar_x = unknown_bars[0]   # defines local x
    bar_y = unknown_bars[1]   # the one we solve

    # --- direction of local x bar ---
    if bar_x.init_node == node:
        other_x = bar_x.end_node
    else:
        other_x = bar_x.init_node

    dx = other_x.location[0] - node.location[0]
    dy = other_x.location[1] - node.location[1]
    L = (dx**2 + dy**2)**0.5
    ex = dx / L
    ey = dy / L

    # --- direction of second bar ---
    if bar_y.init_node == node:
        other_y = bar_y.end_node
    else:
        other_y = bar_y.init_node

    dx2 = other_y.location[0] - node.location[0]
    dy2 = other_y.location[1] - node.location[1]
    L2 = (dx2**2 + dy2**2)**0.5
    ex2 = dx2 / L2
    ey2 = dy2 / L2

    # sine of CCW angle using 2D cross product
    sin_theta = ex*ey2 - ey*ex2

    # Start equilibrium sum
    sum_local_y = node.GetNetXForce()*(-ey) + node.GetNetYForce()*(ex)

    # Contributions of known bars
    for bar in node.bars:
        if bar.is_computed == True:

            if bar.init_node == node:
                other = bar.end_node
            else:
                other = bar.init_node

            dx_b = other.location[0] - node.location[0]
            dy_b = other.location[1] - node.location[1]
            Lb = (dx_b**2 + dy_b**2)**0.5
            ex_b = dx_b / Lb
            ey_b = dy_b / Lb

            contribution = bar.axial_load * (ex_b*(-ey) + ey_b*(ex))
            sum_local_y += contribution

    # Solve second unknown
    bar_y.axial_load = -sum_local_y / sin_theta
    bar_y.is_computed = True

    
def IsThereAnUnknownMember(nodes):
    for node in nodes:
        unknown_bars = UnknownBars(node)
        if len(unknown_bars) > 0:
            return True
    return False

# Perform the method of joints on the structure
def IterateUsingMethodOfJoints(nodes,bars):
    counter = 0
    while IsThereAnUnknownMember(nodes) == True:
        
        # Loop through each node and check if it is viable
        for node in nodes:

            # Determine the unknown bars at this node
            unknown_bars = UnknownBars(node)

            # Determine if the node is viable
            if NodeIsViable(node) == True:

                # If there are two unknown bars, solve using local y first
                if len(unknown_bars) == 2:
                    SumOfForcesInLocalY(node, unknown_bars)

                # Recompute unknown bars (one may now be solved)
                unknown_bars = UnknownBars(node)

                # Perform sum of forces in local x direction
                if len(unknown_bars) >= 1:
                    SumOfForcesInLocalX(node, unknown_bars)
        
        counter += 1
        if counter > len(nodes)+1:
            print("Too many iterations")
            return
    return
