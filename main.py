#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: Jakub Adamec
"""

import sys, os
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QGridLayout, QListWidget, QMessageBox
from PyQt5.QtWidgets import QApplication, QScrollArea, QVBoxLayout, QGroupBox, QLabel, QPushButton, QFormLayout
from PyQt5.QtGui import QIcon, QPixmap
from pygame import mixer
from itertools import cycle
from collections import deque


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


        #os.chdir("/home/jakub/Music/No Doubt-Tragic Kingdom")
    def listview_clicked(self):#set variable with picked song
        item = self.listWidget.currentItem()
        print(item.text())
        #self.play(item.text())
        #self.status == "Stopped"
        self.pickedSong = item.text()
        self.status = "Stopped"

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

        btnPrev = QPushButton(self)
        btnPrev.setIcon(QIcon(QPixmap("previous.png")))
        btnPrev.move(240, 50)
        btnPrev.clicked.connect(self.previous)
        #btnPrev

        btnNext = QPushButton(self)
        btnNext.setIcon(QIcon(QPixmap("next.png")))
        btnNext.move(280, 50)
        btnNext.clicked.connect(self.next)

        btnStop = QPushButton(self)
        btnStop.setIcon(QIcon(QPixmap("stop.png")))
        btnStop.move(320, 50)
        btnStop.clicked.connect(self.stop)

        self.initSongList()
        print("-------------------------")
        self.songsList.sort()
        #iterSongList = iter(self.songsList)
        iterSongList = cycle(self.songsList)
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

    def play(self):
        print("Status in play is " + self.status)
        if self.status == "Paused": #continues playing
            self.status = "Played"
            mixer.music.unpause()
            return
        else: # play song from beginning
            #self.stop()
            self.status = "Played"
            print("Mixer loads "+ self.pickedSong)
            mixer.music.load("/home/jakub/Music/No Doubt-Tragic Kingdom/"+self.pickedSong)#"10 - No Doubt - DON'T SPEAK.MP3"
            mixer.music.play()
            return


    def pause(self):
        if self.status == "Played":
            self.status = "Paused"
            mixer.music.pause()
        return

    def stop(self):
        mixer.music.stop()
        self.status = "Stopped"; #TODO: make enum for this
        return

    def next(self):
        mixer.music.stop()

        index = self.songsList.index(self.pickedSong)#index of actual song
        #print("Index is "+ str(index))
        deq = deque(self.songsList)
        deq.rotate(-1)#shift to left
        self.pickedSong = deq[index]
        #print("Wanna "+ deq[index])
        self.status = "Played"
        self.play()
        return

    def previous(self):
        mixer.music.stop()
        index = self.songsList.index(self.pickedSong)#index of actual song
        deq = deque(self.songsList)
        deq.rotate(1)#shift to left
        self.pickedSong = deq[index]
        self.status = "Played"
        self.play()
        return



if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MusicPlayer()
    sys.exit(app.exec_())
