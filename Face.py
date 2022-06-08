from Yolo.detect import Y5Detect
from pymongo import MongoClient
# import face_recognition
import cv2

model = Y5Detect(weights="./Yolo/weights/best.pt")


uri = "mongodb://localhost:27017/"
Client = MongoClient(uri)
DataBase = Client["Thien"]
UserCollection = DataBase["User"]





def RegFace(Codes,TestImage,bboxes,thresh=0.6):
    Name = None
    Id = None

    if len(bboxes)> 0:
        x0, y0, x1, y1 = [int(_) for _ in bboxes[0]][:4]
        img = TestImage[y0-10:y1+10, x0-10:x1+10]
        if img.shape[0]>0 and img.shape[1]>0:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            EncodeTest = face_recognition.face_encodings(img)
            if len(EncodeTest)>0:
                EncodeTest = EncodeTest[0]
                for i in range(len(Codes)):
                    result = face_recognition.compare_faces([Codes[i]], EncodeTest,tolerance=thresh)
                    if result[0] == True:
                        User = UserCollection.find_one({"Code": Codes[i]})
                        Id = User['_id']
                        Name = User['Name']
                        # cv2.putText(TestImage, "Name:{} id {}".format(Name, id ), (x0, y0), 0, 5e-3 * 130, (0, 255, 255), 2)

    return TestImage,Name,Id

def DrawFace(image=None, boxes=None,labels=None, scores=0):

    FaceBoxes  = []
    FaceScores = []
    for i in range(len(labels)):
        W = boxes[i][2] - boxes[i][0]
        H = boxes[i][3] - boxes[i][1]
        if (labels[i] =="withmask" or labels[i] =="withoutmask") and W > 100 and H >100:
            FaceBoxes.append(boxes[i])
            FaceScores.append(scores[i])
    color = [0,255,0]

    FaceBbox = []



    if len(FaceBoxes) > 0:
        FaceBbox.append(FaceBoxes[0])
        label = "Face: {:.2f}".format(FaceScores[0])
        xmin, ymin, xmax, ymax = FaceBoxes[0]

        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, 1) #cv2.FONT_HERSHEY_SIMPLEX

        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2, cv2.LINE_AA)
        cv2.rectangle(image, (xmin, ymin - h), (xmin + w, ymin), color, -1, cv2.LINE_AA)
        cv2.putText(image, label, (xmin, ymin), cv2.FONT_HERSHEY_COMPLEX_SMALL ,0.8, (255,255,255),1,cv2.LINE_AA)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image,FaceBbox


def DetectFace(image):
    img = image.copy()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    bboxs,labels,scores = model.predict(img)
    img ,bbox = DrawFace(img , bboxs,labels,scores)
    return img,bbox

    


# # from re import I

# from PyQt5.QtWidgets import QDesktopWidget
# from PyQt5 import QtCore, QtGui, QtWidgets
# from pymongo import MongoClient
# from PyQt5.QtCore import QTimer,pyqtSignal,QThread
# from PyQt5.QtGui import QImage
# import imutils
# import Login
# import MainWindow
# import cv2
# import threading
# import numpy as np
# from bson.objectid import ObjectId
# from PIL import Image
# import io
# import time
# from insightface.model_zoo.retinaface import RetinaFace
# from insightface.model_zoo.arcface_onnx import ArcFaceONNX

# detect = RetinaFace(model_file='/home/thien/.insightface/models/buffalo_l/det_10g.onnx')
# from Face import DetectFace


# class Ui_LoginFaceWindow(object):
#     def __init__(self):
#         self.source = 0
#         self.ID = None
#         self.ss = "False"
#         self.StateNext = False
#         self.StaffName = None
#         self.img = None
#         self.Name = None
#         self.ID = None
#         self.count =0
#         self.check = False
#         self.maxvalue = 0
 


#         ## Database
#         uri = "mongodb://localhost:27017/"
#         Client = MongoClient(uri)
#         DataBase = Client["Thien"]
#         self.UserCollection = DataBase["User"]

