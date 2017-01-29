import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
import time
import requests
import operator
import numpy as np
import http.client, urllib.request, urllib.parse, urllib.error
import pyttsx


#Inteligent Police Helmet 
#Nolan Nisbet
#Alex Harrietha
#Nathan Stevenson




#Thread used to capture frames from camera and send them send them to GUI
class ShowVideo(QThread):
    camera_port = 0
    camera = cv2.VideoCapture(camera_port)
    camera.set(3, 500) #Width
    camera.set(4,375) #Height
    videoSignal = pyqtSignal(QImage, int, int, np.ndarray)
 


    def __init__(self):
        super().__init__()

        self.prev_mode = False
        self.curr_mode = False





    def toggle_mode(self):
        self.prev_mode = self. curr_mode
        self.curr_mode = not self.curr_mode

    @pyqtSlot()
    def run(self):
        run_video = True
        while run_video:
            ret, image = self.camera.read()

            if(self.curr_mode == True and not self.prev_mode):
                self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
                self.out = cv2.VideoWriter('output.avi', self.fourcc, 20.0, (640,480))
                #print('started recording')
                self.out.write(image)
                self.prev_mode = True
            elif(self.curr_mode and self.prev_mode):
                self.out.write(image)
                #print('recording')
            elif(not self.curr_mode and self.prev_mode):
                self.out.release()
                #print('done recording')
                self.prev_mode = False



            color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            height, width, byteValue = color_swapped_image.shape
            byteValue = byteValue * width
            qt_image = QImage(color_swapped_image.data,
                              width, height, byteValue,
                                        QImage.Format_RGB888)

            self.videoSignal.emit(qt_image, height, width, image)

