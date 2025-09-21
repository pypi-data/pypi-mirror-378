"""


galapagos.py

supercharged Tracy

"""
import turtle
from turtle import *

"""
CONFIG
"""
base_speed = 0
"""
END CONFIG
"""

speed(base_speed)

# boolean support
true = "true"
false = "false"
"""
FUNCTIONS
"""
def setpen(mode):
    if mode == "down":
        pendown()
    
    if mode == "up":
        penup()

def rect(x, y, clr="black"):
    pendown()
    color(clr)
    for i in range(2):
        forward(x)
        left(90)
        forward(y)
        left(90)
    
def better_circle(rad, deg=360, points=0, fill=false):
    if fill==true:
        begin_fill()
    circle(rad,deg,points)
    if fill ==true:
        end_fill()

def shape(name, rad, deg=360, fill=false):
    shape_points = {
        "triangle":3,
        "square":4,
        "pentagon":5,
        "hexagon":6,
        "heptagon":7,
        "octagon":8,
        "nonagon":9,
        "decagon":10
    }
    
    if fill == true:
        begin_fill()
        
    if shape == "circle":
        circle(rad, deg)
    else:
        circle(rad, deg, shape_points[name])
        
    if fill == true:
        end_fill()
    

def teleport(x, y):
    speed(0)
    penup()
    setposition(x,y)
    speed(base_speed)

def lunge(px):
    speed(0)
    penup()
    forward(px)
    speed(base_speed)

def grid(spacing):
    for i in range(4):
        teleport(-200+i*spacing,200)
        pendown()
        setheading(270)
        forward(400)

def base_move(direction, amount):
    setheading(direction)
    forward(amount)

def dashed_line(spacing, dash_length):
    for b in range (400/(spacing+dash_length)):
        pendown()
        forward(dash_length)
        penup()
        forward(spacing)

"""


END GALAPAGOS


"""