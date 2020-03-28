#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial 

This program creates a quit
button. When we press the button,
the application terminates. 

Author: Jan Bodnar
Website: zetcode.com 
Last edited: January 2018
"""

import sys, os
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QGridLayout, QListWidget, QMessageBox
from PyQt5.QtWidgets import QApplication, QScrollArea, QVBoxLayout, QGroupBox, QLabel, QPushButton, QFormLayout
from PyQt5.QtGui import QIcon, QPixmap
from pygame import mixer


class MyButtons():
    def __init__(self):
        QObject.__init__(self)

    
class MusicPlayer(QWidget):
    songsList = [] # class variable shared by all instances


    def __init__(self):
        super().__init__()
        mixer.init()
        self.initUI()

    def initSongList(self):
        os.chdir("/home/jakub/Music/No Doubt-Tragic Kingdom")
        filesList= os.listdir()
        for file in filesList:
            
            if file.lower().endswith(".mp3"):#case insensitive
                self.songsList.append(file)
                print(file) 
            

        #os.chdir("/home/jakub/Music/No Doubt-Tragic Kingdom")
    def listview_clicked(self):#set variable with picked song
        item = self.listWidget.currentItem()
        print(item.text())
        #self.play(item.text())
        self.pickedSong = item.text()

    def initUI(self):               
        self.pickedSong = ""
        self.status = "Stopped" #activity in player ->played|paused|unpaused|stopped
        qbtn = QPushButton('Quit', self)
        qbtn.clicked.connect(QApplication.instance().quit)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 50)  

        btnPlay = QPushButton(self)
        btnPlay.setIcon(QIcon(QPixmap("play.png")))
        btnPlay.move(160, 50) 
        btnPlay.clicked.connect(self.play)

        btnPause = QPushButton(self)
        btnPause.setIcon(QIcon(QPixmap("pause.png")))
        btnPause.move(200, 50) 
        btnPause.clicked.connect(self.pause)

        self.initSongList()
        layout = QGridLayout()

        

        self.listWidget = QListWidget(self)
        for song in self.songsList:#fill list with songs
            self.listWidget.addItem(song)
        #Resize width and height
        self.listWidget.resize(300,220)
        self.listWidget.move(50, 80)
        

        self.listWidget.setWindowTitle('PyQT QListwidget Demo')
        #listWidget.itemClicked.connect(listWidget.Clicked)
        self.listWidget.clicked.connect(self.listview_clicked)

        #listWidget.show()

        self.setGeometry(100, 100, 750, 400)
        self.setWindowTitle('Gnome Music Player Clone')    
        self.show()

    def play(self, name):
        if self.status == "Stopped":
            self.status = "Played"
            mixer.music.load("/home/jakub/Music/No Doubt-Tragic Kingdom/"+self.pickedSong)#"10 - No Doubt - DON'T SPEAK.MP3"
            mixer.music.play()
            return
        elif self.status == "Paused":
            self.status = "Played"
            mixer.music.unpause()

    def pause(self):
        if self.status == "Played":
            self.status = "Paused"
            mixer.music.pause()
        return



        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = MusicPlayer()
    sys.exit(app.exec_())