class Window(QWidget):
    def __init__(self):
        super().__init__()



        self.initUI()
        self.frame = None
        self.frameCV = None
        self.currframe = None
        self.recording = False
        self.cur_mode = 'feed'

        # initialize cam capture thread
        self.feedThread = ShowVideo()
        self.feedThread.videoSignal.connect(self.updateImage)
        self.feedThread.start()

    def initUI(self):

        #self.setStyleSheet('background-color: rgb(64,64,64)')
        self.piclbl = QLabel('prev text')
        self.infolbl = QLabel('this is where all important info will be displayed')

        self.recordbtn = QPushButton('Rec')
        self.feedbtn = QPushButton('Cam Feed')
        self.emotionbtn = QPushButton('Emotion')
        self.facebtn = QPushButton('Face Detect')
        self.visionbtn = QPushButton('Scene Recognition')
        self.cvbtn = QPushButton('CV')

        self.feedbtn.clicked.connect(self.feedClicked)
        self.emotionbtn.clicked.connect(self.emotionClicked)
        self.visionbtn.clicked.connect(self.visionClicked)
        self.facebtn.clicked.connect(self.faceClicked)
        self.recordbtn.clicked.connect(self.recordClicked)

        self.feedbtn.setFixedSize(300, 80)
        self.emotionbtn.setFixedSize(300, 80)
        self.facebtn.setFixedSize(300, 80)
        self.visionbtn.setFixedSize(300, 80)
        self.cvbtn.setFixedSize(300, 80)

        self.infolbl.setWordWrap(True) #allows multiline text
        self.infolbl.setFixedSize(590,80)

        vboxleft = QVBoxLayout()
        vboxleft.addWidget(self.recordbtn)
        vboxleft.addWidget(self.piclbl)
        vboxleft.addWidget(self.infolbl)

        vboxright = QVBoxLayout()
        vboxright.addWidget(self.feedbtn)
        vboxright.addWidget(self.emotionbtn)
        vboxright.addWidget(self.facebtn)
        vboxright.addWidget(self.visionbtn)
        vboxright.addWidget(self.cvbtn)

        hbox = QHBoxLayout()
        hbox.addLayout(vboxleft)
        hbox.addLayout(vboxright)

        self.setLayout(hbox)



        self.setGeometry(0, 0, 800, 480)

        self.setWindowTitle('Demo')
        self.show()

    def updateImage(self,frame, height, width, frameCV):
        self.frame = frame
        self.frameCV = frameCV


        if (self.cur_mode == 'feed'):
            pixmap = QPixmap(width, height)
            pixmap.convertFromImage(frame)
            self.piclbl.setPixmap(pixmap)

    #def speak(self):
        #self.engine.speak(str) #Will use later for text to speech
        #self.engine.runAndWait()

    def feedClicked(self):
        self.cur_mode = 'feed'
        self.infolbl.setText('')


    def recordClicked(self):
        self.feedThread.toggle_mode()
        self.recording = not self.recording

        if self.recording:
            self.recordbtn.setStyleSheet('background-color: rgb(204,0,0)')

        else:
            self.recordbtn.setStyleSheet('background-color: rgb(192,192,192)')

    def processEmotionRequest(self, json, data, headers, params):
        retries = 0
        result = None
        _url = 'https://api.projectoxford.ai/emotion/v1.0/recognize'

        while True:
            response = requests.request('post', _url, json=json, data=data, headers=headers, params=params)
            if response.status_code == 429:
                print("Message: %s" % (response.json()['error']['message']))
                if retries <= 10:
                    time.sleep(1)
                    retries += 1
                    continue
                else:
                    print('Error: failed after retrying!')
                    break

            elif response.status_code == 200 or response.status_code == 201:

                if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                    result = None
                elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                    if 'application/json' in response.headers['content-type'].lower():
                        result = response.json() if response.content else None
                    elif 'image' in response.headers['content-type'].lower():
                        result = response.content
            else:
                print("Error code: %d" % (response.status_code))
                print("Message: %s" % (response.json()['error']['message']))
            break
        return result

    def renderEmotionResultOnImage(self, result, img):
        for currFace in result:
            faceRectangle = currFace['faceRectangle']
            cv2.rectangle(img, (faceRectangle['left'], faceRectangle['top']),
                          (faceRectangle['left'] + faceRectangle['width'],
                           faceRectangle['top'] + faceRectangle['height']),
                          color=(255, 0, 0), thickness=5)

        for currFace in result:
            faceRectangle = currFace['faceRectangle']
            currEmotion = max(currFace['scores'].items(), key=operator.itemgetter(1))[0]

            textToWrite = "%s" % (currEmotion)
            cv2.putText(img, textToWrite, (faceRectangle['left'], faceRectangle['top'] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 0, 0), 1)

    def emotionClicked(self):
        headers = dict()
        headers['Ocp-Apim-Subscription-Key'] = '' #Put you sub key here
        headers['Content-Type'] = 'application/octet-stream'



        json = None
        params = None

        self.currframe = self.frameCV.copy()
        cv2.imwrite('testimage.jpg', self.currframe)
        pathToFileInDisk = r'testimage.jpg'

        with open(pathToFileInDisk, 'rb') as f:
           data = f.read()

        result = self.processEmotionRequest(json, data, headers, params)

        print(result)

        if result:
            print('what')
            self.renderEmotionResultOnImage(result, self.currframe)

            color_swapped_image = cv2.cvtColor(self.currframe, cv2.COLOR_BGR2RGB)

            height, width, byteValue = color_swapped_image.shape
            byteValue = byteValue * width
            qt_image = QImage(color_swapped_image.data,
                              width, height, byteValue,
                              QImage.Format_RGB888)

            pixmap = QPixmap(width, height)
            pixmap.convertFromImage(qt_image)
            self.cur_mode = 'emotion'
            self.piclbl.setPixmap(pixmap)
        else:
            self.infolbl.setText('no person found')

        self.cur_mode = 'emotion' #not sure why needed, but program will crash (probably threading issues)


    def processVisionRequest(self, json, data, headers, params):

        _url = 'https://api.projectoxford.ai/vision/v1.0/analyze'

        retries = 0
        result = None

        while True:
            response = requests.request('post', _url, json=json, data=data, headers=headers, params=params)
            print(response)
            if response.status_code == 429:
                print("Message: %s" % (response.json()['error']['message']))
                if retries <= 10:
                    time.sleep(1)
                    retries += 1
                    continue
                else:
                    print('Error: failed after retrying!')
                    break

            elif response.status_code == 200 or response.status_code == 201:

                if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                    result = None
                elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                    if 'application/json' in response.headers['content-type'].lower():
                        result = response.json() if response.content else None
                    elif 'image' in response.headers['content-type'].lower():
                        result = response.content
            else:
                print("Error code: %d" % (response.status_code))
                print("Message: %s" % (response.json()['error']['message']))

            break

        return result


    def renderVisionResultOnImage(self, result, img):

        R = int(result['color']['accentColor'][:2], 16)
        G = int(result['color']['accentColor'][2:4], 16)
        B = int(result['color']['accentColor'][4:], 16)

        cv2.rectangle(img, (0, 0), (img.shape[1], img.shape[0]), color=(R, G, B), thickness=25)

        #if 'categories' in result:
        #    categoryName = sorted(result['categories'], key=lambda x: x['score'])[0]['name']
        #    cv2.putText(img, categoryName, (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)

        for currFace in result['faces']:
            faceRectangle = currFace['faceRectangle']
            cv2.rectangle(img, (faceRectangle['left'], faceRectangle['top']),
                          (faceRectangle['left'] + faceRectangle['width'],
                           faceRectangle['top'] + faceRectangle['height']),
                          color=(255, 0, 0), thickness=5)

        for currFace in result['faces']:
            faceRectangle = currFace['faceRectangle']
            currGender = currFace['gender']
            currAge = currFace['age']

            textToWrite = "%s" % (currGender) + ', ' + "%s" % (currAge)
            cv2.putText(img, textToWrite, (faceRectangle['left'], faceRectangle['top'] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 0, 0), 1)



    def visionClicked(self):

        # Computer Vision parameters
        params = {'visualFeatures': 'Color,Categories,Tags,Description,Faces'}
        headers = dict()
        headers['Ocp-Apim-Subscription-Key'] = '' #Put you sub key here
        headers['Content-Type'] = 'application/octet-stream'
        json = None


        self.currframe = self.frameCV.copy()

        cv2.imwrite('testimage.jpg', self.currframe)
        pathToFileInDisk = r'testimage.jpg'

        with open(pathToFileInDisk, 'rb') as f:
            data = f.read()

        result = self.processVisionRequest(json, data, headers, params)

        print(result)

        if result is not None:
            self.renderVisionResultOnImage(result, self.currframe)
            color_swapped_image = cv2.cvtColor(self.currframe, cv2.COLOR_BGR2RGB)

            height, width, byteValue = color_swapped_image.shape
            byteValue = byteValue * width
            qt_image = QImage(color_swapped_image.data,
                              width, height, byteValue,
                              QImage.Format_RGB888)

            pixmap = QPixmap(width, height)
            pixmap.convertFromImage(qt_image)
            self.infolbl.setText('Description: ' + result['description']['captions'][0]['text'])
            self.cur_mode = 'vision'
            self.piclbl.setPixmap(pixmap)


    def processFaceIDRequest(self, json, data, headers, params):

        """
        Helper function to process the request to Project Oxford

        Parameters:
        json: Used when processing images from its URL. See API Documentation
        data: Used when processing image read from disk. See API Documentation
        headers: Used to pass the key information and the data type request
        """

        _url = 'https://api.projectoxford.ai/face/v1.0/detect'

        retries = 0
        result = None

        while True:

            response = requests.request('post', _url, json=json, data=data, headers=headers, params=params)

            print(response)

            if response.status_code == 429:

                print("Message: %s" % (response.json()['error']['message']))

                if retries <= 10:
                    time.sleep(1)
                    retries += 1
                    continue
                else:
                    print('Error: failed after retrying!')
                    break

            elif response.status_code == 200 or response.status_code == 201:

                if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                    result = None
                elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                    if 'application/json' in response.headers['content-type'].lower():
                        result = response.json() if response.content else None
                    elif 'image' in response.headers['content-type'].lower():
                        result = response.content
            else:
                print("Error code: %d" % (response.status_code))
                print("Message: %s" % (response.json()['error']['message']))

            break

        return result


    def faceClicked(self):
        # Face parameters
        params = urllib.parse.urlencode({
            # Request parameters
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
        })

        headers = dict()
        headers['Ocp-Apim-Subscription-Key'] = '' #Put you sub key here
        headers['Content-Type'] = 'application/octet-stream'

        json = None

        self.currframe = self.frameCV.copy()
        cv2.imwrite('testimage.jpg', self.currframe)
        pathToFileInDisk = r'testimage.jpg'

        with open(pathToFileInDisk, 'rb') as f:
            data = f.read()

        result = self.processFaceIDRequest(json, data, headers, params)

        if result:
            faceId = result[0]['faceId'] #could be trouble
            print(faceId)
            headers = None
            headers = dict()
            headers['Ocp-Apim-Subscription-Key'] = '' #Put you sub key here
            headers['Content-Type'] = 'application/json'
            data = None
            faceIds = [faceId]
            json = None
            params = None

            json = {
                'personGroupId': 'testgroup',
                'faceIds': [faceId],
                'maxNumOfCandidatesReturned': 1,
                'confidenceThreshold': 0.5,
            }

            _url = 'https://api.projectoxford.ai/face/v1.0/identify'
            response = requests.request('post', _url, params=params, data=data,
                                        json=json, headers=headers)
            result = response.json()
            print(result)
            print(result[0]['candidates'])

            if  result[0]['candidates']:
                candidateId = result[0]['candidates'][0]['personId']
                confidence = result[0]['candidates'][0]['confidence']
                print(candidateId)

                _url = 'https://api.projectoxford.ai/face/v1.0/persongroups/{}/persons/{}'.format('testgroup', candidateId) #Repalce testgroup with the name of your group
                json = None
                params = urllib.parse.urlencode({
                    # Request parameters
                    'personGroupId': 'testgroup', #Replace testgroup with the name of your group
                    'personId': candidateId,
                })

                params = None
                response = requests.request('get', _url, params=params, data=data,
                                            json=json, headers=headers)
                result = response.json()
                person = result['name']
                info = result['userData']
                self.infolbl.setText(person + ': ' + info)
                #self.speak(person)
                #self.speak(info)
                self.cur_mode = 'face'
            else:
                self.infolbl.setText('person not found in database')
                #self.speak('person not found in database')
        else:
            self.infolbl.setText('no face identified')
            #self.speak('no face identified')

        self.cur_mode = 'face' #not sure why needed, but program will crash (probably threading issues)

if __name__ == '__main__':

    app = QApplication(sys.argv)

    w = Window()
    sys.exit(app.exec_())
