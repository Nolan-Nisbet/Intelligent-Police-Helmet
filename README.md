# Intelligent Police Helmet (Work-in-Progress)
This project is aimed to tackle the technological limitations police officers face when they are away from their vehicles or out on patrol. The goal of this project is to design an intelligent safety helmet that will be outfitted with several features that will function both as a means of protecting an officer and providing them with supplemental information not clearly apparent to them through the use of computer vision applications. The brain of the helmet, the Jetson TK1 Developmental Board, receives a live video stream from the helmet mounted camera, where we then plan to implement: facial detection for suspect recognition, calls to Microsoft Oxford API’s for individual information (age, gender, emotional state), and video storage onto a black box. The information will be presented to the officer via a GUI on a touchscreen heads-up-display unit, which allows for officer input to access the different functions. Stretch goals include licnes plaet number recognition as well as matching any scanned numbers with a predefined database of vehicles and their registration details, 

##Current State
The program currently supports calls to Microsofts Project Oxford API for facial recognition, scene recognition amd emption detection. The GUI is currently being tailored for our screen.

##Upcoming
###Software
We plan on taking advantage of Jetsons on Board graphics card to run various image progcessing techniques using openCV. This inlcudes face detection, object tracking, and text recognition for identifying license plate numbers. Our program currently stored recorded video onboard but we would like to move towards uploading video to a remote server.

###Hardware
Next step is to 3D print cases for the board, camera, battery and mount them on our helmet. Due to budget constrants we wont be able to mount a micro OLED "Google Glass Style" over the eye but will instead have our 5 inch touchscreen secured to the users arm via an elastic wrist band. To help fix any limitations caused by the absens eof a heads up display we will use text-to-speech software to tell the user the information found after scanning so they are not forced to  look down to get their results.


####Parts List
Nvidia Jetson Tk1: http://www.nvidia.ca/object/jetson-tk1-embedded-dev-kit.html

5 inch touchscreen: https://www.seeedstudio.com/5-Inch-HDMI-Display-with-USB-TouchScreen-p-2638.html

Helmet: https://www.amazon.ca/Black-Free-Size-Tactical-Helmet/dp/B01CLN0ZEY/ref=s9_simh_gw_g79_i4_r?pf_rd_m=A3DWYIK6Y9EEQB&pf_rd_s&pf_rd_r=Z47D9BEGF3JF2V9596WT&pf_rd_t=36701&pf_rd_p=b06971ce-9992-44c1-9ee0-eb9792e71b5e&pf_rd_i=desktop

Battery: https://www.amazon.com/gp/product/B00FE0OHKK/ref=as_li_tl?ie=UTF8&camp=1789&creative=390957&creativeASIN=B00FE0OHKK&linkCode=as2&tag=jetsonhacks-20&linkId=LEGLHUR5BPT67TNF

8mb USB 3.0 Global Shutter Camera


##Additional Information
API Link: https://www.microsoft.com/cognitive-services/en-us/
Python GUI: PyQt5
python Version 3.44
Operating System: Ubuntu 14.0
OpenCV V2
Text-to-Speech Library: Pyttsx

