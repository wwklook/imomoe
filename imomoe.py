import re
import os
import sys
import requests
import threading
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import VideoWidget as VW

class Thread(threading.Thread):
    def __init__(self, func):
        super(Thread, self).__init__()
        self.func = func

    def run(self):
        self.func()

class Imomoe(QMainWindow):
    def __init__(self, parent=None):
        super(Imomoe, self).__init__(parent)
        self.setWindowTitle('樱花动漫')
        self.setGeometry(100, 60, 1200, 800)
        self.is_watching = False
        self.where = ''

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.mask = QBitmap(1200, 800)
        self.mask.fill(Qt.white)
        painter = QPainter(self.mask)
        painter.setBrush(QColor(0x000000))
        painter.drawRoundedRect(0, 0, 1200, 800, 25, 20)
        self.setMask(self.mask)

        self.name = QLineEdit(self)
        self.name.setPlaceholderText('- - * - - 搜索动漫 - - * - -')
        self.name.returnPressed.connect(self.search1)
        self.name.setGeometry(QRect(230, 20, 300, 35))
        act = QAction(QIcon('search.ico'), '搜索', self)
        act.triggered.connect(self.search1)
        self.name.addAction(act, QLineEdit.TrailingPosition)

        min = QPushButton(self)
        min.setIcon(QIcon('./ico/min.ico'))
        min.clicked.connect(self.min)
        min.setGeometry(QRect(1138, 0, 32, 32))
        end = QPushButton(self)
        end.setIcon(QIcon('./ico/close.ico'))
        end.clicked.connect(self.end)
        end.setGeometry(QRect(1168, 0, 32, 32))

        self.Table = QTableWidget(self)
        self.Table.setColumnCount(2)
        self.Table.setColumnWidth(0, 110)
        self.Table.setColumnWidth(1, 690)
        self.Table.setGeometry(QRect(70, 70, 820, 650))
        self.Table.setIconSize(QSize(100, 150))
        self.Table.verticalHeader().setVisible(False)
        self.Table.horizontalHeader().setVisible(False)
        self.Table.setShowGrid(False)
        self.Table.setAlternatingRowColors(True)
        self.Table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.Table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.Table.itemDoubleClicked.connect(self.get_episode1)

        self.Table1 = QTableWidget(self)
        self.Table1.setColumnCount(1)
        self.Table1.setColumnWidth(0, 600)
        self.Table1.setGeometry(QRect(70, 70, 620, 650))
        self.Table1.verticalHeader().setVisible(False)
        self.Table1.horizontalHeader().setVisible(False)
        self.Table1.setShowGrid(False)
        self.Table1.setAlternatingRowColors(True)
        self.Table1.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.Table1.setSelectionMode(QAbstractItemView.SingleSelection)
        self.Table1.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Table1.customContextMenuRequested[QPoint].connect(self.showContextMenu)
        self.Table1.itemDoubleClicked.connect(self.movie1)
        self.Table1.hide()

        self.tip = QLabel(self)
        self.tip.setObjectName('tip')
        self.tip.setGeometry(QRect(600, 20, 480, 35))

        self.mv_show = VW.VideoWidget(self)
        # self.mv_show.setGeometry(QRect(90, 70, 900, 650))
        self.mv_show.mv_hide()

    def search1(self):
        thread = Thread(self.search)
        thread.start()
        self.Table1.hide()
        self.Table.show()
        self.mv_show.mv_hide()

    def search(self):
        self.tip.setText("正在查找相关视频......")
        self.where = ''
        self.playlist = []
        word = self.name.text()
        req = requests.post('http://www.imomoe.io/search.asp', data={'searchword': word.encode('gb2312')})
        req.encoding = 'gb2312'
        soup = BeautifulSoup(req.text, 'html.parser')
        div = soup.select('div .pics')[0]
        try:
            self.Table.setRowCount(len(div.ul.li) / 2)
        except Exception:
            self.tip.setText("没有找到与“" + word + "”相关的结果")
            return
        self.page_url = []
        self.img_url = []
        self.text = []
        for i in div.ul:
            try:
                self.page_url.append('http://www.imomoe.io' + i.a.get('href'))
                self.img_url.append(i.a.img.get('src'))
                self.text.append(i.text)
            except Exception:
                pass
        self.Table.setRowCount(len(self.page_url))
        for i in range(len(self.page_url)):
            self.Table.setRowHeight(i, 160)
            photo = QPixmap()
            photo.loadFromData((requests.get(self.img_url[i]).content))
            self.Table.setItem(i, 0, QTableWidgetItem(QIcon(photo), ''))
            item = QTableWidgetItem(self.text[i])
            self.Table.setItem(i, 1, item)
        self.tip.setText("搜索成功,请选择......")

    def get_episode1(self):
        thread = Thread(self.get_episode)
        thread.start()
        self.Table.hide()
        self.Table1.setColumnWidth(0, 600)
        self.Table1.setGeometry(QRect(70, 70, 620, 650))
        self.Table1.show()

    def get_episode(self):
        self.tip.setText("正在搜索视频剧集......")
        item = self.Table.currentRow()
        self.titletip = self.text[item].split('\n')[1]
        url = self.page_url[item]
        req = requests.get(url)
        req.encoding = 'gb2312'
        soup = BeautifulSoup(req.text, 'html.parser')
        div = soup.select('div .movurl')
        self.episode = []
        self.title = []
        for i in div[0].ul:
            self.title.append(i.a.get('title'))
            self.episode.append(i.a.get('href'))
        self.Table1.setRowCount(len(self.title))
        for i in range(len(self.title)):
            self.Table1.setRowHeight(i, 50)
            item = QTableWidgetItem(self.title[i])
            self.Table1.setItem(i, 0, item)
        self.tip.setText("搜索成功,请选择......")

    def movie1(self):
        thread = Thread(self.movie)
        thread.start()
        self.mv_show.mv_view()

    def movie(self):
        self.tip.setText("正在获取资源...")
        item = self.Table1.currentRow()
        if self.where == 'mv':
            self.mv_show.item = item
            self.mv_show.play_mv()
            self.tip.setText("搜索成功,正在观看--" + self.titletip)
            return
        url = self.episode[item]

        print('http://www.imomoe.io' + url)
        self.get_mv(url)
        print(self.playlist)
        self.Table1.setColumnWidth(0, 190)
        self.Table1.setGeometry(991, 70, 210, 650)
        self.mv_show.playlist = self.playlist
        self.mv_show.item = item
        self.where = 'mv'
        self.mv_show.play_mv()
        self.tip.setText("搜索成功,正在观看--" + self.titletip)

    def get_mv(self, url):
        req = requests.get('http://www.imomoe.io' + url)
        soup = BeautifulSoup(req.text, 'html.parser')
        src = soup.find('div', class_='player').script.get('src')
        u = 'http://www.imomoe.io' + src
        movie_url = re.findall(r"\$(http[^\$]+)", requests.get(u).text)
        self.playlist = []
        if len(movie_url) < len(self.episode):
            movie_url = re.findall(r"\$([^\$pvod]+)", requests.get(u).text)
            print(movie_url)
            if len(movie_url) < len(self.episode):
                self.tip.setText("搜索失败，找不到视频来源")
                return
            else:
                for i in range(len(movie_url)):
                    s = 'https://v.jialingmm.net/mmletv/mms.php?vid=%s&type=letv' % movie_url[i]
                    try:
                        src = re.findall("var video =  '([^']+)", requests.get(s).text)[0]
                    except Exception:
                        src = ''
                    self.playlist.append(src)
        else:
            self.playlist = movie_url[:len(self.episode)]

    def showContextMenu(self, point):
        self.item = self.Table1.row(self.Table1.itemAt(point.x(), point.y()))
        if self.item != -1:
            self.Menu = QMenu(self.Table1)
            self.Menu.addAction((QAction(u'播放', self, triggered=self.movie1)))
            self.Menu.addAction((QAction(u'下载', self, triggered=self.load)))
        self.Menu.exec_(QCursor.pos())

    def download(self):
        if self.playlist == []:
            self.get_mv(self.episode[self.item])
        req = requests.get(self.playlist[self.item])
        if not os.path.exists(self.titletip):
            os.mkdir(self.titletip)
        os.chdir(self.titletip)
        filename = self.title[self.item] + '.mp4'
        try:
            print('正在下载')
            with open(filename, 'wb') as f:
                f.write(req.content)
        except Exception:
            print('出现预料之外的错误')
        os.chdir('../')
        print("下载完成")

    def load(self):
        thread = Thread(self.download)
        thread.start()

    def end(self):
        self.close()

    def min(self):
        self.showMinimized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def keyPressEvent(self, event):
        if self.where == 'mv':
            if event.key() == Qt.Key_F11:
                self.mv_show.setFullScreen(True)
            elif event.key() == Qt.Key_Space:
                self.mv_show.mv_stop()
            elif event.key() == Qt.Key_Right or event.key() == Qt.Key_D:
                self.mv_show.mv_ff()
            elif event.key() == Qt.Key_Left or event.key() == Qt.Key_A:
                self.mv_show.mv_retreat()

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.width(), self.height(), QPixmap('./ico/4.jpg'))


