from .wifi_utils import connect_to_wifi_dbus, connect_to_wifi_pywifi
import sys
from threading import Event, Lock
from PyQt6 import QtCore, QtGui, QtWidgets
import subprocess
from PyQt6.QtWidgets import QFileDialog
import copy
from PIL.ImageQt import ImageQt
import qrcode
from threading import Thread
from PIL import Image
from PyQt6 import QtGui, QtCore, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.uic import loadUiType
from PyQt6.QtGui import QPixmap
import cv2
import numpy as np
from PyQt6.QtCore import pyqtSignal, Qt
import time
import os
import pyperclip
import webbrowser
import platform
from .clipboard import copy_to_clipboard

from pyzbar.pyzbar import decode


if __file__ and os.path.exists(__file__):
    os.chdir(os.path.dirname(__file__))


def qr_decoder(image):
    gray_img = cv2.cvtColor(image, 0)
    qr_code = decode(gray_img)

    for obj in qr_code:
        points = obj.polygon
        (x, y, w, h) = obj.rect
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(image, [pts], True, (0, 255, 0), 3)

        cv2.putText(
            image,
            obj.data.decode(),
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 0, 0),
            2,
        )
        return {"image": image, "type": obj.type, "data": obj.data}


abs_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)))
if os.path.exists(os.path.join(abs_dir, "ScanGen.ui")):
    os.chdir(abs_dir)
    Ui_MainWindow, QMainWindow = loadUiType("ScanGen.ui")
else:
    from .ScanGen import Ui_MainWindow


