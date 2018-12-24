import itchat
from itchat.content import *
import TuLingRobot
import os
import matplotlib.pyplot as plt
import Util
from ConfigHandle import ConfigHandle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--base_dir',
                    # help='The directory of the project.',
                    default='.', type=str)
parser.add_argument('-p', '--pro_dir',
                    # help='The directory of the project.',
                    default='.', type=str)
parser.add_argument('-i', '--img_path',
                    # help='The directory of the project.',
                    default='picture//qrcode.png', type=str)


'''
全局变量
'''
GROUP_MSG_DATA = {}  # 记录群消息的发言频率
REMIND_MSG_MAP = {1: '好友性别比例', 2: '好友地区分布', 3: '增加\\修改好友自动回复',
                  4: '查看好友自动回复信息', 5: '增加\\修改群自动回复', 6: '查看群自动回复信息',
                  7: '打开\\关闭好友自动回复', 8: '打开\\关闭群自动回复', 9: '统计群消息'}  # 提示消息
BASE_DIR = 'wechat//wechatHelper'
PICTURE_DIR = './/picture'
RECORDING_DIR = './/recording'
REGION_MAX_SHOW = 15  # 显示地区的时候最大显示量，因为显示过多，会导致x轴的标签叠加在一起
CH = ConfigHandle()  # ConfigHandle的实例
FRIENDS_REPLY = {}
GROUP_REPLY = {}
ROBOT_REPLY_STR = '0'
IS_OPEN_FRIENDS_AUTO_REPLY = True  # 是否打开好友自动回复
IS_OPEN_GROUP_AUTO_REPLY = True  # 是否打开群自动回复
MYSELF_MESSAGE = ''  # 用户的个人微信信息
ARGS = parser.parse_args()  # 获取所有的传入参数


@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING, PICTURE, RECORDING, ATTACHMENT, VIDEO, FRIENDS, SYSTEM])
def person_msg(msg):
    '''
    注册事件，用于处理收到的个人发送的消息
    :param msg: 收到的消息
    :return:
    '''
    print('个人消息')
    handle_person_msg(msg)


@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING, PICTURE, RECORDING, ATTACHMENT, VIDEO, FRIENDS], isGroupChat=True)
def group_msg(msg):
    '''
    注册事件，用于处理收到的群消息
    :param msg: 收到的消息
    :return:
    '''
    print('群消息')
    handle_group_msg(msg)


def handle_person_msg(msg):
    '''
    处理个人发送的消息
    :param msg: 消息
    :return:
    '''
    from_user_name = msg['FromUserName']
    to_user_name = msg['ToUserName']
    myself = itchat.get_friends(update=True)[0]
    my_user_name = myself['UserName']
    my_nick_name = myself['NickName']
    msg_type = msg['Type']
    if from_user_name == my_user_name and to_user_name == 'filehelper':
        # 微信本人向自己好的文件助手发送消息，用于一些操作
        if msg_type == 'Text':
            text = msg['Text']
            if text == '1':
                friends_sex_ratio()
            elif text == '2':
                friends_region_ratio(REGION_MAX_SHOW)
            elif text == '3':
                itchat.send_msg('功能暂未开放,敬请期待', toUserName='filehelper')
            elif text == '4':
                get_friends_reply()
            elif text == '5':
                itchat.send_msg('功能暂未开放,敬请期待', toUserName='filehelper')
            elif text == '6':
                get_group_reply()
            elif text == '7':
                modify_friends_auto_reply()
            elif text == '8':
                modify_group_auto_reply()
            elif text == '9':
                itchat.send_msg('功能暂未开放,敬请期待', toUserName='filehelper')
        elif msg_type == 'Attachment':  # 发送的是文件,那么默认是配置文件
            path = CH.get_path(MYSELF_MESSAGE)
            (msg['Text'])(path)
            Util.remove_BOM(path)
            update_reply_content()

    if not IS_OPEN_FRIENDS_AUTO_REPLY:  # 好友自动回复被关闭
        return

    if from_user_name != my_user_name:
        # 这里过滤掉我自己发送的消息
        friend = itchat.search_friends(userName=from_user_name)
        remark_name = Util.standard_name(friend['RemarkName'])
        nick_name = Util.standard_name(friend['NickName'])
        key = remark_name + '—' + nick_name
        reply = FRIENDS_REPLY[key]
        if reply == '':  # 不需要自动回复
            return
        elif reply == ROBOT_REPLY_STR:
            robot_reply_person(msg)
        else:
            itchat.send_msg(reply, from_user_name)


