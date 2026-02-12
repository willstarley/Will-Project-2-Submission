#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 14:34:19 2021

@author: kendrick shepherd
"""

import sys

# determine if the bar is statically determinate (and belongs to a truss)
def StaticallyDeterminate(nodes,bars):                 
    # Determine the number of nodes in the truss
    n_nodes = len(nodes)
    n_bars = len(bars)
    
    # Determine number of (valid) reactions supported by nodes of the truss
    n_reactions = 0
    for node in nodes:
        if(any(node.ConstraintType())):
            if(2 in node.ConstraintType()):
                sys.exit("Truss cannot support a moment reaction force")
            elif(-1 in node.ConstraintType()):
                sys.exit("Invalid constraint type specified for the truss")
            else:
                n_reactions += len(node.ConstraintType())
    
    # Compute if b + r = 2j (Equation 3-1 of the textbook)
    if(n_bars + n_reactions < 2*n_nodes):
        sys.exit("The truss is unstable; did you input all of the reaction constraints correctly?")
    elif(n_bars + n_reactions > 2*n_nodes):
        sys.exit("The truss is statically indeterminate, and cannot be resolved using method of joints")
    else:
        return True
 
def ComputeReactions(nodes):
    # assume that there is one pin and one roller for our statically determinate structure
    n_pins = 0
    n_roller = 0
    for node in nodes:
        if(node.constraint=="pin"):
            pin_node = node
            n_pins += 1
        elif(node.constraint=="roller_no_xdisp"):
            roller_node = node
            n_roller += 1
        elif(node.constraint=="roller_no_ydisp"):
            roller_node = node
            n_roller += 1
    
    if(n_pins != 1 or n_roller != 1):
        sys.exit("A more clever way must be found to compute the reaction forces")
    
    # Continue from here
    # Sum of moments about the pin
    [pin_x, pin_y] = pin_node.location # Gets x and y coordinates of pin
    [roller_x, roller_y] = roller_node.location # Gets x and y coordinates of roller
    
    roller_reaction = 0
    for node in nodes:
        [node_x, node_y] = node.location
        # contributions in the y direction
        roller_reaction += node.yforce_external * (node_x - pin_x)
        # contributions in the x direction
        roller_reaction += node.xforce_external * (pin_y - node_y)
        
    if(roller_node.constraint == "roller_no_xdisp"):
        roller_reaction = -roller_reaction / (pin_y - roller_y)
        roller_node.AddReactionXForce(roller_reaction)
    elif(roller_node.constraint == "roller_no_ydisp"):
        roller_reaction = -roller_reaction / (roller_x - pin_x)
        roller_node.AddReactionYForce(roller_reaction)
        
    # sum of forces in y direction
    sum_force_y = 0
    for node in nodes:
        sum_force_y += node.yforce_external
        
    # sum of forces in x direction
    sum_force_x = 0
    for node in nodes:
        sum_force_x -= node.xforce_external
        
    if(roller_node.constraint=="roller_no_xdisp"):
        sum_force_x += roller_reaction
        
    elif(roller_node.constraint=="roller_no_ydisp"):
        sum_force_y += roller_reaction
        
    pin_node.AddReactionYForce(-sum_force_y)
    pin_node.AddReactionXForce(-sum_force_x)
    
