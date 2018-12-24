import configparser
import TuLingRobot
import itchat
import cv2
import Util
from django.http import HttpResponse


a = itchat.get_QRuuid()
print(a)
itchat.get_QR(uuid=a, enableCmdQR=2, picDir='tt.png')
# itchat.login(picDir='./tt.png')
if(itchat.check_login()):
    print(123)