#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: Jakub Adamec
"""

import sys, os
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget, QMessageBox, QPushButton, QApplication, QGridLayout, QListWidget, QMessageBox
from PyQt5.QtWidgets import QApplication,QVBoxLayout, QHBoxLayout, QGroupBox, QScrollArea, QVBoxLayout, QGroupBox, QLabel, QPushButton, QFormLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem
from pygame import mixer
from itertools import cycle
from collections import deque #iterate reversely
from mutagen.id3 import *
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.mp3 import MP3 #metadata manipulation
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import musicbrainzngs #metadata from public database
import copy #copy instance of object
import gzip, pickle
import atexit
import threading
import time
import audio_metadata
from tinytag import TinyTag
import zipfile
import wave

#my own modules
import data
import beatalg


# will be added to lists and playlists



"""
    A class used to represent one Playlist

    ...

    Attributes
    ----------
    name : str
        the name of the playlist
    songs : list
        the list of names of playlists
"""

class Playlist():
    #allPlaylists = []
    def __init__(self):
        self.name = "" #unique to each instance
        self.songs = [] #songs with path or list of songs

    def setNameToPlaylist(self, name):
        """ Sets new name of playlist object

            Parameters
            ----------
            name : str
                Name of playlist
        """
        self.name = name

    def addSongToPlaylist(self, songName):
        """
            Add name of playlist to list

            Parameters
            ----------
            songName : str
                name of song

            Returns
            ------
            list : playlist with names

        """
        self.songs.append(songName)

    def setMergedList(self, list1, list2):
        """ Sets similar items together

            Parameters
            ----------
            list1: list
                First list to merge
            list2: list
                Second list to merge
            Returns
            -------
            list : result of merge operation
        """
        self.songs = list(set(list1 + list2))

    def setIntersectedList(self, list1, list2):
        """ Sets all items together

            Parameters
            ----------
            list1: list
                First list of songs
            list2: list
                Second list to songs
            Returns
            -------
            list : result of intersection
        """
        self.songs = [value for value in list1 if value in list2]

    def setSymDiffList(self, list1, list2):
        """ Sets difference of items

            Parameters
            ----------
            list1: list
                First list of songs
            list2: list
                Second list of songs
            Returns
            -------
            list : result of difference
        """
        self.songs = [value for value in list1 + list2 if value not in list1 or value not in list2]

    def removeSongFromPlaylist(self, songName):
        """ Removes song from playlist

            Parameters
            ----------
            songName : str
                Name of song to delete
        """
        self.songs.remove(songName)

    def clearAllPlaylist(self):
        """ Removes all songs from playlist

        """
        self.songs.clear()

    def getAllSongs(self):
        """ Just gets all songs

            Returns
            -------
            list : list of songs
        """
        return self.songs #maybe next func to return for QComboBox

    def printAllsongs(self):#debugging
        for i in range(len(self.songs)):
            print(self.songs[i])

    def getNameOfPlaylist(self):
        """ Getter for playlist name

            Returns
            -------
            str : name
        """
        return self.name


"""
    A class for media player, that contains every aspect
    of functionality in project, uses

    ...

    Attributes
    ----------
    songsList : list
        list of songs in main playlist from system
    allPlaylists : list
        the list of names of playlists
    playLists : list
        list of songs in playlist for operations and export