gss = '''
    QWidget {
        border-radius:30px;
        font: 75 12pt "黑体";
        }
    QTableWidget {
        color: white;
        background-color: rgba(0,0,0,0.1);
        alternate-background-color: rgba(0,0,0,0.15);
        border: none;
        border-radius:50px;
    }
    QLabel#mv {
        color: rgba(34,174,230,1);
        font: 65 13pt "华文行楷";
    }
    QLabel#tip {
        color: #FFFFFF;
        font: 75 15pt "楷体";
    }
    QPushButton {
        border-radius:15px;
    }
    QPushButton:hover {
        background-color: rgba(0,0,0,0.4);
    }
    QLineEdit {
        margin-bottom: 1px;
        border: 4px solid #555555;
        border-radius: 15px;
        color: #00ff00;
        font: 75 12pt "黑体";
        background: #555555;
    }
    QHeaderView:section {
        font: 75 14pt "楷体";
        background: rgba(0,0,0,0.3);
    }
    QTableWidget:item {
        background: rgba(0,0,0,0.3);
        color: #FFFFFF;
        border-bottom:1px solid #EEF1F7;
    }
    QTableWidget:item:selected {
        background: rgba(0,0,110,0.4);
        color: #FFFFFF;
    }
    QScrollArea {
        background: #16181C;
        border: none;
    }
    QSlider {
        border-color: #bcbcbc;
    }
    QSlider:groove:horizontal {                                
        border: 2px solid #999999;                             
        height: 1px;                                           
        margin: 0px 0;                                         
        left: 5px; right: 5px; 
    }
    QSlider:handle:horizontal {                               
        border: 0px ;                           
        border-image: url('fire.ico');
        width: 15px;                                           
        margin: -12px -10px -3px -10px;                  
    }
    QSlider:add-page:horizontal{
        background: #FF6347;
    }
    QSlider:sub-page:horizontal{                               
        background: #FF4500;
    }
    QScrollBar {
        background: rgba(0,0,0,0);
        border: none;
        border-radius: 1px;
    }
    QScrollBar:handle:vertical {
        width: 8px;
        background: rgba(0,245,255,0.3);
        border-radius: 1px;
        min-height: 20px;
    }
    QScrollBar:handle:vertical:hover {
        width: 9px;
        background: rgba(0,245,255,0.4);
        border-radius: 10%;
        min-height: 5px;
    }
    QScrollBar:add-page:vertical,QScrollBar::sub-page:vertical
    {
        background:rgba(0,0,0,10%);
        border-radius:15px;
    }
    QScrollBar:add-line:vertical,QScrollBar::sub-line:vertical
    {
        border: none;
    }
    QSlider#mv,QLabel#mv,QPushButton#mv {
        background: rgba(0,0,0,0.2);
        border-radius: none;
    }
    QPushButton:hover#mv {
        background: rgba(0,0,0,0.4);
    }
'''

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('favicon.ico'))
    main = Imomoe()
    main.setStyleSheet(gss)
    main.show()
    sys.exit(app.exec_())
