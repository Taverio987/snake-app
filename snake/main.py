# -*- coding: utf-8 -*-
import kivy
from utils import setColor
# Config
from kivy.config import Config
Config.read("config/config.ini")


from kivy.core.window import Window
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle, Color, Ellipse
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from random import randint

SCREEN_W = Window.width
SCREEN_H = Window.height/2
PIX_W = int(Window.width/50)
PIX_H = PIX_W
PIX_SIZE = (PIX_W, PIX_H)
SNAKE_W = 2*PIX_W
SNAKE_H = 2*PIX_H
LX = SCREEN_W - SCREEN_W % PIX_W
LY = SCREEN_H - SCREEN_H % PIX_W
NX = (LX-SNAKE_W)  // SNAKE_W
NY = (LY-SNAKE_H) // SNAKE_H

COLOR_BOX = {"boundary": Color(1,1,0), # jaune
             "snake": Color(0,1,0)} # bleu

class SnakeApp(App):
    def build(self):
        self.game_lyt = BoxLayout()
        self.game_lyt.add_widget(SnakeGame())
        return self.game_lyt
    
class SnakeGame(BoxLayout):
    def __init__(self):
        super().__init__()
        self.orientation = "vertical"
        self.setStartParameters()   
        self.setupUi()
        self.connectUi()
        self.move_evt = Clock.schedule_interval(self.wind_snake.update, self.dt)
        self.updateScore()
        self.updateSpeed()
        
    def setStartParameters(self):
        self.on_pause = False
        self.dt = 0.8
        self.speed_lvl = 1
        self.score = 0
        
    def updateSpeed(self):
        self.wind_cmd.lab_speed_lvl.text = "speed : %d"%self.speed_lvl
    
    def updateScore(self):
        self.wind_cmd.lab_score.text = "score : %d"%self.score
        
    def setupUi(self):
        self.wind_snake = SnakeWind()
        self.layt_menu_cmd = BoxLayout(orientation="horizontal")
        self.add_widget(self.wind_snake)
        self.add_widget(self.layt_menu_cmd)
        
        self.wind_menu = MenuWind()
        self.wind_cmd = CommandWind()
        self.layt_menu_cmd.add_widget(self.wind_menu)
        self.layt_menu_cmd.add_widget(self.wind_cmd)
        self.wind_menu.speed_settings.btn_slower.disabled = True
    
    def connectUi(self):
        self.wind_cmd.btn_up.bind(on_press=self.goUp)
        self.wind_cmd.btn_down.bind(on_press=self.goDown)
        self.wind_cmd.btn_left.bind(on_press=self.goLeft)
        self.wind_cmd.btn_right.bind(on_press=self.goRight)
        self.wind_menu.btn_pause.bind(on_press=self.changeStatus)
        self.wind_menu.btn_quit.bind(on_press=self.exitApp)
        self.wind_menu.speed_settings.btn_faster.bind(on_press=self.getFaster)
        self.wind_menu.speed_settings.btn_slower.bind(on_press=self.getSlower)
    
    def getFaster(self, instance):
        self.speed_lvl += 1
        self.dt /= 1.5
        self.wind_menu.speed_settings.btn_slower.disabled = False
        if self.speed_lvl == 6:
            self.wind_menu.speed_settings.btn_faster.disabled = True
        self.move_evt.cancel()
        self.move_evt = Clock.schedule_interval(self.wind_snake.update, self.dt)
        self.updateSpeed()    
            
    def getSlower(self, instance):
        self.speed_lvl -= 1
        self.dt *= 1.5
        self.wind_menu.speed_settings.btn_faster.disabled = False
        if self.speed_lvl == 1:
            self.wind_menu.speed_settings.btn_slower.disabled = True
        self.move_evt.cancel()
        self.move_evt = Clock.schedule_interval(self.wind_snake.update, self.dt)
        self.updateSpeed()    
        
    def exitApp(self, instance):
        App.get_running_app().stop()
        Window.close()
    
    def changeStatus(self, instance):
        if self.on_pause == True:
            self.move_evt()
            self.on_pause = False
        else:
            self.move_evt.cancel()
            self.on_pause = True
    
    def goUp(self, instance):
        self.wind_snake.dx, self.wind_snake.dy = 0, SNAKE_H
        if self.score>0:
            self.wind_cmd.btn_down.disabled = True
            self.wind_cmd.btn_up.disabled = False
            self.wind_cmd.btn_right.disabled = False
            self.wind_cmd.btn_left.disabled = False
        
    def goDown(self, instance):
        self.wind_snake.dx, self.wind_snake.dy = 0, -1*SNAKE_H
        if self.score>0:
            self.wind_cmd.btn_up.disabled = True
            self.wind_cmd.btn_down.disabled = False
            self.wind_cmd.btn_right.disabled = False
            self.wind_cmd.btn_left.disabled = False
            
    def goLeft(self, instance):
        self.wind_snake.dx, self.wind_snake.dy = -1*SNAKE_W, 0
        if self.score>0:
            self.wind_cmd.btn_right.disabled = True
            self.wind_cmd.btn_down.disabled = False
            self.wind_cmd.btn_up.disabled = False
            self.wind_cmd.btn_left.disabled = False
        
    def goRight(self, instance):
        self.wind_snake.dx, self.wind_snake.dy = SNAKE_W, 0
        if self.score>0:
            self.wind_cmd.btn_left.disabled = True
            self.wind_cmd.btn_down.disabled = False
            self.wind_cmd.btn_up.disabled = False
            self.wind_cmd.btn_right.disabled = False
        
        