def handle_group_msg(msg):
    '''
    处理群消息
    :param msg:消息
    :return:
    '''
    self_message = itchat.get_friends(update=True)[0]
    my_username = self_message['UserName']
    from_user = msg['FromUserName']
    # chart_room_name 群聊名称
    # nick_name 发消息的人的昵称

    if not IS_OPEN_GROUP_AUTO_REPLY:  # 群消息自动回复被关闭
        return

    if from_user == my_username:
        # 我自己发送的消息
        to_user = msg['ToUserName']
        chart_room_name = itchat.search_chatrooms(userName=to_user)['NickName']
        nick_name = self_message['NickName']
    else:
        # 其他人发送的群消息
        chart_room_name = itchat.search_chatrooms(userName=from_user)['NickName']
        nick_name = msg['ActualNickName']
        group = itchat.search_chatrooms(userName=msg['FromUserName'])
        key = Util.standard_name(group['NickName'])
        if key == '':
            key = '无群名'
        reply = GROUP_REPLY[key]
        if reply == '':  # 不需要自动回复
            pass
        elif reply == ROBOT_REPLY_STR:
            robot_reply_person(msg)
        else:
            itchat.send_msg(reply, msg['FormUserName'])

    count_group_msg(chart_room_name, nick_name)


def robot_reply_person(msg):
    '''
    机器人自动回复微信好友的消息
    :param msg: 好友发送过来的消息
    :return:
    '''
    type = msg['Type']
    from_user_name = msg['FromUserName']
    if type == 'Text':
        reply = TuLingRobot.get_text_reply(msg['Text'])
    elif type == 'Picture':
        path = PICTURE_DIR + '//' + msg['FileName']
        (msg['Text'])(path)
        reply = TuLingRobot.get_picture_reply(path)
    elif type == 'Recording':
        path = RECORDING_DIR + '//' + msg['FileName']
        (msg['Text'])(path)
        reply = [{'values': {'text': '你发的我听不懂啊'}, 'groupType': 0, 'resultType': 'text'}]
    else:
        reply = [{'values': {'text': '你发的我看不懂啊'}, 'groupType': 0, 'resultType': 'text'}]
        pass
    for r in reply:
        text = r['values'][r['resultType']]
        itchat.send_msg(text, from_user_name)


def robot_reply_group(msg):
    '''
    机器人自动回复微信群的消息
    :param msg: 收到的群消息
    :return:
    '''
    type = msg['Type']
    from_user_name = msg['FromUserName']
    if type == 'Text':
        reply = TuLingRobot.get_text_reply(msg['Text'])
    elif type == 'Picture':
        path = PICTURE_DIR + '//' + msg['FileName']
        (msg['Text'])(path)
        reply = TuLingRobot.get_picture_reply(path)
    elif type == 'recording':
        path = RECORDING_DIR + '//' + msg['FileName']
        (msg['Text'])(path)
        # itchat.send_video(path, toUserName='filehelper')
        # reply = TuLingRobot.get_recording_reply(path)
        reply = [{'values': {'text': '你发的我听不懂啊'}, 'groupType': 0, 'resultType': 'text'}]
    else:
        reply = [{'values': {'text': '你发的我看不懂啊'}, 'groupType': 0, 'resultType': 'text'}]
    for r in reply:
        text = r['values'][r['resultType']]
        itchat.send_msg(text, from_user_name)


def count_group_msg(chart_room_name, nick_name):
    '''
    统计群内用户的发言频率
    :param chart_room_name:群名
    :param nick_name:发言人的昵称
    :return:
    '''
    if not chart_room_name in GROUP_MSG_DATA:
        count = {}
        count[nick_name] = 1
        GROUP_MSG_DATA[chart_room_name] = count
    else:
        if not nick_name in GROUP_MSG_DATA[chart_room_name]:
            GROUP_MSG_DATA[chart_room_name][nick_name] = 1
        else:
            GROUP_MSG_DATA[chart_room_name][nick_name] += 1


def friends_sex_ratio():
    '''
    获取好友的男女比例
    :return:
    '''
    friends = itchat.get_friends()
    # myUserName = friends[0]['UserName']
    boy = 0  # 1
    girl = 0  # 2
    other = 0  # 0
    for f in friends:
        if f['Sex'] == 0:
            other += 1
        elif f['Sex'] == 1:
            boy += 1
        else:
            girl += 1
    sum = boy + girl + other

    msg = '您共有好友 %d, 男生占比 %f , 女生占比 %f , 其他 %f' % (sum, boy / sum, girl / sum, other / sum)
    itchat.send_msg(msg, toUserName='filehelper')
    x = ['boy', 'girl', 'other']
    y = [boy, girl, other]
    plt.figure(figsize=(7, 6))
    plt.bar(x, y, width=0.35, facecolor='lightskyblue', edgecolor='white')
    plt.xlabel('性别')
    plt.ylabel('数量')
    plt.title('微信好友性别比例')
    for x, y in zip(x, y):
        # 在每个柱上写上数据标注
        plt.text(x, y, '%d' % y, ha='center', va='bottom')
    # plt.show()
    path = PICTURE_DIR + '//sex_ratio.png'
    plt.savefig(path)
    itchat.send_image(path, toUserName='filehelper')


