import sys
from PyQt5.QtWidgets import QApplication, QWidget,QTableWidget,QTableWidgetItem
import mutagen
from mutagen.mp3 import MP3 #metadata manipulation
from mutagen.id3 import *
import musicbrainzngs
import eyed3
import librosa
import scipy.stats
import json
import objectpath

def getMetadata(artist, release):
    finalList = {}

    #artistinfo = musicbrainzngs.search_recordings(artist="Rihanna", release="Umbrella")

    #ss = json.dumps(artistinfo, indent=4, sort_keys=True)


    #wjson = json.loads(ss)
    #jsonnn_tree = objectpath.Tree(wjson)
    #print(ss)
    #exit()


    result = musicbrainzngs.search_releases(artist=artist, tracks=release,limit=1)

    sorted_string = json.dumps(result, indent=4, sort_keys=True)
    #print(sorted_string)

    wjson = json.loads(sorted_string)
    jsonnn_tree = objectpath.Tree(wjson['release-list'])

    #print(result['release-list'])
    #print(type(result['release-list']))
    #print(len(result['release-list']))
    IDval = 0
    for (idx, release) in enumerate(result['release-list']):#goes once
        if 'date' in release:#check for existence
            finalList.update({"date":release['date']})
        if 'country' in release:
            finalList.update({"country":release['country']})
        if 'title' in release:
            finalList.update({"title":release['title']})
        if 'packaging' in release:
            finalList.update({"packaging":release['packaging']})
        if 'barcode' in release:
            finalList.update({"barcode":release['barcode']})
        if 'status' in release:
            finalList.update({"status":release['status']})
        if 'id' in release:
            finalList.update({"Release ID":release['id']})
            IDval = release['id']
        for (jdx, items) in enumerate(release):#iterovanie vo vsetkych
            repre = release[items]
            if 'text-representation' == items:
                if 'language' in (repre):
                    finalList.update({"language":repre['language']})
                if 'script' in (repre):
                    finalList.update({"script":repre['script']})
            if 'artist-credit' == items:
                #print(repre)
                #a = json.dumps(release[items], indent=4, sort_keys=True)
                #print(a)
                try:
                    tree = objectpath.Tree(release[items])
                    ent = tree.execute("$.artist[0]")
                    for x in (ent):
                        keyID = "Artist " + str(x)
                        finalList.update({keyID:ent[x]})
                except Exception:
                    pass
    for key, value in finalList.items():
        #print(key, "---", value)
        return finalList


class Example(QWidget):

    def __init__(self, flist):
        super().__init__()
        self.flist = flist
        self.initUI()


    def initUI(self):

        self.setGeometry(300, 300, 400, 620)
        self.setWindowTitle('Metadata box')
        self.initTable()
        self.show()

    def initTable(self):
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setRowCount(12)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.move(0,0)

        i = 0
        for key, value in finalList.items():
            self.tableWidget.setItem(i,0, QTableWidgetItem(key))
            self.tableWidget.setItem(i,1, QTableWidgetItem(value))
            i = i + 1




#if __name__ == '__main__':
#    musicbrainzngs.set_useragent(
    "python-musicbrainzngs-example",
    "0.1",
    "https://github.com/alastair/python-musicbrainzngs/",
#)
#    artist = "Rihanna"
#    song = "Umbrella"
#    getMetadata(artist,song)


    '''
    picRes = musicbrainzngs.get_image_list(IDval)


    picTree = json.dumps(picRes, indent=4, sort_keys=True)
    print(picTree)
    picObject = objectpath.Tree(picTree)
    entPic = tree.execute("$.picture")
    '''
    #for x in (ent):
        #finalList.update({x:ent[x]})
    #app = QApplication(sys.argv)
    #ex = Example(finalList)

    #sys.exit(app.exec_())
