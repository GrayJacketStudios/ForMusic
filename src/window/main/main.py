import datetime
import urllib

from PyQt5 import QtCore, QtGui, QtWidgets

from design.main_window import Ui_MainWindow
from src.utils.youtb import VideoGetter


from src.utils.worker import Worker

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        Ui_MainWindow.__init__(self)

        self.setupUi(self)
        self.setWindowTitle("ForMusic - descargar musica")
        self.vg = VideoGetter()

        self.preffered_format = None

        self.threadpool = QtCore.QThreadPool()
        self.run_downloader = True

        self.show()




    def signal_search_url(self):
        """ Busca la informacion del video segun la url proporcionada """
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        res = self.vg.getUrl(self.edit_url.text())
        if res == 0:
            self.edit_nombre.setText(self.vg.title)
            self.edit_duracion.setText(format_time(self.vg.duracion))
            try:
                self.set_image(self.vg.imageurl)
            except:
                pass
            self.vg.get_audio_formats()
            self.set_cb_extensions()
        elif res == -1:
            self.error_inesperado("La url introducida no es correcta, revisala!")
        elif res == -2:
            self.error_inesperado("No nos hemos podido conectar, revisa tu conexion.")
        QtWidgets.QApplication.restoreOverrideCursor()
        self.btn_guardar.setEnabled(True)

    def set_image(self, url):
        """ Coloca la imagen del video para identificarlo correctamente """
        data = urllib.request.urlopen(url).read()
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(data)
        self.img_lbl.setPixmap(pixmap)

    def set_cb_extensions(self):
        """ Coloca en nuestro combobox las extensiones disponibles del video """
        self.edit_cb_extension.clear()
        for frmt in self.vg.formats:
            self.edit_cb_extension.addItem(frmt)

    def signal_cb_changed(self, signal):
        """ accion cuando cambian nuestro combobox """
        self.preffered_format = signal
        if signal != "":
            self.edit_size.setText(format_bytes(self.vg.formats[signal]["filesize"]))
            self.progressBar.setMaximum(self.vg.formats[signal]["filesize"])


    def signal_guardar(self):
        """ accion el btn_guardar, indicando para guardar el archivo...
        >>> Preguntemos donde! """

        try:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar como...", self.edit_nombre.text(), f"{self.preffered_format} (*.{self.preffered_format})")
            if filename != "":
                self.limpia_pantalla()
                self.descargar_musica(self.preffered_format, filename)


        except TypeError as err:
            self.error_inesperado(f"Error: {err}")

    def progressHook(self, d):
        """ Nuestro hook con ydl que nos indica el estado de la descarga """
        if d["status"] == "downloading":
            self.progressBar.setValue(d["downloaded_bytes"])
            self.lbl_progress.setText(f"{format_bytes(d['downloaded_bytes'])}/{format_bytes(d['total_bytes'])} - a {format_bytes(d['speed'])}/s")
            if self.run_downloader is False:
                raise ValueError

        if d["status"] == "finished":
            QtWidgets.QMessageBox.information(self, "Operación realizada", "¡Se ha descargado la canción exitosamente!")
            self.limpia_pantalla(False)
        if d["status"] == "error":
            self.error_inesperado()
            self.limpia_pantalla(False)


    def error_inesperado(self, txt="Ocurrio un error inesperado."):
        QtWidgets.QMessageBox.warning(self, "Error", txt)

    def descargar_musica(self, format, path):
        self.run_downloader = True
        worker = Worker(self.vg.getVideo, (self, self.preffered_format, path))
        self.threadpool.start(worker)

    def signal_btn_cancelar(self):
        self.run_downloader = False
        self.error_inesperado("Se cancelo la descarga")
        self.limpia_pantalla(False)

    def limpia_pantalla(self, flag=True):
        """ Limpia los valores
        >>> flag == True: Bloquea todo menos el boton cancelar
        >>> flag == False: Desbloquea todas las opciones y bloquea cancelar """
        if flag:
            self.btn_cancelar.setEnabled(True)
            self.progressBar.setEnabled(True)
            self.edit_cb_extension.setEnabled(False)
            self.btn_guardar.setEnabled(False)
            self.edit_nombre.setEnabled(False)
        else:
            self.btn_cancelar.setEnabled(False)
            self.progressBar.setEnabled(False)
            self.progressBar.setValue(0)
            self.lbl_progress.setText("")
            self.edit_cb_extension.setEnabled(True)
            self.btn_guardar.setEnabled(True)
            self.edit_nombre.setEnabled(True)


def format_bytes(size):
    """ Nos devuelve un texto comprensible con el tamaño """
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'k', 2: 'm', 3: 'g', 4: 't'}
    while size > power:
        size /= power
        n += 1
    return str(format(size, ".2f"))+power_labels[n]+'b'

def format_time(seconds):
    """ Nos devuelve la duracion del video de forma comprensible """
    a = datetime.timedelta(0, seconds)
    return str(a)