def friends_region_ratio(max_show):
    '''
    获取各个地区的好友数量，只显示
    :param max_show: 最多显示max_show个地区的好友数量，剩余的好友用其他表示，
    因为显示多了，可能会导致图形堆积在一起
    :return:
    '''
    friends = itchat.get_friends()
    province = {'未知': 0} # key是地区，value是好友数量
    for m in friends:
        p = m['Province']
        if p != '':
            if not Util.check_contain_chinese(p):  # 如果省份不含有中文，那么说明是国外的省份
                p = '国外'
            if p in province:
                province[p] += 1
            else:
                province[p] = 1

        else:
            province['未知'] += 1
    total_num = len(friends)  # 好友总数
    sum = 0  # 好友数量前REGION_MAX_SHOW个的总和
    keys, values = Util.sort_dict(province, sort_type=1)
    for v, i in zip(values, range(max_show-1)):
        sum += v

    # 如果当前好友数量大于可以显示的数量，那么剩余的好友归入其他
    if len(province) > max_show:
        keys[max_show-1] = '其他'
        values[max_show-1] = total_num-sum
    keys = keys[0: max_show]
    values = values[0: max_show]
    plt.figure(figsize=(10, 8))
    plt.bar(keys, values, width=0.35, facecolor='lightskyblue', edgecolor='white')
    # plt.xlabel('省份')
    # plt.ylabel('好友数量')
    plt.title('微信好友省份分布')
    plt.xticks(rotation=45)  # 横坐标标注旋转一定角度
    for x, y in zip(keys, values):
        # 在每个柱上写上数据标注
        plt.text(x, y, '%d' % y, ha='center', va='bottom')
    path = PICTURE_DIR + '/region_ratio.png'
    plt.savefig(path)  # 需要先保存到本地才可以发送
    itchat.send_image(path, toUserName='filehelper')


def get_friends_reply():
    '''
    向文件助手发送所有的好友自动回复
    :return:
    '''
    msg = ''
    for key in FRIENDS_REPLY:
        if FRIENDS_REPLY[key] == '':
            pass
            # msg += '*无自动回复*\n'
        elif FRIENDS_REPLY[key] == ROBOT_REPLY_STR:
            msg += key + ':\n'
            msg += '*机器人回复*\n'
        else:
            msg += key + ':\n'
            msg += '*' + FRIENDS_REPLY[key] + '*\n'
    if msg == '':
        msg = '暂未设置好友自动回复内容'
    itchat.send_msg(msg, toUserName='filehelper')


def get_group_reply():
    '''
    向文件助手发送所有的群自动回复
    :return:
    '''
    msg = ''
    for key in GROUP_REPLY:
        if GROUP_REPLY[key] == '':
            pass
            # msg += '*无自动回复*\n'
        elif GROUP_REPLY[key] == ROBOT_REPLY_STR:
            msg += key + ':\n'
            msg += '*机器人回复*\n'
        else:
            msg += key + ':\n'
            msg += '*' + GROUP_REPLY[key] + '*\n'
    if msg == '':
        msg = '暂未设置群自动回复内容'
    itchat.send_msg(msg, toUserName='filehelper')

def set_friends_reply():
    pass


def send_remind():
    '''
    向用户发送提示信息
    :return:
    '''
    remind_msg = '输入以下数字获取相关数据\n'
    for key in REMIND_MSG_MAP:
        remind_msg += '%d %s' % (key, REMIND_MSG_MAP[key])
        remind_msg += '\n'
    itchat.send_msg(remind_msg, toUserName='filehelper')
    path = CH.get_path(MYSELF_MESSAGE)
    itchat.send_file(path, toUserName='filehelper')


def update_reply_content():
    '''
    从配置文件更新回复内容
    :return:
    '''
    '''微信好友'''
    CH.init_friends(itchat.get_friends())  # 初始化配置文件，并加载到当前全局变量中
    # myself = itchat.get_friends(update=True)[0]
    # my_nick_name = myself['NickName']
    global FRIENDS_REPLY
    FRIENDS_REPLY = CH.get_all_friends_reply(MYSELF_MESSAGE)

    '''微信群'''
    CH.init_group(MYSELF_MESSAGE, itchat.get_chatrooms())
    global GROUP_REPLY
    GROUP_REPLY = CH.get_all_group_reply(MYSELF_MESSAGE)