class SnakeWind(Screen):
    def __init__(self):
        super().__init__()
        self.setRefPoints()
        self.setBoudaries()
        self.snakeObj = SnakeObj()
        self.addSnake(self.p_c)
        self.addApple()
        self.direction = ""
        self.dx = 0
        self.dy = 0
        
    def setRefPoints(self):
        # set ref points
        self.p_sw = (PIX_W, PIX_H)
        self.p_nw = (PIX_W, LY-PIX_H-SNAKE_H)
        self.p_ne = (LX-PIX_W-SNAKE_W, LY-PIX_H-SNAKE_H)
        self.p_se = (LX-PIX_W-SNAKE_W, PIX_H)
        self.p_c = (PIX_W+int(NX/2)*SNAKE_W, PIX_H+int(NY/2)*SNAKE_H)
    
    def setBoudaries(self):
        with self.canvas:
            setColor("boundary")
            Rectangle(pos=(0,0), size=(PIX_W,LY))
            Rectangle(pos=(0,0), size=(LX,PIX_H))
            Rectangle(pos=(LX-PIX_W,0), size=(PIX_W,LY))
            Rectangle(pos=(0,LY-PIX_H), size=(LX,PIX_H))
    
    def addSnake(self, head_pos):
        with self.canvas:
            setColor("snake_head")
            snake_head = Rectangle(pos=head_pos, size=(SNAKE_W,SNAKE_H))    
        self.snakeObj.body.append(snake_head)
    
    def addPart(self):
        pos = self.snakeObj.last_positions[-1]
        with self.canvas:
            setColor("snake_body")
            snake_part = Rectangle(pos=pos, size=(SNAKE_W,SNAKE_H))
        self.snakeObj.body.append(snake_part)
    
    def addApple(self):
        """
        Placer la pomme sur une position autre que l'une
        des positions occupees par le snake
        """
        body = self.snakeObj.body
        x, y = body[0].pos[0], body[0].pos[1]
        move_apple = True
        while move_apple:
            move_apple = False
            x = self.p_sw[0]+randint(1,NX-1)*SNAKE_W
            y = self.p_sw[1]+randint(1,NY-1)*SNAKE_H
            for part in body:
                if (x,y) == part.pos :
                    move_apple = True
                    break
        with self.canvas:
            setColor("apple")
            self.apple = Ellipse(pos=(x, y), size=(SNAKE_W,SNAKE_H))    
    
    def getPositions(self):
        list_pos = []
        body = self.snakeObj.body
        for snake_part in body:
            list_pos.append(snake_part.pos)
        return list_pos
    
    def moveSnake(self, dt):
        body = self.snakeObj.body
        # save last positions
        self.snakeObj.last_positions = self.getPositions()
        # move snake head
        head = self.snakeObj.body[0]
        head.pos = (head.pos[0]+self.dx,
                    head.pos[1]+self.dy)
        # move snake body
        for i in range(1 ,len(body)):
            body[i].pos = self.snakeObj.last_positions[i-1]
    
    def isOnBoundary(self):
        is_on_boundary = False
        head = self.snakeObj.body[0]
        pos_x, pos_y = 0+head.pos[0], 0+head.pos[1]
        if  (pos_x < self.p_sw[0]) or (pos_x > self.p_se[0]):
            is_on_boundary = True
        elif (pos_y < self.p_sw[1]) or (pos_y > self.p_nw[1]):
            is_on_boundary = True
        return is_on_boundary
    
    def queueIsbitten(self):
        queue_is_bitten = False
        body = self.snakeObj.body
        head = body[0]
        for part in body[1:]:
            if head.pos == part.pos:
                queue_is_bitten = True
                break
        return queue_is_bitten
    
    def appleIsEaten(self):
        apple_is_eaten = False
        head = self.snakeObj.body[0]
        if head.pos == self.apple.pos:
            apple_is_eaten = True
        return apple_is_eaten
    
    def moveApple(self):
        """
        Bouger la pomme une fois mangee sur une position autre que l'une
        des positions occupees par le snake
        """
        body = self.snakeObj.body
        x, y = body[0].pos[0], body[0].pos[1]
        move_apple = True
        while move_apple:
            move_apple = False
            x = self.p_sw[0]+randint(1,NX-1)*SNAKE_W
            y = self.p_sw[1]+randint(1,NY-1)*SNAKE_H
            for part in body:
                if (x,y) == part.pos :
                    move_apple = True
                    break
        self.apple.pos = (x, y)
    
    def update(self, dt):
        game_over = False
        # Collision mgnt
        if self.isOnBoundary() or self.queueIsbitten():
            self.parent.move_evt.cancel()
            game_over = True
            self.my_popup = PopupWind(self.parent.score)
            self.my_popup.open()
        if not game_over:
            self.moveSnake(dt)
        if self.appleIsEaten():
            self.parent.score += 1
            self.parent.updateScore()
            self.addPart()
            self.moveApple()
        