#         #face reg

#         self.codes = []
#         self.ids = []
#         for self.UserDocument in self.UserCollection.find():
#             self.codes.append(self.UserDocument["Code"])
#             self.ids.append(str(self.UserDocument["_id"]))

#         self.detector = RetinaFace(model_file='/home/thien/.insightface/models/buffalo_l/det_10g.onnx')
#         self.recognizer = ArcFaceONNX(model_file='/home/thien/.insightface/models/buffalo_l/w600k_r50.onnx')

#     def Default(self):
#         self.CODES = []
#         self.IDS = []
#         for UserDocument in self.UserCollection.find():
#             self.CODES.append(UserDocument["Code"])
#             self.IDS.append(str(UserDocument["_id"]))

#     def OpenMainWindow(self):
#         self.MainWindow = QtWidgets.QMainWindow()
#         self.MainUi = MainWindow.Ui_MainWindow(StaffName=self.StaffName)
#         self.MainUi.setupUi(self.MainWindow)
#         self.MainWindow.show()

#     def Next(self):
#         if self.StateNext:
#             self.OpenMainWindow()
#             self.LoginFaceWindow.close()



#     def Logout(self):
#         if self.cap != None and self.timer != None:
#             self.cap.release()
#             self.timer.stop()
#         self.LoginWindow = QtWidgets.QMainWindow()
#         self.LoginUi = Login.UiLoginWindow()
#         self.LoginUi.setupUi(self.LoginWindow)
#         self.LoginWindow.show()
    

#     def Center(self,widget):
#         qr = widget.frameGeometry()
#         cp = QDesktopWidget().availableGeometry().center()
#         qr.moveCenter(cp)
#         widget.move(qr.topLeft())

#     def LoadImage(self, image):
#         image = imutils.resize(image, width=500)
#         frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
#         image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
#         self.GetFaceLabel.setPixmap(QtGui.QPixmap.fromImage(image))
    
#     def drawbox(self,image):
#         if len(self.bboxes)> 0:
#             xmin,ymin,xmax,ymax,score = [int(_) for _ in bboxes[0]][:5]
#             # FaceImage = self.image[ymin:ymax,xmin:xmax]
#             cv2.rectangle(image, (xmin, ymin ), (xmax ,ymax), (0,255,0), 1, cv2.LINE_AA)
#             self.image = image
#             # return FaceImage
#     def detect(self,image):
#         self.bboxes, self.kpss = self.detector.detect(image, input_size =(640, 640))
#         self.drawbox(image)

#     def View_video(self):
#         t1 = time.time()
#         ret, self.image = self.cap.read()
#         self.image,bbox= DetectFace(self.image)
        
#         # if self.count < 5:
#         #     self.count +=1
#         # if self.count == 5:
        
#         k1 = threading.Thread(target=self.RecognizeFace,args=(self.image,))
#         k1.start()
        
            
#             # threading.Thread(target=self.CheckAndShowInfo(self.img,self.Name,self.ID))
#             # self.count =0

        
       
#         self.LoadImage(self.image)
#         # image,self.Name,self.ID  = self.RecognizeFace()

        
#         #
#         # self.CheckAndShowInfo(self.img,self.Name,self.ID)
#         print("time:",time.time()-t1)
 

#     def RecognizeFace(self,image):
#         self.img = None
#         self.Name = None
#         self.ID = None
#         print("RecognizeFace")
#         bboxes, self.kpss = self.detector.detect(image, input_size =(640, 640))
#         if len(bboxes)> 0:
            
            
#             Distance = []
#             EncodeTest = self.recognizer.get(image, self.kpss[0])
#             for CodeOb in self.CODES:
#                 ds = []
#                 for code in CodeOb:
#                     distance = self.recognizer.compute_sim(EncodeTest,np.array(code))
#                     ds.append(distance)
#                 d = max(ds) 
#                 Distance.append(d)
#             self.maxvalue = max(Distance)
#             self.indexmax = np.argmax(Distance)
#             print(self.maxvalue)
            
            
            
            

       


