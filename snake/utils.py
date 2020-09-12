# -*- coding: utf-8 -*-

from kivy.graphics import Color
COLOR_BOX = {"boundary": (1,1,0), # jaune
             "snake_body": (0,1,0), # vert clair
             "snake_head": (0,0.5,0), # vert foncé
             "apple": (1,0,0)} # rouge

def setColor(obj):
    return Color(COLOR_BOX[obj][0],
                 COLOR_BOX[obj][1],
                 COLOR_BOX[obj][2])
    