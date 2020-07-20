import datetime
import urllib

from PyQt5 import QtCore, QtGui, QtWidgets

from design.main_window import Ui_MainWindow
from src.utils.youtb import VideoGetter


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        Ui_MainWindow.__init__(self)

        self.setupUi(self)
        self.vg = VideoGetter()

        self.preffered_format = None

        self.show()


    def signal_guardar(self):
        try:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar como...", self.edit_nombre.text(), f"{self.preffered_format} (*.{self.preffered_format})")
            if filename != "":
                self.progressBar.setEnabled(True)
                self.pushButton_2.setEnabled(False)
                self.edit_cb_extension.setEnabled(False)
                self.vg.getVideo(self, self.preffered_format, filename)

        except TypeError:
            pass


    def signal_search_url(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.vg.getUrl(self.edit_url.text())
        if self.vg.video is not None:
            self.edit_nombre.setText(self.vg.title)
            self.edit_duracion.setText(self.format_time(self.vg.duracion))
            self.set_image(self.vg.imageurl)
            self.vg.get_audio_formats()
            self.set_cb_extensions()
        QtWidgets.QApplication.restoreOverrideCursor()

    def format_time(self, seconds):
        a = datetime.timedelta(0, seconds)
        return str(a)

    def set_image(self, url):
        data = urllib.request.urlopen(url).read()
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(data)
        self.img_lbl.setPixmap(pixmap)

    def set_cb_extensions(self):
        self.edit_cb_extension.clear()
        for frmt in self.vg.formats:
            self.edit_cb_extension.addItem(frmt)

    def signal_cb_changed(self, signal):
        self.preffered_format = signal
        self.edit_size.setText(format_bytes(self.vg.formats[signal]["filesize"]))
        self.progressBar.setMaximum(self.vg.formats[signal]["filesize"])

    def progressHook(self, d):
        if d["status"] == "downloading":
            self.progressBar.setValue(d["downloaded_bytes"])
        if d["status"] == "finished":
            self.progressBar.setValue(0)
            self.pushButton_2.setEnabled(True)
            self.progressBar.setEnabled(False)
            self.edit_cb_extension.setEnabled(True)


def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'k', 2: 'm', 3: 'g', 4: 't'}
    while size > power:
        size /= power
        n += 1
    return str(format(size, ".2f"))+power_labels[n]+'b'