#     def CheckAndShowInfo(self):
            
#             if  self.maxvalue > 0.3:
#                 ID = self.IDS[self.indexmax]
               
#                 object = self.UserCollection.find_one({"_id":ObjectId(ID)})
#                 Name = object["Name"]
#                 img = object["Images"][0]
#                 image = np.asarray(Image.open(io.BytesIO(img)))


#                 self.CheckNameLabel.setText("{}".format(Name))
#                 self.CheckIDLabel.setText("{}".format(ID))
#                 bboxes, kpss = self.detector.detect(image , input_size =(640, 640))
        
#                 xmin,ymin,xmax,ymax,score = [int(_) for _ in bboxes[0]][:5]
#                 FaceImage = image[ymin:ymax,xmin:xmax]
                
#                 self.LoadImage(FaceImage)
#                 self.StateNext = True
#                 self.StaffName = self.UserCollection.find_one({"_id":ObjectId(ID)})["Name"]
#                 self.check = True
               
#                 self.timer.stop()
#                 self.cap.release()

        
#             self.CheckNameLabel.setText("{}".format(Name))
#             self.CheckIDLabel.setText("{}".format(ID))
#             bboxes, kpss = self.detector.detect(image, input_size =(640, 640))
      
#             xmin,ymin,xmax,ymax,score = [int(_) for _ in bboxes[0]][:5]
#             FaceImage = image[ymin:ymax,xmin:xmax]
            
#             self.LoadImage(FaceImage)
#             self.StateNext = True
#             self.StaffName = self.UserCollection.find_one({"_id":ObjectId(ID)})["Name"]
#             self.timer.stop()
#             self.cap.release()


#     def Run(self):
#         self.cap = cv2.VideoCapture(self.source)
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.View_video)
#         self.timer.start(60)


