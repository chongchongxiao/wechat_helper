from mysite import settings
import os
import argparse
import itchat
import time

uuid = itchat.get_QRuuid()
print(uuid)
itchat.get_QR(uuid=uuid, picDir='static/qrcode.png')

res = itchat.check_login(uuid=uuid)
print(res)
# time.sleep(10)
res = itchat.check_login(uuid=uuid)
print(res)
fr = itchat.get_friends(update=True)
print(fr)
itchat.web_init()
fr = itchat.get_friends(update=True)
print(fr)
itchat.new_instance()