class ScanGen(QMainWindow, Ui_MainWindow):
    data = ""
    update_qr_code_sig = pyqtSignal()
    update_text_sig = pyqtSignal()
    search_for_cameras_sig = pyqtSignal()
    update_camera_list_sig = pyqtSignal(list)

    current_camera_info = None
    radio_buttons = []
    closing = False

    def __init__(
        self,
    ):
        super(ScanGen, self).__init__()
        self.setupUi(self)
        bundle_dir = getattr(
            sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__))
        )
        self.setWindowIcon(QtGui.QIcon(os.path.join(bundle_dir, "Icon.svg")))
        self.setWindowTitle("QR ScanGen")
        self.layed_out_vertically = False
        self.camera_initialised = Event()
        self.update_text_sig.connect(self.update_text)
        self.update_qr_code_sig.connect(self.update_qr_code)
        self.search_for_cameras_sig.connect(self.search_for_cameras)
        self.update_camera_list_sig.connect(self.udpate_camera_list)
        self.text_txbx.textChanged.connect(self.text_changed)
        self.qr_code_lbl.mousePressEvent = self.save_qr_file
        self.text_lock = Lock()

        Thread(target=self.run_scanner, args=()).start()
        # self.search_for_cameras_sig.emit()
        print("ready")

    def text_changed(self, _=None):
        with self.text_lock:
            if self.text_txbx.toPlainText() != self.data:
                self.data = self.text_txbx.toPlainText()
                self.update_qr_code_sig.emit()

    def resizeEvent(self, _=None):
        self.update_qr_code()
        self.text_txbx.setFixedHeight(self.height() // 6)
        if self.width() < self.height() and not self.right_frame_lyt.isEmpty():
            self.layed_out_vertically = True
            self.right_frame_lyt.removeWidget(self.qr_code_lbl)
            self.cam_frm_lyt.insertWidget(0, self.qr_code_lbl)
            self.scanner_video_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.qr_code_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            # self.right_frame_lyt.setVisible(False)
            self.images_frm_lyt.removeWidget(self.right_frame)
        elif self.width() > self.height() and self.right_frame_lyt.isEmpty():
            self.layed_out_vertically = False
            self.cam_frm_lyt.removeWidget(self.qr_code_lbl)
            self.right_frame_lyt.addWidget(self.qr_code_lbl)
            self.images_frm_lyt.addWidget(self.right_frame)
            self.scanner_video_lbl.setAlignment(
                QtCore.Qt.AlignmentFlag.AlignLeft
                | QtCore.Qt.AlignmentFlag.AlignTop
                | QtCore.Qt.AlignmentFlag.AlignTrailing
            )
            self.qr_code_lbl.setAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight
                | QtCore.Qt.AlignmentFlag.AlignTop
                | QtCore.Qt.AlignmentFlag.AlignTrailing
            )

            # self.right_frame_lyt.setVisible(True)

    def update_qr_code(self):
        qr_code = self.generate_qr_code(self.data)

        image = ImageQt((qr_code.get_image()))
        self.qr_code_lbl.setPixmap(QtGui.QPixmap.fromImage(image))

    def update_text(self):
        self.text_txbx.setPlainText(self.data)

    def list_camera_ports(self):
        """
        Test the ports and returns a tuple with the available ports and the ones that are working.
        """
        non_working_ports = []
        available_cameras = []

        # iterate through ports starting at 0.
        # if there are more than 5 non working ports stop the testing.
        dev_port = 0
        while len(non_working_ports) < 6:
            if (
                self.current_camera_info
                and dev_port == self.current_camera_info["port"]
            ):
                available_cameras.append(self.current_camera_info)
            else:
                camera = cv2.VideoCapture(dev_port)
                if camera.isOpened():
                    is_reading, img = camera.read()
                    w = camera.get(3)
                    h = camera.get(4)
                    if is_reading:
                        width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = camera.get(cv2.CAP_PROP_FPS)
                        camera_name = get_camera_name(dev_port)

                        camera_info = {
                            "port": dev_port,
                            "name": camera_name,
                            "width": width,
                            "height": height,
                            "fps": fps,
                        }
                        available_cameras.append(camera_info)

                else:
                    non_working_ports.append(dev_port)
                camera.release()
            dev_port += 1
        if (
            not self.current_camera_info and available_cameras
        ):  # if Scanner currently doesn't know which camera to use
            self.current_camera_info = available_cameras[0]
        return available_cameras

    def change_camera(self, e):
        self.current_camera_info = self.sender().camera_info

    testing_camera_ports = False

    def search_for_cameras(self):
        if self.testing_camera_ports:
            return
        self.testing_camera_ports = True

        def _search_for_cameras():
            working_cameras = self.list_camera_ports()
            self.update_camera_list_sig.emit(working_cameras)
            self.testing_camera_ports = False

        Thread(target=_search_for_cameras, args=()).start()

    def udpate_camera_list(self, working_cameras: list):
        for radio_button in self.radio_buttons:
            try:
                radio_button.deleteLater()
            except:
                pass
        for cam_info in working_cameras:
            label = f"{cam_info['port']} {cam_info['name']}"
            radio_button = QtWidgets.QRadioButton(label, self.right_frame)
            radio_button.camera_info = cam_info
            if cam_info["port"] == self.current_camera_info["port"]:
                radio_button.setChecked(True)
            radio_button.clicked.connect(self.change_camera)
            self.cam_frm_lyt.addWidget(radio_button)
            self.radio_buttons.append(radio_button)

    def run_scanner(self):
        # camera usage session loop (new iteration only when user changes camera)
        while True:
            if self.closing:
                return
            self.search_for_cameras_sig.emit()
            while self.current_camera_info is None:
                time.sleep(1)
                print("Waiting for cameras...")
                self.search_for_cameras_sig.emit()
            current_camera_port = copy.deepcopy(self.current_camera_info["port"])
            cap = cv2.VideoCapture(current_camera_port)

            try:
                while True:
                    if self.closing:
                        cap.release()

                        return
                    if current_camera_port != self.current_camera_info["port"]:
                        cap.release()

                        break
                    ret, frame = cap.read()
                    result = qr_decoder(frame)
                    if result is not None:
                        frame = result["image"]
                        data = result["data"].decode()
                        with self.text_lock:
                            if data != self.data:
                                self.data = data
                                self.update_text_sig.emit()
                                self.update_qr_code_sig.emit()
                                Thread(target=self.run_qr_actions, args=()).start()
                    self.camera_image = convert_cv_qt(
                        frame,
                        self.scanner_video_lbl.width() - 5,
                        self.scanner_video_lbl.height() - 5,
                    )
                    self.scanner_video_lbl.setPixmap(self.camera_image)
                    if not self.camera_initialised.is_set():
                        self.camera_initialised.set()
                        self.resizeEvent()

                    # code = cv2.waitKey(10)
                    # if code == ord('q'):
                    #     cap.release()
                    #
                    #     break
            except Exception as error:
                print(error)
                print(f"Error working with camera {self.current_camera_info['port']}")
                cap.release()

                self.scanner_video_lbl.clear()
                self.current_camera_info = None
                # self.search_for_cameras_sig.emit()
                # while self.current_camera_info is None:
                #     time.sleep(0.1)

                # self.search_for_cameras()

    def run_qr_actions(self):
        # COPY
        try:
            # pyperclip.copy(self.data)
            copy_to_clipboard(self.data)
        except Exception as e:
            print(e)

        # WIFI analysis
        try:
            elements = [e.split(":") for e in self.data.split(";")]
            if (
                len(elements) > 2
                and elements[0][0] == "WIFI"
                and elements[0][1] == "S"
                and elements[1][0] == "T"
                and elements[2][0] == "P"
            ):
                ssid = elements[0][2]
                auth_type = elements[1][1]
                password = elements[2][1]

                try:
                    connect_to_wifi_pywifi(ssid, auth_type, password)
                except Exception:
                    # handling permission denied error on linux
                    if platform.system() == "Linux":
                        connect_to_wifi_dbus(ssid, auth_type, password)
        except Exception as e:
            import traceback

            traceback.print_exc()
            print(e)

        try:
            if is_website(self.data):
                webbrowser.open_new_tab(self.data)
        except Exception as e:
            print(e)

    def generate_qr_code(self, text):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3,
            border=4,  # number of pixels is  this * box_size
        )
        qr.add_data(text)  # give QRCode object our text to encode
        qr.make(fit=True)  # generate QR code from our text
        # we would like our QR code to be about as high as the camera image displayed
        if self.camera_initialised.is_set():
            desired_height = (
                min(self.right_frame.height(), self.right_frame.width()) - 2
            )
        else:
            desired_height = 300
        # get the number of squares along an edge of the QR code
        qr_height_squares = len(qr.get_matrix())
        # calculate how many pixels should be used to display one square of the QR code
        qr.box_size = int((desired_height) / (qr_height_squares + qr.border))
        return qr.make_image()  # generate and return QR code image

    def save_qr_file(self, eventargs):
        """Saves the currently displayed QR-Code to a file,
        after opening a file dialog asking the user for the file path"""
        filepath, ok = QFileDialog.getSaveFileName(
            self, "Save QR Code", "", ("Images (*.png)")
        )
        if filepath:
            if filepath[-4:].lower() != ".png":
                print(filepath[-4:].lower())
                filepath += ".png"
            self.qr_code_lbl.pixmap().save(filepath)

    def closeEvent(self, event):
        self.closing = True
        event.accept()


def convert_cv_qt(cv_img, width, height):
    """Convert from an opencv image to QPixmap"""
    rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    convert_to_Qt_format = QtGui.QImage(
        rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888
    )
    p = convert_to_Qt_format.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio)
    return QPixmap.fromImage(p)


def is_website(text):
    return text.startswith("https://") or text.startswith("http://")


def get_camera_name(camera_index):
    if platform.system() == "Linux":
        return ""
    else:
        return ""


def main():
    app = QApplication(sys.argv)
    main = ScanGen()
    main.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