"""

class MusicPlayer(QWidget):
    songsList = [] # class variable shared by all instances
    allPlaylists = []
    playLists = [] # users created class of playlists


    def __init__(self):
        super().__init__()
        mixer.init()



        self.initUI()

    def initSongList(self):
        """ Function for initialization of songsList
            user has to pick directory from system
            path to file is parsed (realpath)
            MP3 and WAV formats get accepted

        """
        #self.filesList = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        #print(self.filesList)
        self.filesList = "/home/jakub/Music/The Cure - 1979 Boys Don't Cry"
        os.chdir(self.filesList)
        filesLists= os.listdir()
        self.realpath = filesLists
        for file in filesLists:
            if (file.lower().endswith(".mp3")):#case insensitive
                self.songsList.append(file)
            elif(file.lower().endswith(".wav")):
                self.songsList.append(file)

    def listview_clicked(self):#set variable with picked song
        """
            Runs when action click pressed in playlist widget (listwidget)

        """
        item = self.listWidget.currentItem()
        self.pickedSong = item.text()
        self.status = "Stopped"
        self.fillBoxSongInfo()
        self.fillBoxSongPic()
        #self.initTable()

    def playlistview_clicked(self):
        """
            Iterate in playlist when action click pressed
        """
        itemPlaylist2 = self.playlistWidget.currentItem()
        self.playlist2CurrentSong = itemPlaylist2.text()

    def initUI(self):
        """ Main part, contains PyQt5 implementation

        """

        self.pickedSong = "" # currently playing song
        self.playlist2CurrentSong = "" #picked song in second playlist
        self.status = "Stopped" #activity in player ->played|paused|unpaused|stopped
        self.currentPlaylist = Playlist() # init current playlist

        #initialization of permanent object from file
        try:
            with open('playlists', 'rb') as self.f:
                database = pickle.load(self.f)
                self.allPlaylists = copy.copy(database)
                self.f.close()

        except (IOError, EOFError):
            database = []
            print("eeee")
            pass

        atexit.register(self.loadPermanentData)

        try:
            self.file = open('playlists', 'wb')
        except:
            pass


        #database[0].printAllsongs()

        #button to play music
        btnPlay = QPushButton(self)
        btnPlay.setIcon(QIcon(QPixmap("icons/iconPlay.svg")))
        btnPlay.move(20, 20)
        btnPlay.clicked.connect(self.play)

        #button to pause music
        btnPause = QPushButton(self)
        btnPause.setIcon(QIcon(QPixmap("icons/iconPause.svg")))
        btnPause.move(60, 20)
        btnPause.clicked.connect(self.pause)

        #button to stop music
        btnStop = QPushButton(self)
        btnStop.setIcon(QIcon(QPixmap("icons/iconStop.svg")))
        btnStop.move(100, 20)
        btnStop.clicked.connect(self.stop)

        #button for previous song
        btnPrev = QPushButton(self)
        btnPrev.setIcon(QIcon(QPixmap("icons/iconPrev.svg")))
        btnPrev.move(140, 20)
        btnPrev.clicked.connect(self.previous)

        #button for next Song
        btnNext = QPushButton(self)
        btnNext.setIcon(QIcon(QPixmap("icons/iconNext.svg")))
        btnNext.move(180, 20)
        btnNext.clicked.connect(self.next)

        # button for Select playlist to show in playlist box
        btnSelectPlaylist = QPushButton('Select Playlist',self)
        btnSelectPlaylist.move(280, 20)
        btnSelectPlaylist.clicked.connect(self.selectPlaylistAction)

        # button for Adding song to playlist
        btnToPlaylist = QPushButton('Add to Playlist',self)
        btnToPlaylist.move(390, 20)
        btnToPlaylist.clicked.connect(self.addSongToPlaylistAction)

        # button for erase song from playlist
        btnEraseFromPlaylist = QPushButton('Erase from Playlist',self)
        btnEraseFromPlaylist.move(620, 50)
        btnEraseFromPlaylist.clicked.connect(self.eraseSongFromPlaylistAction)

        # button for create playlist
        btnCreatePlaylist = QPushButton('Create Playlist',self)
        btnCreatePlaylist.move(505, 20)
        btnCreatePlaylist.clicked.connect(self.createPlaylistAction)

        # button for delete playlist
        btnDeletePlaylist = QPushButton('Delete Playlist',self)
        btnDeletePlaylist.move(620, 20)
        btnDeletePlaylist.clicked.connect(self.deletePlaylistAction)

        # button for merge playlist together
        btnMergePlaylist = QPushButton('Merge playlists',self)
        btnMergePlaylist.move(620, 80)
        btnMergePlaylist.clicked.connect(self.mergePlaylistsAction)

        # button for intersection for playlist
        btnInterPlaylist = QPushButton('Inter playlists',self)
        btnInterPlaylist.move(620, 110)
        btnInterPlaylist.clicked.connect(self.interPlaylistsAction)

        # button for  differece of two playlists
        btnSymDiffPlaylist = QPushButton('Diff playlists',self)
        btnSymDiffPlaylist.move(620,140)
        btnSymDiffPlaylist.clicked.connect(self.symetricDiffPlaylistsAction)

        # button for export playlist
        btnExportPlaylist = QPushButton('Export PL->ALBUM',self)
        btnExportPlaylist.move(620,170)
        btnExportPlaylist.clicked.connect(self.exportPlaylistAction)

        # button for BPM function
        btnBPM = QPushButton('Get BPM',self)
        btnBPM.move(620,210)
        btnBPM.clicked.connect(self.getBpmOfSong)

        #label to show bpm next to bpm button
        self.labelBPM = QLabel(self)
        self.labelBPM.move(620,240)
        self.labelBPM.resize(100,20)
        self.labelBPM.setStyleSheet("background-color: red; border: 1px inset grey;")
        self.labelBPM.setText("BPM: ")

        #show playlist name
        self.labelPlaylist = QLabel(self)
        self.labelPlaylist.move(300, 230)
        self.labelPlaylist.resize(200,20)
        self.labelPlaylist.setStyleSheet("background-color: white; border: 1px inset grey;")
        self.labelPlaylist.setText("")

        # call initialization at start of media player to init directory and playlists
        self.initSongList()
        self.songsList.sort()
        iterSongList = cycle(self.songsList)
        layout = QGridLayout()


        #songs in main playlist
        self.listWidget = QListWidget(self)
        for song in self.songsList:#fill list with songs
            self.listWidget.addItem(song)
        #Resize width and height
        self.listWidget.resize(270,370)
        self.listWidget.move(20, 250)

        # main playlist
        self.listWidget.setWindowTitle('PyQT QListwidget Demo')
        self.listWidget.clicked.connect(self.listview_clicked)

        #playlist for operations
        self.playlistWidget = QListWidget(self)
        self.playlistWidget.resize(240,370)
        self.playlistWidget.move(300, 250)

        self.playlistWidget.clicked.connect(self.playlistview_clicked)
        #self.playlistWidget

        #Song Info Box
        self.groupbox = QGroupBox("Song Info",self)
        self.groupbox.move(50, 46)
        self.groupbox.resize(500, 170)
        self.hbox = QHBoxLayout()
        self.v2box = QVBoxLayout()
        self.vbox = QVBoxLayout()
        self.infoLabels = []
        # labels in box of song for metadata
        for i in range(0,5):
            self.infoLabels.append(QLabel(""))
            self.vbox.addWidget(self.infoLabels[i])

        #self.groupbox.setLayout(vbox)
        #groupbox.setFont(QtGui.QFont("Sanserif", 15))
        self.imageAlbumLabel = QLabel(self)
        self.v2box.addWidget(self.imageAlbumLabel)
        self.v2box.setAlignment(Qt.AlignTop)

        # set box to 2 vertical boxes
        self.hbox.addLayout(self.v2box)
        self.hbox.addLayout(self.vbox)
        self.groupbox.setLayout(self.hbox)

        #vbox.addWidget(label)

        #init metadata databse table
        self.tableWidgetMeta = QTableWidget(self)
        self.tableWidgetMeta.move(550,270)
        self.tableWidgetMeta.resize(240,350)


        #self.setGeometry(100, 100, 750, 400)
        self.setFixedSize(800, 640)
        self.setWindowTitle('Gnome Music Player Clone')

        self.show()

    def getBpmOfSong(self):
        """ Calls bpm of WAV file from module beatalg
            sets value in label in red
        """
        if(self.pickedSong.lower().endswith(".wav")):
            song = self.filesList + "/" + self.pickedSong
            bpm = beatalg.getBPM(song)


            self.labelBPM.setText("BPM: " + str(bpm))

    def addSongToPlaylistAction(self):
        """ Add picked song to playlist

        """
        if(self.pickedSong):
            for x in range(len(self.allPlaylists)):
                if(self.allPlaylists[x].getNameOfPlaylist() == self.currentPlaylist.getNameOfPlaylist()):#current playlist
                    self.allPlaylists[x].addSongToPlaylist(self.pickedSong)
                    self.refreshPlaylistWidget()

    def eraseSongFromPlaylistAction(self):
        """ Erase Picked song from playlist

        """
        if(self.playlist2CurrentSong):
            #print(self.playlist2CurrentSong)
            for x in range(len(self.allPlaylists)):
                if(self.allPlaylists[x].getNameOfPlaylist() == self.currentPlaylist.getNameOfPlaylist()):#current playlist
                    self.allPlaylists[x].removeSongFromPlaylist(self.playlist2CurrentSong)
                    self.refreshPlaylistWidget()

    def addToPlaylists(self, playlist):
        self.allPlaylists.append(playlist)

    def initDatabaseTable(self, nameArtist, nameSong):
        """ Automatic download of metadata from web database
            data shows in table panel in right side

            Parameters
            ----------
            nameArtist - str
                Artist to find in database
            nameSong - str
                Song from artist to search

        """
        metadataList = data.getMetadata(nameArtist,nameSong)
        rowL = len(metadataList)
        if(rowL < 1):#do nothing, no data
            return
        #set length of rows in table
        self.tableWidgetMeta.setRowCount(rowL)
        self.tableWidgetMeta.setColumnCount(2)
        #catch error for empty metadaList
        i = 0
        for key, value in metadataList.items():
            self.tableWidgetMeta.setItem(i,0, QTableWidgetItem(key))
            self.tableWidgetMeta.setItem(i,1, QTableWidgetItem(value))
            i = i + 1


    def savePermanent(self):
        """
            Permanent objects
        """
        try:
            pickle.dump(self.allPlaylists, self.f)
            self.f.close()
        except:
            pass
        #print("Saving data")


    def mergePlaylistsAction(self):
        """
            Gets all songs to one new playlist
            with new name, user as to set
        """
        newName, ok = QInputDialog.getText(self, 'Merge of Playlist', 'Set new Name for merged playlist:')
        if not ok:
            return
        if not newName:
            return
        tempArray1 = []#names of playlist to qdialog
        for x in range(len(self.allPlaylists)):
            tempArray1.append(self.allPlaylists[x].getNameOfPlaylist())
        firstPlaylist, ok = QInputDialog.getItem(self, "First Playlist", "Select first playlist to merge",tempArray1 , 0, False)
        if not ok:
            return
        tempArray2 = []#names of playlist to qdialog
        for x in range(len(self.allPlaylists)):
            if(self.allPlaylists[x].getNameOfPlaylist() != firstPlaylist):
                tempArray2.append(self.allPlaylists[x].getNameOfPlaylist())
        if not ok:
            return
        secondPlaylist, ok = QInputDialog.getItem(self, "Second Playlist", "Select second playlist to merge",tempArray2 , 0, False)

        playlist1 = Playlist()
        playlist1 = self.playlistFromName(firstPlaylist)
        playlist2 = Playlist()
        playlist2 = self.playlistFromName(secondPlaylist)

        merged = Playlist()
        merged.setNameToPlaylist(newName)
        merged.setMergedList(playlist1.getAllSongs(), playlist2.getAllSongs())
        self.allPlaylists.append(merged)

        self.refreshPlaylistWidget() #refresh values

    def interPlaylistsAction(self):
        """ Picks common songs from two playlists
            to new one
        """
        newName, ok = QInputDialog.getText(self, 'Intersection of Playlists', 'Set new Name for final playlist:')
        if not ok:
            return
        if not newName:
            return
        tempArray1 = []#names of playlist to qdialog
        for x in range(len(self.allPlaylists)):
            tempArray1.append(self.allPlaylists[x].getNameOfPlaylist())
        firstPlaylist, ok = QInputDialog.getItem(self, "First Playlist", "Select first playlist to intersect",tempArray1 , 0, False)
        if not ok:
            return
        tempArray2 = []#names of playlist to qdialog without one
        for x in range(len(self.allPlaylists)):
            if(self.allPlaylists[x].getNameOfPlaylist() != firstPlaylist):
                tempArray2.append(self.allPlaylists[x].getNameOfPlaylist())

        secondPlaylist, ok = QInputDialog.getItem(self, "Second Playlist", "Select second playlist to merge",tempArray2 , 0, False)
        if not ok:
            return

        playlist1 = Playlist()
        playlist1 = self.playlistFromName(firstPlaylist)
        playlist2 = Playlist()
        playlist2 = self.playlistFromName(secondPlaylist)

        intersected = Playlist()
        intersected.setNameToPlaylist(newName)
        intersected.setIntersectedList(playlist1.getAllSongs(), playlist2.getAllSongs())
        self.allPlaylists.append(intersected)

        self.refreshPlaylistWidget() #refresh values

    def symetricDiffPlaylistsAction(self):
        """
            Difference of playlists
        """
        newName, ok = QInputDialog.getText(self, 'Intersection of Playlists', 'Set new Name for final playlist:')
        if not ok:
            return
        if not newName:
            return
        tempArray1 = []#names of playlist to qdialog
        for x in range(len(self.allPlaylists)):
            tempArray1.append(self.allPlaylists[x].getNameOfPlaylist())
        firstPlaylist, ok = QInputDialog.getItem(self, "First Playlist", "Select first playlist to intersect",tempArray1 , 0, False)
        if not ok:
            return
        tempArray2 = []#names of playlist to qdialog without one
        for x in range(len(self.allPlaylists)):
            if(self.allPlaylists[x].getNameOfPlaylist() != firstPlaylist):
                tempArray2.append(self.allPlaylists[x].getNameOfPlaylist())
        if not ok:
            return
        secondPlaylist, ok = QInputDialog.getItem(self, "Second Playlist", "Select second playlist to merge",tempArray2 , 0, False)

        playlist1 = Playlist()
        playlist1 = self.playlistFromName(firstPlaylist)
        playlist2 = Playlist()
        playlist2 = self.playlistFromName(secondPlaylist)

        symDiff = Playlist()
        symDiff.setNameToPlaylist(newName)
        symDiff.setSymDiffList(playlist1.getAllSongs(), playlist2.getAllSongs())
        self.allPlaylists.append(symDiff)

        self.refreshPlaylistWidget() #refresh values


    def playlistFromName(self, name):
        """ Search in list of playlists

            Parameters
            ----------
            name : str
                Name of searched playlist
            Returns
            -------
            list : copy of found playlist, to new instance in callable
        """
        for x in range(len(self.allPlaylists)):
            if(self.allPlaylists[x].getNameOfPlaylist() == name):
                tempPlaylist = Playlist()
                tempPlaylist = copy.copy(self.allPlaylists[x])

        return tempPlaylist

    def createPlaylistAction(self):
        """
            Creates new playlist, from input dialog
            make new instance of playlist
        """
        text, ok = QInputDialog.getText(self, 'Playlist Creator', 'Enter playlist name:')
        if not ok:
            return
        tempPlay = Playlist()
        tempPlay.setNameToPlaylist(str(text))
        #tempPlay.addSongToPlaylist("zzzz")

        self.allPlaylists.append(tempPlay)

        self.refreshPlaylistWidget() #refresh values

        #if ok:
         #print(str(text))

    def deletePlaylistAction(self):
        """
            Deletes playlist that user sets in input dialog
        """
        tempArray = []#names of playlist to qdialog
        for x in range(len(self.allPlaylists)):
            tempArray.append(self.allPlaylists[x].getNameOfPlaylist())


        item, ok = QInputDialog.getItem(self, "select input dialog", "list of playlists",tempArray , 0, False)

        if not ok:
            return

        if not item:
            return
        nameOfDeletedPlaylist = str(item)

        #print(len(self.allPlaylists))
        for x in range(len(self.allPlaylists)):
            if(self.allPlaylists[x].getNameOfPlaylist() == nameOfDeletedPlaylist):
                self.allPlaylists.pop(x)#delete playlist
                break#break, deletes last item and dynamically lowers index so crash appears

        #check for current playlsit deleted
        if(self.currentPlaylist.getNameOfPlaylist() == nameOfDeletedPlaylist):
            if( len(self.allPlaylists) > 0 ):
                self.currentPlaylist = self.allPlaylists[0]
            else:#if there is no other playlist
                self.currentPlaylist.setNameToPlaylist("")
                self.currentPlaylist.clearAllPlaylist()

        self.refreshPlaylistWidget()

    def exportPlaylistAction(self):
        if(not self.currentPlaylist):
            print("not selected playlist")
            return

        #setAlbum name for zip
        albumName = self.currentPlaylist.getNameOfPlaylist()
        zipName = (albumName + ".zip")
        myzip = zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED)

        # for every song add album metadata and do zipping
        for name in (self.currentPlaylist.getAllSongs()):#iterate songs in playlist
            if (name.lower().endswith(".mp3")):
                try:
                    tags =  EasyID3(self.filesList + "/" + name)
                except Exception:
                    tags =  EasyID3()

                # add album info
                originalAlbum = tags['album']
                tags['album'] = albumName
                tags.save()
                #zip to file
                myzip.write(name)
                #get original album back
                tags['album'] = originalAlbum
                tags.save()

            if (name.lower().endswith(".wav")):
                myzip.write(name)
        mess = ("Playlist exported to directory:\n\t" + self.filesList)
        QMessageBox.about(self, "Export PL", mess)
        return

    def fillBoxSongPic(self):
        """
            Creates pixmap in song box info
            image gets from metadata of song
        """
        name = self.pickedSong
        pixmap = QPixmap()

        if (name.lower().endswith(".mp3")):
            try:
                audioMeta =  mutagen.File(self.filesList + "/" + self.pickedSong)
            except Exception:
                return 0

            for tag in audioMeta.tags.values():
                if tag.FrameID == 'APIC':
                    pixmap.loadFromData(tag.data)
                    break
            pixmap = pixmap.scaled(110, 110, Qt.KeepAspectRatio)
            self.imageAlbumLabel.setPixmap(pixmap)



    def fillBoxSongInfo(self):
        """
            Parsing metadat from local music files
            Two formats Wav and MP3

        """
        name = self.pickedSong
        #add path
        #song = ("/home/jakub/Music/The Cure - 1979 Boys Don't Cry/"+self.pickedSong)
        song = (self.filesList + "/" + self.pickedSong)

        if (name.lower().endswith(".mp3")):
            try:
                audio = ID3(song)
            except (ID3NoHeaderError):
                audio = ID3()#or return
                self.infoLabels[0].setText("Name: ")
                self.infoLabels[1].setText("Artist: ")
                self.infoLabels[2].setText("Length: ")
                self.infoLabels[3].setText("Format: ")
                return

            mp3s = MP3(song)
            try:
                self.infoLabels[0].setText("Name: " + audio["TIT2"].text[0])
            except:
                self.infoLabels[0].setText("Name: ")
            try:
                self.infoLabels[1].setText("Artist: " + audio["TPE1"].text[0])
            except:
                self.infoLabels[1].setText("Artist: ")
            try:
                self.infoLabels[2].setText("Length: " + self.secondsLength(mp3s.info.length))
            except:
                self.infoLabels[2].setText("Length: ")
            try:
                self.infoLabels[3].setText("Format: " + str(mp3s.info.channels) + " channels, " + str(mp3s.info.sample_rate/1000) + "KHz, " + str(int(mp3s.info.bitrate/1000)) + "kbps")
            except:
                self.infoLabels[3].setText("Format: ")

            #print(audio.pprint())
            self.initDatabaseTable(audio["TPE1"].text[0], audio["TIT2"].text[0],)


        elif(name.lower().endswith(".wav")):

            try:
                metadata = audio_metadata.load(song)

            except:
                self.infoLabels[0].setText("Name: ")
                self.infoLabels[1].setText("Artist: ")
                self.infoLabels[2].setText("Length: ")
                self.infoLabels[3].setText("Format: ")
                return

            #print(metadata)

            try:
                self.infoLabels[0].setText("Name: " + metadata.tags['title'][0])
            except:
                self.infoLabels[0].setText("Name: ")
            try:
                self.infoLabels[1].setText("Artist: "+ metadata.tags['artist'][0])
            except:
                self.infoLabels[1].setText("Artist: ")
            try:
                self.infoLabels[2].setText("Length: " + self.secondsLength(metadata.streaminfo['duration']))
            except:
                self.infoLabels[2].setText("Length: ")
            try:
                self.infoLabels[3].setText("Format: " + str(metadata.streaminfo['channels']) + " channels, " + str(metadata.streaminfo['sample_rate']/1000) + "KHz, " + str(int(metadata.streaminfo['bitrate']/1000)) + "kbps")
            except:
                self.infoLabels[3].setText("Format: ")

            #todo: everything to block try except


        return

    def refreshPlaylistWidget(self):
        """
            Get current playlist to show in list widget
        """
        #make label
        self.labelPlaylist.setText(self.currentPlaylist.getNameOfPlaylist())
        # update songs in list widget
        self.playlistWidget.clear()
        for song in self.currentPlaylist.getAllSongs():#fill list with songs
            self.playlistWidget.addItem(song)


    def selectPlaylistAction(self):
        '''
            Select playlist from dialog
        '''
        tempArray1 = []#names of playlist to qdialog
        for x in range(len(self.allPlaylists)):
            tempArray1.append(self.allPlaylists[x].getNameOfPlaylist())

        if(len(self.allPlaylists) == 0):
            QMessageBox.about(self, "Nothing found", "No playlists available")
            return
        nameOfPickedPlaylist, ok = QInputDialog.getItem(self, "Second Playlist", "Select second playlist to merge",tempArray1 , 0, False)
        if not ok:
            return

        for idx in range(len(self.allPlaylists)):
            if self.allPlaylists[idx].getNameOfPlaylist() == nameOfPickedPlaylist:
                #print(self.allPlaylists[idx].getNameOfPlaylist())
                self.currentPlaylist = copy.copy(self.allPlaylists[idx])
                self.currentPlaylist.printAllsongs()

                self.refreshPlaylistWidget()


    def play(self):
        """
            Play song, two parts for mixer modul,
            from status paused to unpause and status stopped to play
        """
        if self.status == "Paused": #continues playing
            self.status = "Played"
            mixer.music.unpause()
            return
        else: # play song from beginning
            self.status = "Played"
            mixer.music.load(self.filesList + "/" + self.pickedSong)
            mixer.music.play()
            return

    def pause(self):
        """
            Pause Song
        """
        if self.status == "Played":
            self.status = "Paused"
            mixer.music.pause()
            return
        if self.status == "Stopped":
            mixer.music.pause()
            return

    def stop(self):
        """
            Just Stop playing song
        """
        mixer.music.stop()
        self.status = "Stopped"; #TODO: make enum for this
        return

    def next(self):
        """
            Play next song, with rotation of list
        """
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
        """
            Play rpevious song, with rotation of list
        """
        mixer.music.stop()
        index = self.songsList.index(self.pickedSong)#index of actual song
        deq = deque(self.songsList)
        deq.rotate(1)#shift to left
        self.pickedSong = deq[index]
        self.status = "Played"
        self.play()
        return

    def secondsLength(self, insec):
        """ Get format of time in song to show

            Parameters
            ----------
            insec : int
                number of seconds from metadata of file

            Returns
            -------
            str : String format to show in label
        """
        if insec == 0:
            return "X"
        min = int(insec / 60)
        sec = int(insec % 60)
        word = str(min) + "min:" + str(sec) + "sec"
        return word

        '''
    def closeEvent(self, event):

        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message',
                         quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.saveToFile()

            event.accept()
        else:
            event.ignore()
        '''
    def saveToFile(self):
        try:
            print("save data")
            with open('playlists', 'wb') as f:#overwrite file
                pickle.dump(self.allPlaylists, f, pickle.HIGHEST_PROTOCOL)
                print("opening")

        except:
            print("eeeeerrpr")
            pass
    def loadPermanentData(self): # opens file in main Init beacuse atexit part cant write to file
        pickle.dump(self.allPlaylists, self.file, pickle.HIGHEST_PROTOCOL)
        self.file.close()


if __name__ == '__main__':
    musicbrainzngs.set_useragent(
    "python-musicbrainzngs-example",
    "0.1",
    "https://github.com/alastair/python-musicbrainzngs/",
)



    app = QApplication(sys.argv)
    ex = MusicPlayer()
    sys.exit(app.exec_())
