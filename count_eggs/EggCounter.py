import sys
import os
import numpy as np
import time
import pandas as pd
import cv2

from PyQt5.QtWidgets import QApplication, QLabel, QCheckBox, QPushButton, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPointF
from HDF5VideoPlayer import HDF5VideoPlayerGUI

#mask_file = '/Users/ajaver/OneDrive - Imperial College London/optogenetics/Arantza/MaskedVideos/control_pulse/pkd2_5min_Ch1_11052017_121414.hdf5'
#mask_file = '/Users/ajaver/OneDrive - Imperial College London/aggregation/N2_1_Ch1_29062017_182108_comp3.hdf5'

MIN_DIST = 2
TIME_BTW_PRESS_RELEASE = 0.2

def _updateUI(ui):
    ui.horizontalLayout_6.removeWidget(ui.pushButton_h5groups)
    ui.pushButton_h5groups.deleteLater()
    ui.pushButton_h5groups = None

    ui.horizontalLayout_3.removeWidget(ui.doubleSpinBox_fps)
    ui.doubleSpinBox_fps.deleteLater()
    ui.doubleSpinBox_fps = None


    ui.horizontalLayout_3.removeWidget(ui.label_fps)
    ui.label_fps.deleteLater()
    ui.label_fps = None

    ui.horizontalLayout_3.removeWidget(ui.spinBox_step)
    ui.spinBox_step.deleteLater()
    ui.spinBox_step = None

    ui.horizontalLayout_3.removeWidget(ui.label_step)
    ui.label_step.deleteLater()
    ui.label_step = None


    ui.number_of_eggs = QLabel(ui.centralWidget)
    ui.horizontalLayout_3.addWidget(ui.number_of_eggs)
    ui.number_of_eggs.setText("0 Eggs")



    ui.show_prev = QCheckBox(ui.centralWidget)
    ui.horizontalLayout_3.addWidget(ui.show_prev)
    ui.show_prev.setText("Show Prev Eggs")
    ui.show_prev.setChecked(True)

    ui.copy_prev_b = QPushButton(ui.centralWidget)
    ui.horizontalLayout_3.addWidget(ui.copy_prev_b)
    ui.copy_prev_b.setText("Copy Prev")

    ui.copy_first_b = QPushButton(ui.centralWidget)
    ui.horizontalLayout_3.addWidget(ui.copy_first_b)
    ui.copy_first_b.setText("Copy First")

    ui.copy_earliest_b = QPushButton(ui.centralWidget)
    ui.horizontalLayout_3.addWidget(ui.copy_earliest_b)
    ui.copy_earliest_b.setText("Copy Earliest")

    ui.save_push_button = QPushButton(ui.centralWidget)
    ui.horizontalLayout_3.addWidget(ui.save_push_button)
    ui.save_push_button.setText("Save")

    return ui


