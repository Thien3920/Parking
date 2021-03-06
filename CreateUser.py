# Author: LE VAN THIEN
# Email: ngocthien3920@gmail.com
# Phone: 0329615785


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDesktopWidget

import cv2
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage

import shutil
from glob import glob
from pymongo import MongoClient
import os
import time
import Admin
import io
import PIL
import numpy as np
import cv2
import numpy as np

from insightface.model_zoo.retinaface import RetinaFace
from insightface.model_zoo.arcface_onnx import ArcFaceONNX



class Ui_MainWindow(object):
    def __init__(self):
        self.record = None
        self.cap = None
        self.timer = None
        # self.StateCapture = False 
        self.StateRegister = None

        #Database
        uri = "mongodb://localhost:27017/"
        Client = MongoClient(uri)
        DataBase = Client["ParkingManagement"]

        #Face
        self.image = None
        self.FaceImage = None
        self.bb = None
        self.codes = []
        self.files = []
        self.idx = 0

        #Information
        self.Name = None
        self.UserName = None
        self.Account = None
        self.PassWord = None
        self.ConfirmPassWord = None
        self.CustomerDBCollection = DataBase["Customer"]
        self.StaffCollection = DataBase["Staff"]
        ## Model
        self.detector = RetinaFace(model_file='/home/thien/.insightface/models/buffalo_l/det_10g.onnx')
        self.recognizer = ArcFaceONNX(model_file='/home/thien/.insightface/models/buffalo_l/w600k_r50.onnx')

    def StartVideo(self):
        if self.record == None or self.record == "STOP":
            self.default()
            self.record ="RUNNING"
            self.cap = cv2.VideoCapture(0)
            self.timer = QTimer()
            self.timer.timeout.connect(self.ShowVideo)
            self.timer.start(1)
            self.StartButton.setText("Finish")

        elif self.record =="RUNNING":
            self.record = "STOP"
            self.CameraLargeLabel.setPixmap(QtGui.QPixmap("./icons/face-scan.png"))
            self.timer.stop()
            self.cap.release()
            self.StartButton.setText("Start")

    def ShowVideo(self):
        ret, self.image = self.cap.read()
        self.image2 = self.image.copy()
        self.bboxes, self.kpss = self.detector.detect(self.image, input_size =(640, 640))
        self.FaceImage = self.drawbox()
        # self.CheckFace()
        self.LoadImage(self.image,self.CameraLargeLabel)
    
    def drawbox(self):
        if len(self.bboxes)> 0:
            xmin,ymin,xmax,ymax,score = [int(_) for _ in self.bboxes[0]][:5]
            FaceImage = self.image[ymin:ymax,xmin:xmax]
            cv2.rectangle(self.image, (xmin, ymin ), (xmax ,ymax), (0,255,0), 1, cv2.LINE_AA)
            
            return FaceImage

            # cv2.putText(self.image, "OK", (50, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL,1, (0, 255, 0), 2, cv2.LINE_AA)
            # return 0

    
    # def CheckFace(self):
    #     if len(self.bboxes)> 0:
    #         xmin,ymin,xmax,ymax,score = [int(_) for _ in bboxes[0]][:5]
    #         cv2.rectangle(self.image, (xmin, ymin ), (xmax ,ymax), (0,255,0), 1, cv2.LINE_AA)
    #         self.StateCapture = True
    #         cv2.putText(self.image, "OK", (50, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL,1, (0, 255, 0), 2, cv2.LINE_AA)
    #         return 0
    #     cv2.putText(self.image, "No landmasks", (50, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL,
    #                 1, (0, 0, 255), 2, cv2.LINE_AA)
    #     self.StateCapture = False
        

    def LoadImage(self, image,Label):
        frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        Label.setPixmap(QtGui.QPixmap.fromImage(image))
    
    def Capture(self):
        if self.timer != None:
            xtime = int(float(time.time()))
            cv2.imwrite("./images/image_{}.jpg".format(xtime),self.image2)
            self.ListImage()
    
    def DeletePic(self):
        if len(self.files)>0:
            print(len(self.files))
            self.idx = len(self.files)-1
            print(self.idx)
            self.files.pop(self.idx)
            if self.idx ==0:
                path = "icons/face-scan.png"
                I = cv2.imread(path)
                self.LoadImage(I, self.CameraSmallLabel)
            else:
                self.BackPic()

    def BackPic(self):
        if len(self.files) > 0:
            if self.idx >0:
                self.idx -=1
            else:
                self.idx = len(self.files) -1

            self.ShowImage(self.idx)
    def NextPic(self):
        if len(self.files) > 0:
            if self.idx < len(self.files) -1:
                self.idx+=1
            else:
                self.idx = 0
            self.ShowImage(self.idx)
    
    def ShowImage(self,idx):
   
        if len(self.files) > 0:
            path = self.files[idx]
            image = cv2.imread(path)
            bboxes, kpss = self.detector.detect(image, input_size =(640, 640))
      
            xmin,ymin,xmax,ymax,score = [int(_) for _ in bboxes[0]][:5]
            image = image[ymin:ymax,xmin:xmax]

        else:
            path = "./icons/face-scan-small.png"
            image = cv2.imread(path)
        
        self.LoadImage(image,self.CameraSmallLabel)
    
    def ListImage(self):
        list = glob('./images' + '/*.jpg') + glob('./images' + '/*.png')
        list.sort()
        self.files=list
        self.idx = len(self.files)
        self.ShowImage(self.idx -1)
    
    def default(self):
        if os.path.exists('./images'):
            shutil.rmtree('./images')
        os.makedirs('./images')
        
        self.image = None
        self.codes = []
        self.files = []
        self.idx = 0
        self.files = []
        self.StateRegister = None
        self.Name = None
        self.UserName = None
        self.PassWord = None
        self.code = None
        self.NotifyMainLabel.setText("")
        self.CameraSmallLabel.setPixmap(QtGui.QPixmap("./icons/face-scan-small.png"))
        self.Notify1Label.setText("")
        self.Notify2Label.setText("")
        self.Notify3Label.setText("")
        self.Notify4Label.setText("")
        self.NotifyMainLabel.setText("")
        self.NameLine.clear()
        self.UsernameLine.clear()
        self.PasswordLine.clear()
        self.ConfirmPasswordLine.clear()

    
    def Back(self):
        if self.timer !=None and self.cap!=None:
            self.timer.stop()
            self.cap.release()
        self.AdminWindow = QtWidgets.QMainWindow()
        self.AdminUi = Admin.Ui_AdminWindow()
        self.AdminUi.setupUi(self.AdminWindow)
        self.AdminWindow.show()
        self.MainWindow.close()
    
    

    def Register(self):  
        if len(self.files):
            if self.CheckName():
                if self.CheckUserName()==True:
                    if self.CheckPassWord():
                        if self.CheckConfirmPassWord():
                            self.Notify4Label.setText(u'\u2713')
                            self.NotifyMainLabel.setText("Registration succesful \u2713")
                            codes = []
                            Images = []
                            for ImageName in self.files:
                                image = cv2.imread(ImageName)
                                im = PIL.Image.fromarray(np.uint8(image))
                                image_bytes = io.BytesIO()
                                im.save(image_bytes, format='JPEG')
                                Images.append(image_bytes.getvalue())
                                bboxes, kpss = self.detector.detect(image, input_size =(640, 640))
                                if len(bboxes)> 0:
                                    code = self.recognizer.get(image, kpss[0])
                                    codes.append(code.tolist())
                                
                            self.StaffCollection.insert_one(
                                {"Name": self.Name, "UserName": self.UserName, "PassWord": self.PassWord,
                                    "Code": codes,"Images":Images})
                            self.NotifyMainLabel.setText("Successfully Registed!")

                        else:
                            self.NotifyMainLabel.setText("Password does not match")
                    else:
                        self.NotifyMainLabel.setText("please enter password")

                elif self.CheckUserName()== "Empty":
                    self.NotifyMainLabel.setText("please enter Username")
                else:
                    self.NotifyMainLabel.setText("that username is taken")

            else:
                self.NotifyMainLabel.setText("Please enter Name")

        else:
            self.NotifyMainLabel.setText("No Face!")


    #Press events
    def PressName(self, event):
        self.Notify1Label.setText("")
        self.Notify2Label.setText("")
        self.Notify3Label.setText("")
        self.Notify4Label.setText("")
        self.NotifyMainLabel.setText("")

    def PressUserName(self, event):
        self.Notify2Label.setText("")
        self.Notify3Label.setText("")
        self.Notify4Label.setText("")
        self.NotifyMainLabel.setText("")
        if self.CheckName():
            self.Notify1Label.setText(u'\u2713')
        else:
            self.Notify1Label.setText("Please Enter Your Name!")

    def PressPassWord(self, event):
        self.Notify3Label.setText("")
        self.Notify4Label.setText("")
        self.NotifyMainLabel.setText("")

        if self.CheckUserName() == "Empty":
            self.Notify2Label.setText("Please Enter User Name")
        elif self.CheckUserName() == True:
            self.Notify2Label.setText(u'\u2713')
        else:
            self.Notify2Label.setText("exist")

    def PressConfirmPassWord(self, event):
        self.Notify3Label.setText("")
        self.Notify4Label.setText("")
        self.NotifyMainLabel.setText("")
        if self.CheckPassWord():
            if len(self.PassWord) >= 6:
                self.Notify3Label.setText(u'\u2713')
            else:
                self.Notify3Label.setText("Password too short")
        else:
            self.Notify3Label.setText("Please Enter PassWord")

    def CheckConfirmPassWord(self):
        self.CFPassWord = self.ConfirmPasswordLine.text()
        if self.CFPassWord == self.PassWord:
            return True
        else:
            return False

    def CheckPassWord(self):
        self.PassWord = self.PasswordLine.text()
        if self.PassWord == None or self.PassWord == "":
            return False
        else:
            return True

    def CheckUserName(self):
        self.UserName = self.UsernameLine.text()
        if self.UserName == None or self.UserName == "":
            return "Empty"
        else:
            for User in self.StaffCollection.find():
                if self.UserName == User["UserName"]:
                    return False
            return True

    def CheckName(self):
        self.Name = self.NameLine.text()
        if self.Name == None or self.Name == "":
            return False
        else:
            return True


    def Center(self,widget):
        qr = widget.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        widget.move(qr.topLeft())
  
        
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        self.Center(MainWindow)
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1262, 947)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setStyleSheet("background-color: rgb(12, 11, 42);\n"
"color: rgb(255, 255, 255);")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_2 = QtWidgets.QFrame(self.frame)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setContentsMargins(-1, 0, 11, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frame_5 = QtWidgets.QFrame(self.frame_2)
        self.frame_5.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.BackButton = QtWidgets.QPushButton(self.frame_5)
        self.BackButton.setStyleSheet("QPushButton {\n"
"border-color: rgb(255,255,255);\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 5px;\n"
"color: rgb(255, 255, 255);\n"
"font: 75 15pt \"Ubuntu Condensed\";\n"
"padding: 0 10px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    background-color: rgb(122, 155, 153);\n"
"}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./icons/chevrons-left.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BackButton.setIcon(icon)
        self.BackButton.setIconSize(QtCore.QSize(30, 30))
        self.BackButton.setObjectName("BackButton")
        self.horizontalLayout_5.addWidget(self.BackButton)
        self.horizontalLayout_2.addWidget(self.frame_5, 0, QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.frame_6 = QtWidgets.QFrame(self.frame_2)
        self.frame_6.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(self.frame_6)
        self.label.setStyleSheet("font: 75 27pt \"Ubuntu Condensed\";\n"
"")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.horizontalLayout_2.addWidget(self.frame_6, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.frame_7 = QtWidgets.QFrame(self.frame_2)
        self.frame_7.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_7)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.ExitButton = QtWidgets.QPushButton(self.frame_7)
        self.ExitButton.setStyleSheet("\n"
"QPushButton {\n"
"border-color: rgb(255,255,255);\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 5px;\n"
"color: rgb(255, 255, 255);\n"
"font: 75 15pt \"Ubuntu Condensed\";\n"
"padding: 0 10px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    background-color: rgb(122, 155, 153);\n"
"}")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("./icons/power.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ExitButton.setIcon(icon1)
        self.ExitButton.setIconSize(QtCore.QSize(30, 30))
        self.ExitButton.setObjectName("ExitButton")
        self.horizontalLayout_4.addWidget(self.ExitButton)
        self.horizontalLayout_2.addWidget(self.frame_7, 0, QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        self.verticalLayout.addWidget(self.frame_2, 0, QtCore.Qt.AlignTop)
        self.frame_3 = QtWidgets.QFrame(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.frame_10 = QtWidgets.QFrame(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_10.sizePolicy().hasHeightForWidth())
        self.frame_10.setSizePolicy(sizePolicy)
        self.frame_10.setStyleSheet("")
        self.frame_10.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_10.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_10.setObjectName("frame_10")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_10)
        self.verticalLayout_3.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_3.setSpacing(11)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame_12 = QtWidgets.QFrame(self.frame_10)
        self.frame_12.setStyleSheet("border:none;")
        self.frame_12.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_12.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_12.setObjectName("frame_12")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.frame_12)
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_3 = QtWidgets.QLabel(self.frame_12)
        self.label_3.setStyleSheet("font: 75 20pt \"Ubuntu Condensed\";")
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_9.addWidget(self.label_3)
        self.verticalLayout_3.addWidget(self.frame_12, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.frame_17 = QtWidgets.QFrame(self.frame_10)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_17.sizePolicy().hasHeightForWidth())
        self.frame_17.setSizePolicy(sizePolicy)
        self.frame_17.setStyleSheet("border-color: rgb(255,255,255);\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 8px;\n"
"color: rgb(255, 255, 255);\n"
"")
        self.frame_17.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_17.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_17.setObjectName("frame_17")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frame_17)
        self.verticalLayout_5.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_5.setSpacing(11)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.frame_14 = QtWidgets.QFrame(self.frame_17)
        self.frame_14.setStyleSheet("border:none;")
        self.frame_14.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_14.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_14.setObjectName("frame_14")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.frame_14)
        self.verticalLayout_7.setContentsMargins(0, 11, 0, 11)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.CameraLargeLabel = QtWidgets.QLabel(self.frame_14)
        self.CameraLargeLabel.setMaximumSize(QtCore.QSize(400, 400))
        self.CameraLargeLabel.setStyleSheet("border-color: rgb(255,255,255);\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 8px;\n"
"color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 255, 255);\n"
"")
        self.CameraLargeLabel.setText("")
        self.CameraLargeLabel.setPixmap(QtGui.QPixmap("./icons/face-scan.png"))
        self.CameraLargeLabel.setScaledContents(True)
        self.CameraLargeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.CameraLargeLabel.setObjectName("CameraLargeLabel")
        self.verticalLayout_7.addWidget(self.CameraLargeLabel)
        self.verticalLayout_5.addWidget(self.frame_14, 0, QtCore.Qt.AlignHCenter)
        self.frame_15 = QtWidgets.QFrame(self.frame_17)
        self.frame_15.setStyleSheet("border:none;")
        self.frame_15.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_15.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_15.setObjectName("frame_15")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout(self.frame_15)
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_13.setSpacing(0)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.frame_26 = QtWidgets.QFrame(self.frame_15)
        self.frame_26.setStyleSheet("border:none;")
        self.frame_26.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_26.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_26.setObjectName("frame_26")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout(self.frame_26)
        self.horizontalLayout_14.setContentsMargins(11, 0, 40, 0)
        self.horizontalLayout_14.setSpacing(0)
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.StartButton = QtWidgets.QPushButton(self.frame_26)
        self.StartButton.setMinimumSize(QtCore.QSize(100, 0))
        self.StartButton.setStyleSheet("QPushButton {\n"
"border-color: rgb(255,255,255);\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 5px;\n"
"color: rgb(255, 255, 255);\n"
"font: 75 15pt \"Ubuntu Condensed\";\n"
"padding: 0 10px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    background-color: rgb(122, 155, 153);\n"
"}")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("./icons/play-circle.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.StartButton.setIcon(icon2)
        self.StartButton.setIconSize(QtCore.QSize(30, 30))
        self.StartButton.setObjectName("StartButton")
        self.horizontalLayout_14.addWidget(self.StartButton)
        self.horizontalLayout_13.addWidget(self.frame_26, 0, QtCore.Qt.AlignRight)
        self.frame_28 = QtWidgets.QFrame(self.frame_15)
        self.frame_28.setStyleSheet("border:none;")
        self.frame_28.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_28.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_28.setObjectName("frame_28")
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout(self.frame_28)
        self.horizontalLayout_16.setContentsMargins(40, 0, 0, 0)
        self.horizontalLayout_16.setSpacing(0)
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.CaptureButton = QtWidgets.QPushButton(self.frame_28)
        self.CaptureButton.setMinimumSize(QtCore.QSize(100, 0))
        self.CaptureButton.setStyleSheet("QPushButton {\n"
"border-color: rgb(255,255,255);\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 5px;\n"
"color: rgb(255, 255, 255);\n"
"font: 75 15pt \"Ubuntu Condensed\";\n"
"padding: 0 10px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    background-color: rgb(122, 155, 153);\n"
"}")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("./icons/camera.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.CaptureButton.setIcon(icon3)
        self.CaptureButton.setIconSize(QtCore.QSize(30, 30))
        self.CaptureButton.setObjectName("CaptureButton")
        self.horizontalLayout_16.addWidget(self.CaptureButton)
        self.horizontalLayout_13.addWidget(self.frame_28, 0, QtCore.Qt.AlignLeft)
        self.verticalLayout_5.addWidget(self.frame_15, 0, QtCore.Qt.AlignTop)
        self.verticalLayout_3.addWidget(self.frame_17)
        self.frame_13 = QtWidgets.QFrame(self.frame_10)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_13.sizePolicy().hasHeightForWidth())
        self.frame_13.setSizePolicy(sizePolicy)
        self.frame_13.setStyleSheet("border-color: rgb(255,255,255);\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 8px;\n"
"color: rgb(255, 255, 255);\n"
"")
        self.frame_13.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_13.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_13.setObjectName("frame_13")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame_13)
        self.verticalLayout_6.setContentsMargins(0, 11, 0, 11)
        self.verticalLayout_6.setSpacing(11)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.frame_24 = QtWidgets.QFrame(self.frame_13)
        self.frame_24.setStyleSheet("border:none;")
        self.frame_24.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_24.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_24.setObjectName("frame_24")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.frame_24)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.CameraSmallLabel = QtWidgets.QLabel(self.frame_24)
        self.CameraSmallLabel.setMaximumSize(QtCore.QSize(204, 204))
        self.CameraSmallLabel.setStyleSheet("border-color: rgb(255,255,255);\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 8px;\n"
"color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 255, 255);")
        self.CameraSmallLabel.setText("")
        self.CameraSmallLabel.setPixmap(QtGui.QPixmap("./icons/face-scan-small.png"))
        self.CameraSmallLabel.setScaledContents(True)
        self.CameraSmallLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.CameraSmallLabel.setObjectName("CameraSmallLabel")
        self.verticalLayout_8.addWidget(self.CameraSmallLabel)
        self.verticalLayout_6.addWidget(self.frame_24, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.frame_25 = QtWidgets.QFrame(self.frame_13)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_25.sizePolicy().hasHeightForWidth())
        self.frame_25.setSizePolicy(sizePolicy)
        self.frame_25.setStyleSheet("border:none;")
        self.frame_25.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_25.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_25.setObjectName("frame_25")
        self.horizontalLayout_28 = QtWidgets.QHBoxLayout(self.frame_25)
        self.horizontalLayout_28.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_28.setSpacing(0)
        self.horizontalLayout_28.setObjectName("horizontalLayout_28")
        self.frame_36 = QtWidgets.QFrame(self.frame_25)
        self.frame_36.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_36.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_36.setObjectName("frame_36")
        self.horizontalLayout_29 = QtWidgets.QHBoxLayout(self.frame_36)
        self.horizontalLayout_29.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_29.setSpacing(0)
        self.horizontalLayout_29.setObjectName("horizontalLayout_29")
        self.BackPicButton = QtWidgets.QPushButton(self.frame_36)
        self.BackPicButton.setMinimumSize(QtCore.QSize(100, 0))
        self.BackPicButton.setStyleSheet("QPushButton {\n"
"border-color: rgb(255,255,255);\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 5px;\n"
"color: rgb(255, 255, 255);\n"
"font: 75 15pt \"Ubuntu Condensed\";\n"
"padding: 0 10px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    background-color: rgb(122, 155, 153);\n"
"}")
        self.BackPicButton.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("./icons/skip-back.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BackPicButton.setIcon(icon4)
        self.BackPicButton.setIconSize(QtCore.QSize(30, 30))
        self.BackPicButton.setObjectName("BackPicButton")
        self.horizontalLayout_29.addWidget(self.BackPicButton)
        self.horizontalLayout_28.addWidget(self.frame_36, 0, QtCore.Qt.AlignRight)
        self.frame_37 = QtWidgets.QFrame(self.frame_25)
        self.frame_37.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_37.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_37.setObjectName("frame_37")
        self.horizontalLayout_30 = QtWidgets.QHBoxLayout(self.frame_37)
        self.horizontalLayout_30.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_30.setSpacing(0)
        self.horizontalLayout_30.setObjectName("horizontalLayout_30")
        self.DeletePicButton = QtWidgets.QPushButton(self.frame_37)
        self.DeletePicButton.setMinimumSize(QtCore.QSize(100, 0))
        self.DeletePicButton.setStyleSheet("QPushButton {\n"
"border-color: rgb(255,255,255);\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 5px;\n"
"color: rgb(255, 255, 255);\n"
"font: 75 15pt \"Ubuntu Condensed\";\n"
"padding: 0 10px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    background-color: rgb(122, 155, 153);\n"
"}")
        self.DeletePicButton.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("./icons/trash-2.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.DeletePicButton.setIcon(icon5)
        self.DeletePicButton.setIconSize(QtCore.QSize(30, 30))
        self.DeletePicButton.setObjectName("DeletePicButton")
        self.horizontalLayout_30.addWidget(self.DeletePicButton)
        self.horizontalLayout_28.addWidget(self.frame_37, 0, QtCore.Qt.AlignHCenter)
        self.frame_38 = QtWidgets.QFrame(self.frame_25)
        self.frame_38.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_38.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_38.setObjectName("frame_38")
        self.horizontalLayout_31 = QtWidgets.QHBoxLayout(self.frame_38)
        self.horizontalLayout_31.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_31.setSpacing(0)
        self.horizontalLayout_31.setObjectName("horizontalLayout_31")
        self.NextPicButton = QtWidgets.QPushButton(self.frame_38)
        self.NextPicButton.setMinimumSize(QtCore.QSize(100, 0))
        self.NextPicButton.setStyleSheet("QPushButton {\n"
"border-color: rgb(255,255,255);\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 5px;\n"
"color: rgb(255, 255, 255);\n"
"font: 75 15pt \"Ubuntu Condensed\";\n"
"padding: 0 10px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    background-color: rgb(122, 155, 153);\n"
"}")
        self.NextPicButton.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("./icons/skip-forward.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.NextPicButton.setIcon(icon6)
        self.NextPicButton.setIconSize(QtCore.QSize(30, 30))
        self.NextPicButton.setObjectName("NextPicButton")
        self.horizontalLayout_31.addWidget(self.NextPicButton)
        self.horizontalLayout_28.addWidget(self.frame_38, 0, QtCore.Qt.AlignLeft)
        self.verticalLayout_6.addWidget(self.frame_25, 0, QtCore.Qt.AlignBottom)
        self.verticalLayout_3.addWidget(self.frame_13, 0, QtCore.Qt.AlignBottom)
        self.horizontalLayout_8.addWidget(self.frame_10)
        self.frame_11 = QtWidgets.QFrame(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_11.sizePolicy().hasHeightForWidth())
        self.frame_11.setSizePolicy(sizePolicy)
        self.frame_11.setStyleSheet("")
        self.frame_11.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_11.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_11.setObjectName("frame_11")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_11)
        self.verticalLayout_2.setContentsMargins(-1, 3, -1, -1)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame_4 = QtWidgets.QFrame(self.frame_11)
        self.frame_4.setStyleSheet("border:none;")
        self.frame_4.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.frame_4)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.frame_18 = QtWidgets.QFrame(self.frame_4)
        self.frame_18.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_18.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_18.setObjectName("frame_18")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.frame_18)
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_4 = QtWidgets.QLabel(self.frame_18)
        self.label_4.setStyleSheet("font: 75 20pt \"Ubuntu Condensed\";")
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_10.addWidget(self.label_4)
        self.verticalLayout_9.addWidget(self.frame_18, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.verticalLayout_2.addWidget(self.frame_4, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.frame_8 = QtWidgets.QFrame(self.frame_11)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_8.sizePolicy().hasHeightForWidth())
        self.frame_8.setSizePolicy(sizePolicy)
        self.frame_8.setMinimumSize(QtCore.QSize(672, 500))
        self.frame_8.setStyleSheet("border-color: rgb(255,255,255);\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 8px;\n"
"color: rgb(255, 255, 255);\n"
"\n"
"")
        self.frame_8.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_8.setObjectName("frame_8")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_8)
        self.verticalLayout_4.setContentsMargins(0, 11, 0, 11)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.frame_19 = QtWidgets.QFrame(self.frame_8)
        self.frame_19.setStyleSheet("border:none;\n"
"")
        self.frame_19.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_19.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_19.setObjectName("frame_19")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.frame_19)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.frame_27 = QtWidgets.QFrame(self.frame_19)
        self.frame_27.setMinimumSize(QtCore.QSize(170, 0))
        self.frame_27.setStyleSheet("border:none;")
        self.frame_27.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_27.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_27.setObjectName("frame_27")
        self.horizontalLayout_20 = QtWidgets.QHBoxLayout(self.frame_27)
        self.horizontalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_20.setSpacing(0)
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.label_9 = QtWidgets.QLabel(self.frame_27)
        self.label_9.setStyleSheet("font: 75 15pt \"Ubuntu Condensed\";")
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_20.addWidget(self.label_9)
        self.horizontalLayout_7.addWidget(self.frame_27, 0, QtCore.Qt.AlignLeft)
        self.frame_29 = QtWidgets.QFrame(self.frame_19)
        self.frame_29.setMinimumSize(QtCore.QSize(200, 91))
        self.frame_29.setStyleSheet("border:none;")
        self.frame_29.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_29.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_29.setObjectName("frame_29")
        self.horizontalLayout_24 = QtWidgets.QHBoxLayout(self.frame_29)
        self.horizontalLayout_24.setObjectName("horizontalLayout_24")
        self.NameLine = QtWidgets.QLineEdit(self.frame_29)
        self.NameLine.setMinimumSize(QtCore.QSize(0, 40))
        self.NameLine.setStyleSheet("border-color: rgb(255,255,255);\n"
"font: 75 15pt \"Ubuntu Condensed\";\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 8px;\n"
"color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);")
        self.NameLine.setText("")
        self.NameLine.setObjectName("NameLine")
        self.horizontalLayout_24.addWidget(self.NameLine)
        self.horizontalLayout_7.addWidget(self.frame_29, 0, QtCore.Qt.AlignLeft)
        self.frame_21 = QtWidgets.QFrame(self.frame_19)
        self.frame_21.setMinimumSize(QtCore.QSize(189, 74))
        self.frame_21.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_21.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_21.setObjectName("frame_21")
        self.horizontalLayout_32 = QtWidgets.QHBoxLayout(self.frame_21)
        self.horizontalLayout_32.setObjectName("horizontalLayout_32")
        self.Notify1Label = QtWidgets.QLabel(self.frame_21)
        self.Notify1Label.setStyleSheet("color: rgb(239, 41, 41);")
        self.Notify1Label.setObjectName("Notify1Label")
        self.horizontalLayout_32.addWidget(self.Notify1Label)
        self.horizontalLayout_7.addWidget(self.frame_21)
        self.verticalLayout_4.addWidget(self.frame_19)
        self.frame_22 = QtWidgets.QFrame(self.frame_8)
        self.frame_22.setStyleSheet("border:none;\n"
"")
        self.frame_22.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_22.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_22.setObjectName("frame_22")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout(self.frame_22)
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.frame_30 = QtWidgets.QFrame(self.frame_22)
        self.frame_30.setMinimumSize(QtCore.QSize(170, 0))
        self.frame_30.setStyleSheet("border:none;")
        self.frame_30.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_30.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_30.setObjectName("frame_30")
        self.horizontalLayout_21 = QtWidgets.QHBoxLayout(self.frame_30)
        self.horizontalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_21.setSpacing(0)
        self.horizontalLayout_21.setObjectName("horizontalLayout_21")
        self.label_10 = QtWidgets.QLabel(self.frame_30)
        self.label_10.setStyleSheet("font: 75 15pt \"Ubuntu Condensed\";")
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_21.addWidget(self.label_10)
        self.horizontalLayout_12.addWidget(self.frame_30, 0, QtCore.Qt.AlignLeft)
        self.frame_31 = QtWidgets.QFrame(self.frame_22)
        self.frame_31.setMinimumSize(QtCore.QSize(200, 91))
        self.frame_31.setStyleSheet("border:none;")
        self.frame_31.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_31.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_31.setObjectName("frame_31")
        self.horizontalLayout_25 = QtWidgets.QHBoxLayout(self.frame_31)
        self.horizontalLayout_25.setObjectName("horizontalLayout_25")
        self.UsernameLine = QtWidgets.QLineEdit(self.frame_31)
        self.UsernameLine.setMinimumSize(QtCore.QSize(0, 40))
        self.UsernameLine.setStyleSheet("border-color: rgb(255,255,255);\n"
"font: 75 15pt \"Ubuntu Condensed\";\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 8px;\n"
"color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);")
        self.UsernameLine.setObjectName("UsernameLine")
        self.horizontalLayout_25.addWidget(self.UsernameLine)
        self.horizontalLayout_12.addWidget(self.frame_31, 0, QtCore.Qt.AlignLeft)
        self.frame_39 = QtWidgets.QFrame(self.frame_22)
        self.frame_39.setMinimumSize(QtCore.QSize(189, 74))
        self.frame_39.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_39.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_39.setObjectName("frame_39")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(self.frame_39)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.Notify2Label = QtWidgets.QLabel(self.frame_39)
        self.Notify2Label.setMinimumSize(QtCore.QSize(189, 74))
        self.Notify2Label.setStyleSheet("color: rgb(239, 41, 41);")
        self.Notify2Label.setObjectName("Notify2Label")
        self.horizontalLayout_11.addWidget(self.Notify2Label)
        self.horizontalLayout_12.addWidget(self.frame_39)
        self.verticalLayout_4.addWidget(self.frame_22)
        self.frame_20 = QtWidgets.QFrame(self.frame_8)
        self.frame_20.setStyleSheet("border:none;\n"
"")
        self.frame_20.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_20.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_20.setObjectName("frame_20")
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout(self.frame_20)
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.frame_32 = QtWidgets.QFrame(self.frame_20)
        self.frame_32.setMinimumSize(QtCore.QSize(170, 0))
        self.frame_32.setStyleSheet("border:none;")
        self.frame_32.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_32.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_32.setObjectName("frame_32")
        self.horizontalLayout_22 = QtWidgets.QHBoxLayout(self.frame_32)
        self.horizontalLayout_22.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_22.setSpacing(0)
        self.horizontalLayout_22.setObjectName("horizontalLayout_22")
        self.label_11 = QtWidgets.QLabel(self.frame_32)
        self.label_11.setStyleSheet("font: 75 15pt \"Ubuntu Condensed\";")
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_22.addWidget(self.label_11)
        self.horizontalLayout_17.addWidget(self.frame_32, 0, QtCore.Qt.AlignLeft)
        self.frame_33 = QtWidgets.QFrame(self.frame_20)
        self.frame_33.setMinimumSize(QtCore.QSize(200, 91))
        self.frame_33.setStyleSheet("border:none;")
        self.frame_33.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_33.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_33.setObjectName("frame_33")
        self.horizontalLayout_26 = QtWidgets.QHBoxLayout(self.frame_33)
        self.horizontalLayout_26.setObjectName("horizontalLayout_26")
        self.PasswordLine = QtWidgets.QLineEdit(self.frame_33)
        self.PasswordLine.setMinimumSize(QtCore.QSize(0, 40))
        self.PasswordLine.setStyleSheet("border-color: rgb(255,255,255);\n"
"font: 75 15pt \"Ubuntu Condensed\";\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 8px;\n"
"color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);")
        self.PasswordLine.setEchoMode(QtWidgets.QLineEdit.Password)
        self.PasswordLine.setObjectName("PasswordLine")
        self.horizontalLayout_26.addWidget(self.PasswordLine)
        self.horizontalLayout_17.addWidget(self.frame_33, 0, QtCore.Qt.AlignLeft)
        self.frame_40 = QtWidgets.QFrame(self.frame_20)
        self.frame_40.setMinimumSize(QtCore.QSize(189, 74))
        self.frame_40.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_40.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_40.setObjectName("frame_40")
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout(self.frame_40)
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.Notify3Label = QtWidgets.QLabel(self.frame_40)
        self.Notify3Label.setStyleSheet("color: rgb(239, 41, 41);")
        self.Notify3Label.setObjectName("Notify3Label")
        self.horizontalLayout_15.addWidget(self.Notify3Label)
        self.horizontalLayout_17.addWidget(self.frame_40)
        self.verticalLayout_4.addWidget(self.frame_20)
        self.frame_23 = QtWidgets.QFrame(self.frame_8)
        self.frame_23.setStyleSheet("border:none;\n"
"")
        self.frame_23.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_23.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_23.setObjectName("frame_23")
        self.horizontalLayout_19 = QtWidgets.QHBoxLayout(self.frame_23)
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.frame_34 = QtWidgets.QFrame(self.frame_23)
        self.frame_34.setMinimumSize(QtCore.QSize(170, 0))
        self.frame_34.setStyleSheet("border:none;")
        self.frame_34.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_34.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_34.setObjectName("frame_34")
        self.horizontalLayout_23 = QtWidgets.QHBoxLayout(self.frame_34)
        self.horizontalLayout_23.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_23.setSpacing(0)
        self.horizontalLayout_23.setObjectName("horizontalLayout_23")
        self.label_12 = QtWidgets.QLabel(self.frame_34)
        self.label_12.setMinimumSize(QtCore.QSize(160, 0))
        self.label_12.setStyleSheet("font: 75 15pt \"Ubuntu Condensed\";")
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_23.addWidget(self.label_12)
        self.horizontalLayout_19.addWidget(self.frame_34, 0, QtCore.Qt.AlignLeft)
        self.frame_35 = QtWidgets.QFrame(self.frame_23)
        self.frame_35.setMinimumSize(QtCore.QSize(200, 91))
        self.frame_35.setStyleSheet("border:none;")
        self.frame_35.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_35.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_35.setObjectName("frame_35")
        self.horizontalLayout_27 = QtWidgets.QHBoxLayout(self.frame_35)
        self.horizontalLayout_27.setObjectName("horizontalLayout_27")
        self.ConfirmPasswordLine = QtWidgets.QLineEdit(self.frame_35)
        self.ConfirmPasswordLine.setMinimumSize(QtCore.QSize(0, 40))
        self.ConfirmPasswordLine.setStyleSheet("border-color: rgb(255,255,255);\n"
"font: 75 15pt \"Ubuntu Condensed\";\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 8px;\n"
"color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);")
        self.ConfirmPasswordLine.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ConfirmPasswordLine.setObjectName("ConfirmPasswordLine")
        self.horizontalLayout_27.addWidget(self.ConfirmPasswordLine)
        self.horizontalLayout_19.addWidget(self.frame_35, 0, QtCore.Qt.AlignLeft)
        self.frame_41 = QtWidgets.QFrame(self.frame_23)
        self.frame_41.setMinimumSize(QtCore.QSize(189, 74))
        self.frame_41.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_41.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_41.setObjectName("frame_41")
        self.horizontalLayout_18 = QtWidgets.QHBoxLayout(self.frame_41)
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.Notify4Label = QtWidgets.QLabel(self.frame_41)
        self.Notify4Label.setStyleSheet("color: rgb(239, 41, 41);")
        self.Notify4Label.setObjectName("Notify4Label")
        self.horizontalLayout_18.addWidget(self.Notify4Label)
        self.horizontalLayout_19.addWidget(self.frame_41)
        self.verticalLayout_4.addWidget(self.frame_23)
        self.verticalLayout_2.addWidget(self.frame_8, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.frame_9 = QtWidgets.QFrame(self.frame_11)
        self.frame_9.setStyleSheet("border:none;")
        self.frame_9.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_9.setObjectName("frame_9")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_9)
        self.horizontalLayout_6.setContentsMargins(-1, 89, -1, -1)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.NotifyMainLabel = QtWidgets.QLabel(self.frame_9)
        self.NotifyMainLabel.setStyleSheet("font: 75 15pt \"Ubuntu Condensed\";")
        self.NotifyMainLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.NotifyMainLabel.setObjectName("NotifyMainLabel")
        self.horizontalLayout_6.addWidget(self.NotifyMainLabel)
        self.verticalLayout_2.addWidget(self.frame_9, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.frame_16 = QtWidgets.QFrame(self.frame_11)
        self.frame_16.setStyleSheet("border:none;")
        self.frame_16.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_16.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_16.setObjectName("frame_16")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.frame_16)
        self.verticalLayout_10.setContentsMargins(-1, 42, -1, 21)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.RegisterButton = QtWidgets.QPushButton(self.frame_16)
        self.RegisterButton.setMinimumSize(QtCore.QSize(200, 50))
        self.RegisterButton.setStyleSheet("QPushButton {\n"
"border-color: rgb(255,255,255);\n"
"border-style: inset;\n"
"border-width: 1.5px;\n"
"border-radius: 5px;\n"
"color: rgb(255, 255, 255);\n"
"font: 75 15pt \"Ubuntu Condensed\";\n"
"padding: 0 10px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    background-color: rgb(122, 155, 153);\n"
"}")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("./icons/user-plus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.RegisterButton.setIcon(icon7)
        self.RegisterButton.setIconSize(QtCore.QSize(30, 30))
        self.RegisterButton.setObjectName("RegisterButton")
        self.verticalLayout_10.addWidget(self.RegisterButton, 0, QtCore.Qt.AlignHCenter)
        self.verticalLayout_2.addWidget(self.frame_16, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
        self.horizontalLayout_8.addWidget(self.frame_11, 0, QtCore.Qt.AlignTop)
        self.verticalLayout.addWidget(self.frame_3)
        self.horizontalLayout.addWidget(self.frame)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Parking Management"))
        self.BackButton.setText(_translate("MainWindow", "Back"))
        self.label.setText(_translate("MainWindow", "CREATE NEW ACCOUNT"))
        self.ExitButton.setText(_translate("MainWindow", "Exit"))
        self.label_3.setText(_translate("MainWindow", "FACE"))
        self.StartButton.setText(_translate("MainWindow", "Start"))
        self.CaptureButton.setText(_translate("MainWindow", "Capture"))
        self.label_4.setText(_translate("MainWindow", "ACCOUNT"))
        self.label_9.setText(_translate("MainWindow", "Name"))
        
        self.label_10.setText(_translate("MainWindow", "User name"))
       
        self.label_11.setText(_translate("MainWindow", "Pasword"))

        
        self.label_12.setText(_translate("MainWindow", "Confirm  password"))
        # self.Notify1Label.setText(_translate("MainWindow", ""))
        # self.Notify2Label.setText(_translate("MainWindow", ""))
        # self.Notify3Label.setText(_translate("MainWindow", ""))
        # self.Notify4Label.setText(_translate("MainWindow", ""))
        # self.NotifyMainLabel.setText(_translate("MainWindow", ""))
        
        self.RegisterButton.setText(_translate("MainWindow", "REGISTER"))
        #connect button
        self.StartButton.clicked.connect(self.StartVideo)
        self.CaptureButton.clicked.connect(self.Capture)
        self.BackPicButton.clicked.connect(self.BackPic)
        self.NextPicButton.clicked.connect(self.NextPic)
        self.DeletePicButton.clicked.connect(self.DeletePic)
        self.ExitButton.clicked.connect(MainWindow.close)
        self.BackButton.clicked.connect(self.Back)
        self.RegisterButton.clicked.connect(self.Register)

        ## press event
        self.NameLine.mouseReleaseEvent = self.PressName
        self.UsernameLine.mouseReleaseEvent = self.PressUserName
        self.PasswordLine.mouseReleaseEvent = self.PressPassWord
        self.ConfirmPasswordLine.mouseReleaseEvent = self.PressConfirmPassWord


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
