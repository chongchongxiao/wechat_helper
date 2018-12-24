import json
import requests

ERROR_CODE = [5000, 6000, 4000, 4001, 4002, 4003, 4005, 4007, 4100, 4200, 4300, 4400, 4500, 4600, 4602, 7002, 8008]


def get_text_reply(_info):
    '''
    回复text类的消息
    :param _info: 消息内容
    :return: 一个list，可能有一个元素，可能有多个元素
    '''
    api_url = 'http://www.tuling123.com/openapi/api/v2'  # 图灵机器人网址
    dat = {
        'reqType': 0,
        'perception': {
            'inputText': {
                'text': _info
            }
        },
        'userInfo': {
            'apiKey': '40f93ab6a92a49ff909b329df2a54f0c',
            'userId': 'weChatRobot'
        }
    }
    dat = json.dumps(dat)
    reply = requests.post(api_url, data=dat).json()  # 把data数据发
    code = reply['intent']['code']
    if code in ERROR_CODE:
        return None
    return reply['results']


def get_picture_reply(_info):
    '''
    回复图片类的消息
    :param _info: 图片的本地地址，例如./fun.jpg
    :return: 一个list，可能有一个元素，可能有多个元素
    '''
    img_url = _info
    api_url = 'http://www.tuling123.com/openapi/api/v2'  # 图灵机器人网址
    dat = {
        'reqType': 1,
        'perception': {
            'inputImage': {
                'url': img_url
            }
        },
        'userInfo': {
            'apiKey': '40f93ab6a92a49ff909b329df2a54f0c',
            'userId': 'weChatRobot'
        }
    }
    dat = json.dumps(dat)
    reply = requests.post(api_url, data=dat).json()  # 把data数据发
    code = reply['intent']['code']
    if code in ERROR_CODE:
        return None
    return reply['results']


def get_recording_reply(_info):
    '''
    回复语音类的消息
    :param _info: 语音链接，例如./fun.mp3
    :return:一个list，可能有一个元素，可能有多个元素
    '''
    recording_url = _info
    api_url = 'http://www.tuling123.com/openapi/api/v2'  # 图灵机器人网址
    dat = {
        'reqType': 2,
        'perception': {
            'inputMedia': {
                'url': recording_url
            }
        },
        'userInfo': {
            'apiKey': '40f93ab6a92a49ff909b329df2a54f0c',
            'userId': 'weChatRobot'
        }
    }
    dat = json.dumps(dat)
    reply = requests.post(api_url, data=dat).json()  # 把data数据发
    code = reply['intent']['code']
    if code in ERROR_CODE:
        return None
    return reply['results']