class EggCounterGUI(HDF5VideoPlayerGUI):
    def __init__(self):
        super().__init__()

        self.ui = _updateUI(self.ui)
        self.is_new_eggs = False #flag to know if there are new egg events to save

        #default expected groups in the hdf5
        self.ui.comboBox_h5path.setItemText(1, "/mask")
        self.ui.comboBox_h5path.setItemText(0, "/full_data")

        self.mainImage._canvas.mouseDoubleClickEvent = self.doubleclick_event

        self.eggs = {}

        self.ui.save_push_button.clicked.connect(self.save_eggs_table)
        self.ui.show_prev.clicked.connect(self.updateImage)
        self.ui.copy_prev_b.clicked.connect(self.copy_prev_fun)
        self.ui.copy_first_b.clicked.connect(self.copy_first_fun)
        self.ui.copy_earliest_b.clicked.connect(self.copy_earliest_fun)

        self.mainImage.zoomFitInView()


    def updateVideoFile(self, vfilename):

        self._ask_saving()

        if vfilename.endswith('.hdf5'):
            super().updateVideoFile(vfilename)
        else:

            img = cv2.imread(vfilename, cv2.IMREAD_GRAYSCALE)

            if img is not None:

                self.ui.lineEdit_video.setText(self.vfilename)
                self.image_height = img.shape[0]
                self.image_width = img.shape[1]

                self.h5path = 'img'
                self.vfilename = vfilename
                self.tot_frames = 1

                self.ui.spinBox_frame.setMaximum(self.tot_frames - 1)
                self.ui.imageSlider.setMaximum(self.tot_frames - 1)

                self.frame_number = 0
                self.ui.spinBox_frame.setValue(self.frame_number)

                self.frame_img = img

            else:
                self.fid = None
                self.image_group = None
                QMessageBox.critical(
                    self,
                    '',
                    "The selected file is not a valid.",
                    QMessageBox.Ok)

        self.load_eggs_table()


        self.updateImage()


    def updateImage(self):
        if self.fid is not None:
            self.readCurrentFrame()
        else:
            self._normalizeImage()

        self.mainImage._canvas.setCursor(Qt.CrossCursor)

        if self.h5path in self.eggs:
            if self.frame_number in self.eggs[self.h5path]:
                current_list = self.eggs[self.h5path][self.frame_number]

                painter = QPainter()
                painter.begin(self.frame_qimg)
                pen = QPen()

                pen.setWidth(2)
                pen.setColor(Qt.red)
                painter.setPen(pen)
                painter.setBrush(Qt.red)
                for (x,y) in current_list:
                    #painter.drawEllipse(x,y, 1,1)
                    painter.drawPoint(x,y)
                painter.end()

                #set number of eggs eggs
                n_eggs_txt = "{} Eggs".format(len(self.eggs[self.h5path][self.frame_number]))
                self.ui.number_of_eggs.setText(n_eggs_txt)
            else:
                self.ui.number_of_eggs.setText("0 Eggs")

            prev_frame = self.frame_number-1
            if self.ui.show_prev.isChecked() and prev_frame in self.eggs[self.h5path]:
                prev_list = self.eggs[self.h5path][prev_frame]

                painter = QPainter()
                painter.begin(self.frame_qimg)
                pen = QPen()

                pen.setWidth(1)
                pen.setColor(Qt.blue)
                painter.setPen(pen)
                for (x,y) in prev_list:
                    painter.drawEllipse(x-3,y-3, 5,5)
                    #painter.drawPoint(x,y)
                painter.end()




        self.mainImage.setPixmap(self.frame_qimg)



    def doubleclick_event(self, event):
        self.m_x = event.pos().x()
        self.m_y = event.pos().y()
        self._add_coordinate(self.h5path, self.frame_number, self.m_x, self.m_y)
        self.updateImage()

    def _add_coordinate(self, h5path, frame_number, x, y, is_delete=True):
        self.is_new_eggs = True
        if not h5path in self.eggs:
            self.eggs[h5path] = {}

        if not frame_number in self.eggs[h5path]:
            self.eggs[h5path][frame_number] = []

        current_list = self.eggs[h5path][frame_number]

        if not current_list:
            #add the element if the list if empty
            current_list.append((x,y))
        else:
            V = np.array(current_list)
            dx = x - V[:, 0]
            dy = y - V[:, 1]

            rr = np.sqrt(dx*dx + dy*dy)

            ind = np.argmin(rr)
            if rr[ind] <= MIN_DIST:
                if is_delete:
                    #delete it if there was a click almost over a previous point
                    del current_list[ind]
            else:
                #otherwise add it
                current_list.append((x,y))

    def copy_prev_fun(self):
        prev_frame = self.frame_number -1
        if not prev_frame in self.eggs[self.h5path]:
            return
        else:
            for (x,y) in self.eggs[self.h5path][prev_frame]:
                self._add_coordinate(self.h5path, self.frame_number, x, y, is_delete=False)
        self.updateImage()

    def copy_first_fun(self):
        first_frame = 0
        if not first_frame in self.eggs[self.h5path]:
            return
        else:
            for (x,y) in self.eggs[self.h5path][first_frame]:
                self._add_coordinate(self.h5path, self.frame_number, x, y, is_delete=False)
        self.updateImage()

    def copy_earliest_fun(self):
        earliest_frame = min(self.eggs[self.h5path].keys())
        if not earliest_frame in self.eggs[self.h5path]:
            print('this should really not happen?')
            return
        else:
            for (x,y) in self.eggs[self.h5path][earliest_frame]:
                self._add_coordinate(self.h5path, self.frame_number, x, y, is_delete=False)
        self.updateImage()

    def save_eggs_table(self):
        if self.vfilename is not None:
            save_name = self._get_save_name(self.vfilename)
            df = self._eggs_to_table()
            df.to_csv(save_name, index=False)

    def _eggs_to_table(self):
        data = []
        for gg, frame_data in self.eggs.items():
            for frame, coords in frame_data.items():
                data += [(gg, frame, x,y) for x,y in coords]

        return pd.DataFrame(data, columns=['group_name', 'frame_number', 'x', 'y'])

    def _get_save_name(self, vfilename):
        return os.path.splitext(vfilename)[0] + '_eggs.csv'

    def load_eggs_table(self):
        self.eggs = {}
        self.is_new_eggs = False

        if self.vfilename is not None:
            save_name = self._get_save_name(self.vfilename)

            if os.path.exists(save_name):
                df = pd.read_csv(save_name)

                for gg, g_dat in df.groupby('group_name'):
                    if not gg in self.eggs:
                        self.eggs[gg] = {}
                    for frame_number, f_dat in g_dat.groupby('frame_number'):
                        self.eggs[gg][frame_number] = [(f['x'], f['y']) for i,f in f_dat.iterrows()]

    def _ask_saving(self):
        if self.is_new_eggs:
            quit_msg = "Do you want to save the current progress?"
            reply = QMessageBox.question(self,
                                                   'Message',
                                                   quit_msg,
                                                   QMessageBox.No | QMessageBox.Yes,
                                                   QMessageBox.Yes)


            if reply == QMessageBox.Yes:
                self.save_eggs_table()

    def closeEvent(self, event):
        self._ask_saving()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    ui = EggCounterGUI()
    ui.show()

    sys.exit(app.exec_())