def modify_friends_auto_reply():
    '''
    打开或者关闭好友自动回复功能
    :return:
    '''
    global IS_OPEN_FRIENDS_AUTO_REPLY
    IS_OPEN_FRIENDS_AUTO_REPLY = not IS_OPEN_FRIENDS_AUTO_REPLY
    if IS_OPEN_FRIENDS_AUTO_REPLY:
        text = '好友自动回复功能已打开'
        itchat.send_msg(text, toUserName='filehelper')
        get_friends_reply()
    else:
        text = '好友自动回复功能已关闭'
        itchat.send_msg(text, toUserName='filehelper')


def modify_group_auto_reply():
    '''
    打开或者关闭群消息自动回复功能
    :return:
    '''
    global IS_OPEN_GROUP_AUTO_REPLY
    IS_OPEN_GROUP_AUTO_REPLY = not IS_OPEN_GROUP_AUTO_REPLY
    if IS_OPEN_GROUP_AUTO_REPLY:
        text = '群自动回复功能已打开'
        itchat.send_msg(text, toUserName='filehelper')
        get_group_reply()
    else:
        text = '群自动回复功能已关闭'
        itchat.send_msg(text, toUserName='filehelper')




def get_group():
    group = itchat.get_chatrooms()
    for gr in group:
        print(gr)


def init_gloabl():
    '''
    初始化全局变量，因为不放到函数里面，全局变量总是没有初始化
    :return:
    '''
    # GROUP_MSG_DATA = {}  # 记录群消息的发言频率
    global REMIND_MSG_MAP
    REMIND_MSG_MAP = {1: '好友性别比例', 2: '好友地区分布', 3: '增加\\修改好友自动回复',
                      4: '查看好友自动回复信息', 5: '增加\\修改群自动回复', 6: '查看群自动回复信息',
                      7: '打开\\关闭好友自动回复', 8: '打开\\关闭群自动回复', 9: '统计群消息'}  # 提示消息
    global BASE_DIR
    BASE_DIR = 'wechat//wechatHelper'
    global PICTURE_DIR
    PICTURE_DIR = './/picture'
    global RECORDING_DIR
    RECORDING_DIR = './/recording'
    global REGION_MAX_SHOW
    REGION_MAX_SHOW = 15  # 显示地区的时候最大显示量，因为显示过多，会导致x轴的标签叠加在一起
    global CH
    CH = ConfigHandle()
    global FRIENDS_REPLY
    FRIENDS_REPLY = {}
    global GROUP_REPLY
    GROUP_REPLY = {}
    global ROBOT_REPLY_STR
    ROBOT_REPLY_STR = '0'
    global IS_OPEN_FRIENDS_AUTO_REPLY
    IS_OPEN_FRIENDS_AUTO_REPLY = True  # 是否打开好友自动回复
    global IS_OPEN_GROUP_AUTO_REPLY
    IS_OPEN_GROUP_AUTO_REPLY = True  # 是否打开群自动回复
    global MYSELF_MESSAGE
    MYSELF_MESSAGE = ''  # 用户的个人微信信息
    global FILE_PATH
    FILE_PATH = 'wechat//wechatHelper'


def create_dir():
    '''
    创建一些目录
    :return:
    '''
    # 创建图片文件夹
    if not os.path.exists(PICTURE_DIR):
        os.mkdir(PICTURE_DIR)

    # 创建音频文件夹
    if not os.path.exists(RECORDING_DIR):
        os.mkdir(RECORDING_DIR)


def init():
    '''
    一些初始化服务器的操作
    :return:
    '''
    global MYSELF_MESSAGE
    MYSELF_MESSAGE = itchat.get_friends()[0]

    path = ARGS.base_dir + '//' + ARGS.pro_dir
    global CH
    CH = ConfigHandle(path)

    update_reply_content()  # 更新自动回复的信息
    send_remind()  # 向用户发送提示信息


def start():
    # itchat.login(picDir='static/qrcode.png')
    # itchat.auto_login(hotReload=True)
    # 首先要切换到工作目录
    path = ARGS.base_dir + '//' + ARGS.pro_dir
    os.chdir(path)
    create_dir()
    itchat.login(picDir=ARGS.img_path)
    # uuid = itchat.get_QRuuid()
    # itchat.get_QR(uuid=uuid, picDir=ARGS.img_path)
    init()

    # init_gloabl()
    itchat.run()



if __name__ == '__main__':
    # os.chdir('wechat/wechatHelper/')
    start()