#     def setupUi(self, LoginFaceWindow):
#         self.Center(LoginFaceWindow)
#         LoginFaceWindow.setObjectName("LoginFaceWindow")
#         LoginFaceWindow.resize(760, 658)
#         LoginFaceWindow.setMaximumSize(QtCore.QSize(760, 658))
#         LoginFaceWindow.setStyleSheet("background-color: rgb(18, 16, 61);\n"
# "")
#         self.LoginFaceWidget = QtWidgets.QWidget(LoginFaceWindow)
#         self.LoginFaceWidget.setObjectName("LoginFaceWidget")
#         self.verticalLayout = QtWidgets.QVBoxLayout(self.LoginFaceWidget)
#         self.verticalLayout.setContentsMargins(0, 0, 0, 0)
#         self.verticalLayout.setSpacing(0)
#         self.verticalLayout.setObjectName("verticalLayout")
#         self.main = QtWidgets.QWidget(self.LoginFaceWidget)
#         self.main.setObjectName("main")
#         self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.main)
#         self.verticalLayout_2.setContentsMargins(9, 0, -1, 0)
#         self.verticalLayout_2.setObjectName("verticalLayout_2")
#         self.TopFrame = QtWidgets.QFrame(self.main)
#         self.TopFrame.setMaximumSize(QtCore.QSize(16777215, 100))
#         self.TopFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
#         self.TopFrame.setFrameShadow(QtWidgets.QFrame.Raised)
#         self.TopFrame.setObjectName("TopFrame")
#         self.horizontalLayout = QtWidgets.QHBoxLayout(self.TopFrame)
#         self.horizontalLayout.setObjectName("horizontalLayout")
#         self.BackButton = QtWidgets.QPushButton(self.TopFrame)
#         sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
#         sizePolicy.setHorizontalStretch(0)
#         sizePolicy.setVerticalStretch(0)
#         sizePolicy.setHeightForWidth(self.BackButton.sizePolicy().hasHeightForWidth())
#         self.BackButton.setSizePolicy(sizePolicy)
#         self.BackButton.setMinimumSize(QtCore.QSize(100, 40))
#         self.BackButton.setMaximumSize(QtCore.QSize(100, 40))
#         self.BackButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
#         self.BackButton.setStyleSheet("QPushButton {\n"
# "border-color: rgb(255,255,255);\n"
# "border-style: inset;\n"
# "border-width: 1.5px;\n"
# "border-radius: 8px;\n"
# "color: rgb(255, 255, 255);\n"
# "font: 75 15pt \"Ubuntu Condensed\";\n"
# "}\n"
# "\n"
# "QPushButton:pressed{\n"
# "    background-color: rgb(122, 155, 153);\n"
# "}\n"
# "")
#         icon = QtGui.QIcon()
#         icon.addPixmap(QtGui.QPixmap("./icons/chevrons-left.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
#         self.BackButton.setIcon(icon)
#         self.BackButton.setIconSize(QtCore.QSize(35, 35))
#         self.BackButton.setObjectName("BackButton")
#         self.horizontalLayout.addWidget(self.BackButton)
#         self.TitleLabel = QtWidgets.QLabel(self.TopFrame)
#         self.TitleLabel.setStyleSheet("color: rgb(255, 255, 255);\n"
# "font: 75 30pt \"Ubuntu Condensed\";")
#         self.TitleLabel.setObjectName("TitleLabel")
#         self.horizontalLayout.addWidget(self.TitleLabel, 0, QtCore.Qt.AlignHCenter)
#         self.NextButton = QtWidgets.QPushButton(self.TopFrame)
#         self.NextButton.setMinimumSize(QtCore.QSize(0, 40))
#         self.NextButton.setMaximumSize(QtCore.QSize(100, 40))
#         self.NextButton.setLayoutDirection(QtCore.Qt.RightToLeft)
#         self.NextButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
#         self.NextButton.setStyleSheet("QPushButton {\n"
# "border-color: rgb(255,255,255);\n"
# "border-style: inset;\n"
# "border-width: 1.5px;\n"
# "border-radius: 8px;\n"
# "color: rgb(255, 255, 255);\n"
# "font: 75 15pt \"Ubuntu Condensed\";\n"
# "padding: 0 12px;\n"
# "}\n"
# "\n"
# "QPushButton:pressed{\n"
# "    background-color: rgb(122, 155, 153);\n"
# "}\n"
# "")
#         icon1 = QtGui.QIcon()
#         icon1.addPixmap(QtGui.QPixmap("./icons/chevrons-right.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
#         self.NextButton.setIcon(icon1)
#         self.NextButton.setIconSize(QtCore.QSize(35, 35))
#         self.NextButton.setObjectName("NextButton")
#         self.horizontalLayout.addWidget(self.NextButton)
#         self.verticalLayout_2.addWidget(self.TopFrame)
#         self.CenterFrame = QtWidgets.QFrame(self.main)
#         self.CenterFrame.setMinimumSize(QtCore.QSize(500, 500))
#         self.CenterFrame.setMaximumSize(QtCore.QSize(500, 500))
#         self.CenterFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
#         self.CenterFrame.setFrameShadow(QtWidgets.QFrame.Raised)
#         self.CenterFrame.setObjectName("CenterFrame")
#         self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.CenterFrame)
#         self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
#         self.verticalLayout_3.setSpacing(0)
#         self.verticalLayout_3.setObjectName("verticalLayout_3")
#         self.GetFaceLabel = QtWidgets.QLabel(self.CenterFrame)
#         self.GetFaceLabel.setMinimumSize(QtCore.QSize(500, 500))
#         self.GetFaceLabel.setMaximumSize(QtCore.QSize(500, 500))

#         self.GetFaceLabel.setStyleSheet("border: none;")
#         self.GetFaceLabel.setText("")
#         self.GetFaceLabel.setScaledContents(True)
#         self.GetFaceLabel.setWordWrap(False)

