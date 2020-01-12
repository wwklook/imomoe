import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import QVideoWidget


class VideoWidget(QVideoWidget):
    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)
        self.setGeometry(QRect(90, 70, 900, 650))
        self.setContentsMargins(0, 0, 0, 0)
        self.is_watching = False
        self.playlist = []
        self.item = 0

        self.mv = QMediaPlayer(self)
        self.mv.setVideoOutput(self)
        self.mv_list = QMediaPlaylist(self.mv)
        self.mv_list.setPlaybackMode(QMediaPlaylist.Loop)
        self.mv.setPlaylist(self.mv_list)

        self.mv_slider = QSlider(Qt.Horizontal, parent)
        self.mv_slider.setObjectName('mv')
        self.mv_slider.setMinimum(0)
        self.mv_slider.sliderMoved[int].connect(lambda: self.mv.setPosition(self.mv_slider.value()))
        self.mv_slider.setGeometry(QRect(90, 720, 900, 20))

        self.mv_timer = QTimer()
        self.mv_timer.start(1000)
        self.mv_timer.timeout.connect(self.mvMode)

        self.mv_sound = QSlider(Qt.Horizontal, parent)
        self.mv_sound.setObjectName('mv')
        self.mv_sound.setMinimum(0)
        self.mv_sound.setMaximum(100)
        self.mv_sound.setValue(100)
        self.mv_sound.valueChanged[int].connect(self.mv_sounds)
        self.mv_sound.setGeometry(QRect(760, 740, 150, 40))

        self.mv_pause = QPushButton(parent)
        self.mv_pause.setObjectName('mv')
        self.mv_pause.clicked.connect(self.mv_stop)
        self.mv_pause.setIcon(QIcon('mv_play.ico'))
        self.mv_pause.setGeometry(QRect(90, 740, 40, 40))

        self.mv_next = QPushButton(parent)
        self.mv_next.setObjectName('mv')
        self.mv_next.clicked.connect(self.next_mv)
        self.mv_next.setIcon(QIcon('ico/next_mv.png'))
        self.mv_next.setGeometry(QRect(130, 740, 40, 40))

        self.mv_label1 = QLabel(parent)
        self.mv_label1.setObjectName('mv')
        self.mv_label1.setGeometry(QRect(170, 740, 52, 40))

        self.mv_label2 = QLabel(parent)
        self.mv_label2.setObjectName('mv')
        self.mv_label2.setGeometry(QRect(222, 740, 588, 40))

        self.mv_label3 = QLabel(parent)
        self.mv_label3.setObjectName('mv')
        self.mv_label3.setText(str(self.mv_sound.value()) + '%')
        self.mv_label3.setGeometry(QRect(910, 740, 40, 40))

        self.mv_sound_button = QPushButton(parent)
        self.mv_sound_button.setIcon(QIcon('ico/sound.ico'))
        self.mv_sound_button.setObjectName('mv')
        self.mv_sound_button.clicked.connect(self.mv_soundButton)
        self.mv_sound_button.setGeometry(QRect(720, 740, 40, 40))

        self.mv_fullscreen = QPushButton(parent)
        self.mv_fullscreen.setIcon(QIcon('ico/fullscreen.ico'))
        self.mv_fullscreen.setObjectName('mv')
        self.mv_fullscreen.clicked.connect(lambda: self.setFullScreen(True))
        self.mv_fullscreen.setGeometry(QRect(950, 740, 40, 40))

    def mvMode(self):
        if self.is_watching:
            self.mv_slider.setMaximum((self.mv.duration()))
            self.mv_slider.setValue(self.mv.position())
            self.mv_label1.setText(time.strftime('%M:%S/', time.localtime(self.mv.position() / 1000)))
            self.mv_label2.setText(time.strftime('%M:%S', time.localtime(self.mv.duration() / 1000)))

            if self.mv.position() + 1000 >= self.mv.duration() != 0:
                self.next_mv()
                self.mv_slider.setValue(0)

    def mv_stop(self):
        if self.is_watching:
            self.is_watching = False
            self.mv_pause.setIcon(QIcon('ico/mv_pause.ico'))
            self.mv.pause()
        else:
            self.is_watching = True
            self.mv.play()
            self.mv_pause.setIcon(QIcon('ico/mv_play.ico'))

    def mv_hide(self):
        self.hide()
        self.mv.stop()
        self.mv_label1.hide()
        self.mv_label2.hide()
        self.mv_label3.hide()
        self.mv_slider.hide()
        self.mv_pause.hide()
        self.mv_next.hide()
        self.mv_sound.hide()
        self.mv_fullscreen.hide()
        self.mv_sound_button.hide()

    def mv_view(self):
        self.show()
        self.mv_label1.show()
        self.mv_label2.show()
        self.mv_label3.show()
        self.mv_slider.show()
        self.mv_pause.show()
        self.mv_next.show()
        self.mv_sound.show()
        self.mv_fullscreen.show()
        self.mv_sound_button.show()

    def mv_sounds(self):
        self.mv.setVolume(self.mv_sound.value())
        self.mv_label3.setText(str(self.mv_sound.value()) + '%')
        if not self.mv_sound.value():
            self.mv_sound_button.setIcon(QIcon('ico/off.ico'))
        else:
            self.mv_sound_button.setIcon(QIcon('ico/sound.ico'))

    def mv_soundButton(self):
        if not self.mv_sound.value():
            self.mv_sound_button.setIcon(QIcon('ico/sound.ico'))
            self.mv_sound.setValue(self.mv_s)
        else:
            self.mv_s = self.mv_sound.value()
            self.mv_sound_button.setIcon(QIcon('ico/off.ico'))
            self.mv_sound.setValue(0)

    def play_mv(self):
        url = QUrl(self.playlist[self.item])
        content = QMediaContent(url)
        self.mv_list.addMedia(content)
        self.mv_list.setCurrentIndex(self.mv_list.mediaCount() - 1)
        self.is_watching = True
        self.mv_pause.setIcon(QIcon('ico/mv_play.ico'))
        time.sleep(1)
        self.mv.play()

    def next_mv(self):
        if self.item < len(self.playlist):
            self.item += 1
        else:
            self.item = 0
        self.play_mv()

    def mv_ff(self):
        if self.mv.duration() - self.mv.position() > 5000:
            self.mv.setPosition(self.mv.position() + 5000)

    def mv_retreat(self):
        if self.mv.position() > 5000:
            self.mv.setPosition(self.mv.position() - 5000)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.setFullScreen(False)
            self.setGeometry(QRect(90, 70, 900, 650))
        elif event.key() == Qt.Key_Space:
            self.mv_stop()
        elif event.key() == Qt.Key_Right or event.key() == Qt.Key_D:
            self.mv_ff()
        elif event.key() == Qt.Key_Left or event.key() == Qt.Key_A:
            self.mv_retreat()

    def mousePressEvent(self, *args, **kwargs):
        self.setFocus()