class MenuWind(BoxLayout):
    def __init__(self):
        super().__init__()
        self.orientation = "vertical"
        self.setupUi()
        
    def setupUi(self):
        self.btn_pause = Button(text="pause")
        self.speed_settings = SpeedSettings()
        self.btn_quit = Button(text="quit")
        self.layt = BoxLayout(orientation="vertical")
        self.add_widget(self.speed_settings)
        self.add_widget(self.btn_pause)
        self.add_widget(self.btn_quit)
    
    

class CommandWind(GridLayout):
    def __init__(self):
        super().__init__()
        self.cols = 3
        self.setupUi()
        
    def setupUi(self):
        self.btn_up = Button(background_normal="config/icon/up.png")
        self.btn_down = Button(background_normal="config/icon/down.png")
        self.btn_left = Button(background_normal="config/icon/left.png")
        self.btn_right = Button(background_normal="config/icon/right.png")
        self.lab_speed_lvl = Label()
        self.add_widget(self.lab_speed_lvl)
        self.add_widget(self.btn_up)
        self.add_widget(Widget())
        self.add_widget(self.btn_left)
        self.lab_score = Label()
        self.add_widget(self.lab_score)
        self.add_widget(self.btn_right)
        self.add_widget(Widget())
        self.add_widget(self.btn_down)
        self.add_widget(Widget())

class SpeedSettings(BoxLayout):
    def __init__(self):
        super().__init__()
        self.orientation = "horizontal"
        self.btn_slower = Button(text="x0.5")
        self.btn_faster = Button(text="x2")
        self.add_widget(self.btn_slower)
        self.add_widget(self.btn_faster)

class PopupWind(Popup):
    def __init__(self, score):
        super().__init__()
        self.title = ""
        self.content = PopupContent(score)
        self.size_hint = (0.6, 0.5)
        self.connectUi()
        
    def connectUi(self):
        self.content.btn_retry.bind(on_press=self.retry)
        self.content.btn_quit.bind(on_press=self.exitApp)

    def retry(self, instance):
        app = App.get_running_app()
        app.game_lyt.clear_widgets()
        self.dismiss()
        app.game_lyt.add_widget(SnakeGame())
        
    def exitApp(self, instance):
        App.get_running_app().stop()
        Window.close()
        
class PopupContent(BoxLayout):
    def __init__(self, score):
        super().__init__()
        self.orientation = "vertical"
        self.msg = Label(text="Game over\nScore: %d"%score)
        self.lyt = BoxLayout(orientation="horizontal")
        self.btn_retry = Button(text="retry")
        self.btn_quit = Button(text="quit")
        self.lyt.add_widget(self.btn_retry)
        self.lyt.add_widget(self.btn_quit)
        self.add_widget(self.msg)
        self.add_widget(self.lyt)
    

        
    
class SnakeObj():
    def __init__(self):
        self.body = []
        self.last_positions = []


if __name__=="__main__":
    SnakeApp().run()
    
    
    