#         self.GetFaceLabel.setObjectName("GetFaceLabel")


#         self.verticalLayout_3.addWidget(self.GetFaceLabel, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
#         self.verticalLayout_2.addWidget(self.CenterFrame, 0, QtCore.Qt.AlignHCenter)
#         self.BottomFrame = QtWidgets.QFrame(self.main)
#         self.BottomFrame.setMaximumSize(QtCore.QSize(16777215, 140))
#         self.BottomFrame.setStyleSheet("color: rgb(255, 255, 255);\n"
# "font: 75 12pt \"Ubuntu Condensed\";")
#         self.BottomFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
#         self.BottomFrame.setFrameShadow(QtWidgets.QFrame.Raised)
#         self.BottomFrame.setObjectName("BottomFrame")
#         self.gridLayout = QtWidgets.QGridLayout(self.BottomFrame)
#         self.gridLayout.setHorizontalSpacing(50)
#         self.gridLayout.setObjectName("gridLayout")
#         self.CheckNameLabel = QtWidgets.QLabel(self.BottomFrame)
#         self.CheckNameLabel.setObjectName("CheckNameLabel")
#         self.gridLayout.addWidget(self.CheckNameLabel, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
#         self.NameLabel = QtWidgets.QLabel(self.BottomFrame)
#         self.NameLabel.setObjectName("NameLabel")
#         self.gridLayout.addWidget(self.NameLabel, 0, 0, 1, 1, QtCore.Qt.AlignRight)
#         self.IDLabel = QtWidgets.QLabel(self.BottomFrame)
#         self.IDLabel.setObjectName("IDLabel")
#         self.gridLayout.addWidget(self.IDLabel, 1, 0, 1, 1, QtCore.Qt.AlignRight)
#         self.CheckIDLabel = QtWidgets.QLabel(self.BottomFrame)
#         self.CheckIDLabel.setObjectName("CheckIDLabel")
#         self.gridLayout.addWidget(self.CheckIDLabel, 1, 1, 1, 1, QtCore.Qt.AlignLeft)
#         self.verticalLayout_2.addWidget(self.BottomFrame)
#         self.verticalLayout.addWidget(self.main)
#         LoginFaceWindow.setCentralWidget(self.LoginFaceWidget)

#         self.retranslateUi(LoginFaceWindow)
#         QtCore.QMetaObject.connectSlotsByName(LoginFaceWindow)

#     def retranslateUi(self, LoginFaceWindow):
#         self.LoginFaceWindow = LoginFaceWindow
#         _translate = QtCore.QCoreApplication.translate
#         LoginFaceWindow.setWindowTitle(_translate("LoginFaceWindow", "Parking Management"))
#         self.BackButton.setText(_translate("LoginFaceWindow", "Back"))
#         self.TitleLabel.setText(_translate("LoginFaceWindow", "LOGIN WITH FACE"))
#         self.NextButton.setText(_translate("LoginFaceWindow", "Next"))
#         self.CheckNameLabel.setText(_translate("LoginFaceWindow", "Unknow"))
#         self.NameLabel.setText(_translate("LoginFaceWindow", "Name"))
#         self.IDLabel.setText(_translate("LoginFaceWindow", "ID"))
#         self.CheckIDLabel.setText(_translate("LoginFaceWindow", "None"))
#         self.Run()

#         self.BackButton.setShortcut("Ctrl+B")
#         self.NextButton.setShortcut("Ctrl+N")
#         self.BackButton.clicked.connect(self.Logout)
#         self.BackButton.clicked.connect(LoginFaceWindow.close)
#         self.NextButton.clicked.connect(self.Next)

#         #default
#         self.Default()

# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     LoginFaceWindow = QtWidgets.QMainWindow()
#     ui = Ui_LoginFaceWindow()
#     ui.setupUi(LoginFaceWindow)
#     LoginFaceWindow.show()
#     sys.exit(app.exec_())
