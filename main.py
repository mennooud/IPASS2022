import numpy as np
import sys
import pyaudio
import pyqtgraph as pg
from qtpy import QtCore, QtGui, QtWidgets

class StartStop(QtCore.QThread):
    sig = QtCore.Signal(bytes)

    def __init__(self, sc):
        super(StartStop, self).__init__()
        self.sc = sc
        self.sig.connect(self.sc.unpack)
        self.running = True

    def run(self):
        while self.running:
            data = self.sc.stream.read(self.sc.CHUNK)
            self.sig.emit(data)

    def stop(self):
        sys.stdout.write('THREAD STOPPED')
        self.running = False

class AudioStream(QtWidgets.QWidget):
    def __init__(self):
        super(AudioStream, self).__init__()
        self.data = np.zeros((100000), dtype=np.int32)
        self.CHUNK = 1024 * 4
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.FPS = 60

    def startStream(self):
        self.audio = pyaudio.PyAudio()
        self.frames_per_buffer = self.CHUNK
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.frames_per_buffer
        )

        self.startstop = StartStop(self)
        self.startstop.start()

    def playStream(self):
        self.stream.write(self.stream.read(self.frames_per_buffer))


    def unpack(self, newdata):
        '''
        :param newdata: copy of data in Numpy array
        '''
        newdata = np.frombuffer(newdata, 'int16')
        c = self.CHUNK
        self.data[:-c] = self.data[c:]
        self.data[-c:] = newdata

        self.x = np.fft.fft(self.data)
        self.freqs = np.fft.fftfreq(len(self.x))
        self.index = np.argmax(np.abs(self.x))
        self.freq = self.freqs[self.index]
        self.hz = int(abs(self.freq * self.RATE))
        if self.hz > 16 and self.hz < 60:                     # Sub-bass	        20 to 60 Hz
            QtVizualize.strobe
            print('Sub')


    def stopStream(self):
        self.startstop.terminate()
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(400, loop.quit)
        loop.exec_()

class QtVizualize(object):
    def __init__(self):
        super(QtVizualize, self).__init__()
        '''
        Settings for visualization
        '''

        pg.setConfigOptions(antialias=True)
        self.app = QtGui.QApplication(sys.argv)
        self.win = pg.GraphicsWindow(title='Audio Analyzer')
        self.win.setWindowTitle('Audio Analyzer')


        self.sc = AudioStream()
        self.sc.startStream()


        self.vlayout = QtGui.QVBoxLayout()
        self.win.setLayout(self.vlayout)


        self.p1 = self.win.addPlot(title='Waveform',row=1, col=0)
        self.pdataitem = self.p1.plot(self.sc.data)
        self.vlayout.addWidget(self.sc)

        self.p2 = QtWidgets.QPushButton('STROBE')
        self.p2.setGeometry(200, 150, 100, 40)
        self.p2.setCheckable(True)
        #self.p2.clicked.connect(self.strobe)
        self.p2.setStyleSheet("background-color : lightgrey")
        #self.p2.released.connect(self.strobe)
        #self.p2.setChecked.connect(self.strobe)
        self.vlayout.addWidget(self.p2)

        self.win.show()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_streamplot)
        self.timer.timeout.connect(self.strobe)
        self.timer.start(10)


        self.startstop_button = QtWidgets.QPushButton('Stop')
        self.startstop_button.pressed.connect(self.startstop)
        self.startstop_button.status = 1
        self.vlayout.addWidget(self.startstop_button)

        #self.update()
        #self.show()

    def startstop(self):
        b = self.startstop_button
        b.setEnabled(False)
        if b.status:
            self.sc.stopStream()
            b.setText('Start')
            b.status = 0
        else:
            self.sc.startStream()
            b.setText('Stop')
            b.status = 1
        b.setEnabled(True)



    def strobe(self):
        '''
        Strobe currently not working. Trying to fix for the demo, waiting for materials.
        '''
        self.strobe = self.p2.isChecked()


    def closeEvent(self, event):
        if self.startstop_button.status:
            self.sc.breakdown_stream()
        event.accept()

    def update_streamplot(self):
        self.pdataitem.setData(self.sc.data)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    s = QtVizualize()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')