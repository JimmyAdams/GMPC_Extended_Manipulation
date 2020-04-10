#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: Jakub Adamec
"""

import sys, os
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget, QMessageBox, QPushButton, QApplication, QGridLayout, QListWidget, QMessageBox
from PyQt5.QtWidgets import QApplication,QVBoxLayout, QHBoxLayout, QGroupBox, QScrollArea, QVBoxLayout, QGroupBox, QLabel, QPushButton, QFormLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem
from pygame import mixer
from itertools import cycle
from collections import deque
from mutagen.id3 import *
import mutagen
from mutagen.mp3 import MP3
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import musicbrainzngs
import copy

# all songs will be in one default playlist

class Playlist():
    def __init__(self):
        self.name = "" #unique to each instance
        self.songs = [] #songs with path or list of songs

    def setNameToPlaylist(self, name):
        self.name = name

    def addSongToPlaylist(self, songName):
        self.songs.append(songName)

    def removeSongFromPlaylist(self, songName):
        self.songs.remove(songName)

    def getAllSongs(self):
        return self.songs #maybe next func to return for QComboBox

    def printAllsongs(self):
        for i in range(len(self.songs)):
            print(self.songs[i])

    def getNameOfPlaylist(self):
        return self.name



class Dialog(QDialog):#nemusi byt ako samotna trieda asi
    nameOfPlaylist = ""

    def __init__(self,allplaylists):
        super(Dialog, self).__init__()
        self.createFormGroupBox(allplaylists)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)# | QDialogButtonBox.Cancel
        buttonBox.accepted.connect(self.accept)
        #buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Playlist selector")
        self.boxCombo.activated[str].connect(self.pLaylistOnClick)
        #self.show()

    def createFormGroupBox(self, allplaylists):
        self.boxCombo = QComboBox()
        self.boxCombo.clear()
        #array = allplaylists.returnListPlaylist()
        #print(len(playlists))
        for item in range(len(allplaylists)):
            self.boxCombo.addItem(allplaylists[item].getNameOfPlaylist())
            #print(playlists[item].getNameOfPlaylist())
        self.formGroupBox = QGroupBox("Click playlist")
        layout = QFormLayout()
        layout.addRow(QLabel("Playlist:"), self.boxCombo)
        self.formGroupBox.setLayout(layout)

    def pLaylistOnClick(self, text):
        self.nameOfPlaylist = text # return name of picked playlist

    def returnPickedPlaylist(self):
        return self.nameOfPlaylist

class MusicPlayer(QWidget):
    #TODO: function for loading files
    songsList = [] # class variable shared by all instances
    dataSongs = [] #ID3 for songs
    allPlaylists = []
    playLists = [] # users created class of playlists


    def __init__(self):
        super().__init__()
        mixer.init()
        self.initUI()

    def initSongList(self):
        #file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        #print(file)
        os.chdir("/home/jakub/Music/The Cure - 1979 Boys Don't Cry")
        filesList= os.listdir()
        for file in filesList:

            if file.lower().endswith(".mp3"):#case insensitive
                self.songsList.append(file)
                realdir = os.path.realpath(file)
                tempAudio = ID3(realdir)
                #TODO if exist
                self.dataSongs.append(tempAudio['TIT2'].text[0])
                self.autor = tempAudio['TPE1'].text[0]
                #print(audio['TIT2'].text[0])


        #os.chdir("/home/jakub/Music/No Doubt-Tragic Kingdom")
    def listview_clicked(self):#set variable with picked song
        item = self.listWidget.currentItem()
        #print(item.text())
        self.pickedSong = item.text()
        self.status = "Stopped"
        self.fillBoxSongInfo()
        self.initTable()

    def initUI(self):
        self.pickedSong = ""
        self.status = "Stopped" #activity in player ->played|paused|unpaused|stopped
        self.currentPlaylist = Playlist()

        onePlaylist = Playlist()
        onePlaylist.setNameToPlaylist("Prvy playlist")
        onePlaylist.addSongToPlaylist("Pesnicka 1")
        onePlaylist.addSongToPlaylist("Necho boze da")
        onePlaylist.addSongToPlaylist("Siel siel")
        twoPlaylist = Playlist()
        twoPlaylist.setNameToPlaylist("Druhy Playlist")
        twoPlaylist.addSongToPlaylist("Pesnicka AA")
        twoPlaylist.addSongToPlaylist("Pesnicka AB")
        twoPlaylist.addSongToPlaylist("Pesnicka CC")
        threePlaylist = Playlist()
        threePlaylist.setNameToPlaylist("Treti Playlist")
        threePlaylist.addSongToPlaylist("Pesnicka 1233")
        self.addToPlaylists(onePlaylist)
        self.addToPlaylists(twoPlaylist)
        self.addToPlaylists(threePlaylist)



        btnPlay = QPushButton(self)
        btnPlay.setIcon(QIcon(QPixmap("play.png")))
        btnPlay.move(20, 20)
        btnPlay.clicked.connect(self.play)

        btnPause = QPushButton(self)
        btnPause.setIcon(QIcon(QPixmap("pause.png")))
        btnPause.move(60, 20)
        btnPause.clicked.connect(self.pause)

        btnStop = QPushButton(self)
        btnStop.setIcon(QIcon(QPixmap("stop.png")))
        btnStop.move(100, 20)
        btnStop.clicked.connect(self.stop)

        btnPrev = QPushButton(self)
        btnPrev.setIcon(QIcon(QPixmap("previous.png")))
        btnPrev.move(140, 20)
        btnPrev.clicked.connect(self.previous)
        #btnPrev

        btnNext = QPushButton(self)
        btnNext.setIcon(QIcon(QPixmap("next.png")))
        btnNext.move(180, 20)
        btnNext.clicked.connect(self.next)

        btnSelectPlaylist = QPushButton('Select Playlist',self)
        btnSelectPlaylist.move(280, 20)
        btnSelectPlaylist.clicked.connect(self.selectPlaylists)
        #self.infobox()



        btnToPlaylist = QPushButton('Add to Playlist',self)
        btnToPlaylist.move(390, 20)
        btnToPlaylist.clicked.connect(self.addSongToPlaylistAction)

        btnCreatePlaylist = QPushButton('Create Playlist',self)
        btnCreatePlaylist.move(505, 20)
        btnCreatePlaylist.clicked.connect(self.createPlaylistAction)

        btnDeletePlaylist = QPushButton('Delete Playlist',self)
        btnDeletePlaylist.move(620, 20)
        btnDeletePlaylist.clicked.connect(self.deletePlaylistAction)

        btnMergePlaylist = QPushButton('Merge playlist',self)
        btnMergePlaylist.move(620, 50)

        self.labelPlaylist = QLabel(self)
        self.labelPlaylist.move(420, 210)
        self.labelPlaylist.resize(200,20)
        self.labelPlaylist.setStyleSheet("background-color: white; border: 1px inset grey;")
        self.labelPlaylist.setText("")
        #self.labelPlaylist

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
        self.listWidget.resize(300,370)
        self.listWidget.move(50, 230)


        self.listWidget.setWindowTitle('PyQT QListwidget Demo')
        #listWidget.itemClicked.connect(listWidget.Clicked)
        self.listWidget.clicked.connect(self.listview_clicked)

        self.playlistWidget = QListWidget(self)
        self.playlistWidget.resize(300,370)
        self.playlistWidget.move(420, 230)
        #self.playlistWidget

        #Song Info Box
        self.groupbox = QGroupBox("Song Info",self)
        self.groupbox.move(50, 60)
        self.groupbox.resize(500, 150)
        hbox = QHBoxLayout()
        v2box = QVBoxLayout()
        vbox = QVBoxLayout()
        self.infoLabels = []
        #infoLabels[1] = QLabel()
        for i in range(0,4):
            self.infoLabels.append(QLabel(""))
            vbox.addWidget(self.infoLabels[i])

        #self.groupbox.setLayout(vbox)
        #groupbox.setFont(QtGui.QFont("Sanserif", 15))

        label = QLabel(self)
        pixmap = QPixmap('cover.jpg')

        label.setPixmap(pixmap)
        label.setFixedSize(150,110)

        v2box.addWidget(label)
        v2box.setAlignment(Qt.AlignTop)

        hbox.addLayout(v2box)
        hbox.addLayout(vbox)
        self.groupbox.setLayout(hbox)

        #vbox.addWidget(label)

        #self.setGeometry(100, 100, 750, 400)
        self.setFixedSize(800, 640)
        self.setWindowTitle('Gnome Music Player Clone')



        self.show()

    def addSongToPlaylistAction(self):
        if(self.pickedSong):
            for x in range(len(self.allPlaylists)):
                if(self.allPlaylists[x].getNameOfPlaylist() == self.currentPlaylist.getNameOfPlaylist()):#current playlist
                    self.allPlaylists[x].addSongToPlaylist(self.pickedSong)
                    self.refreshPlaylistWidget()

    def addToPlaylists(self, playlist):
        self.allPlaylists.append(playlist)

    def createPlaylistAction(self):
        text, ok = QInputDialog.getText(self, 'Playlist Creator', 'Enter playlist name:')
        tempPlay = Playlist()
        tempPlay.setNameToPlaylist(str(text))
        #tempPlay.addSongToPlaylist("zzzz")

        self.allPlaylists.append(tempPlay)

        self.refreshPlaylistWidget() #refresh values in dropmenu

        if ok:
         print(str(text))

    def deletePlaylistAction(self):
        text, ok = QInputDialog.getText(self, 'Playlist For Deleting', 'Enter playlist to delete:')
        nameOfDeletedPlaylist = str(text)
        tempPlay = Playlist()

        for x in range(len(self.allPlaylists)-1):
            if(self.allPlaylists[x].getNameOfPlaylist() == nameOfDeletedPlaylist):#current playlist
                #self.allPlaylists[x].addSongToPlaylist(self.pickedSong)
                print(nameOfDeletedPlaylist)
                #Sprint(x)
                del self.allPlaylists[x]


        self.refreshPlaylistWidget()


    def fillBoxSongInfo(self):
        name = self.pickedSong
        #print(("/home/jakub/Music/No Doubt-Tragic Kingdom/"+self.pickedSong))
        song = ("/home/jakub/Music/The Cure - 1979 Boys Don't Cry/"+self.pickedSong)
        audio = ID3(song)
        mp3s = MP3(song)
        #print(audio.pprint())
        #TODO: coditions for existence
        self.infoLabels[0].setText("Name: " + audio["TIT2"].text[0])
        self.infoLabels[1].setText("Artist: " + audio["TPE1"].text[0])
        self.infoLabels[2].setText("Length: " + self.secondsLength(mp3s.info.length))
        self.infoLabels[3].setText("Format: " + str(mp3s.info.channels) + " channels, " + str(mp3s.info.sample_rate/1000) + "Hz, " + str(int(mp3s.info.bitrate/1000)) + "kbps")

        # check if has picture
        has_pic = False

        for k, v in audio.items():
            if "APIC" in k:
                has_pic = True
                break

        if(has_pic):
            pict = audio.get("APIC:").data
            #print(pict)


        return

    def refreshPlaylistWidget(self):
        #make label
        self.labelPlaylist.setText(self.currentPlaylist.getNameOfPlaylist())
        # update songs in list widget
        self.playlistWidget.clear()
        for song in self.currentPlaylist.getAllSongs():#fill list with songs
            self.playlistWidget.addItem(song)

    def selectPlaylists(self):


        #self.allPlaylists.printAllPlaylists()
        self.dialog = Dialog(self.allPlaylists) # popup window to select playlist
        self.dialog.exec_()

        #print(self.dialog.returnPickedPlaylist())
        nameOfPickedPlaylist = self.dialog.returnPickedPlaylist()
        for idx in range(len(self.allPlaylists)):
            if self.allPlaylists[idx].getNameOfPlaylist() == nameOfPickedPlaylist:
                print(self.allPlaylists[idx].getNameOfPlaylist())
                self.currentPlaylist = copy.copy(self.allPlaylists[idx])
                self.currentPlaylist.printAllsongs()

                self.refreshPlaylistWidget()

        return


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
            mixer.music.load("/home/jakub/Music/The Cure - 1979 Boys Don't Cry/"+self.pickedSong)#"10 - No Doubt - DON'T SPEAK.MP3"
            mixer.music.play()
            return

    def pause(self):
        if self.status == "Played":
            self.status = "Paused"
            mixer.music.pause()
            return
        if self.status == "Stopped":
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

    def secondsLength(self, insec):
        if insec == 0:
            return "X"
        min = int(insec / 60)
        sec = int(insec % 60)
        word = str(min) + "min:" + str(sec) + "sec"
        return word


    def initTable(self):
        if self.pickedSong:#if ssong is choosen, find autohor and song title for searching in database
            song = ("/home/jakub/Music/The Cure - 1979 Boys Don't Cry/"+self.pickedSong)
            tempAudio = ID3(song)
            songTitle = tempAudio['TIT2'].text[0]
            autor = tempAudio['TPE1'].text[0]
            print("Table")
            print(autor)
            print(songTitle)
            print("Tableend")

            #result = musicbrainzngs.search_releases(artist=autor, tracks=songTitle,limit=1)
            #print(result['release-list'])
        # set row count
        #self.tableWidget.setRowCount(12)
        # set column count
        #self.tableWidget.setColumnCount(2)

        #for idx,name in enumerate(self.dataSongs):
        #s    self.tableWidget.setItem(idx,0, QTableWidgetItem(name))

def printString(rel):
    for key in rel:
        #print(type(rel[key]))
        if isinstance(rel[key], str):
            print(key + " : " + rel[key])
            #array1.append(key)
            #array2.append(rel[key])
        elif isinstance(rel[key], dict):
            printString(rel[key])
        #elif isinstance(rel[key], list):


if __name__ == '__main__':
    musicbrainzngs.set_useragent(
    "python-musicbrainzngs-example",
    "0.1",
    "https://github.com/alastair/python-musicbrainzngs/",
)
    artist = "U2"
    album = "One"

    #result = musicbrainzngs.search_releases(artist=artist, tracks=album,limit=1)
    #print(result['release-list'])



    app = QApplication(sys.argv)
    ex = MusicPlayer()
    sys.exit(app.exec_())
