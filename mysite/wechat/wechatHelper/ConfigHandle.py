import configparser
import os
import Util


class ConfigHandle:
    def __init__(self, path='.'):
        self.confFilePath = 'config'
        self.conf_name_parm = 'Uin'  # 用户微信号对应的id，据说是不会改变，所以暂时用这个参数，
                                        # 如果用用户昵称做配置文件名的话，在send_file的时候会有问题
        self.friend_section = "friends_auto"
        self.group_section = 'group_auto'
        self.conf = configparser.ConfigParser()
        os.chdir(path)  # 切换到工作目录
        if not os.path.exists(self.confFilePath):
            os.mkdir(self.confFilePath)

    def init_friends(self, friends):
        '''
        初始化好友自动回复配置文件，如果当前用户第一次登录，那么所有的好友都默认设置为不自动回复
        :param friends: 用户的所有微信好友
        :return:
        '''
        self.conf.clear()  # 在开始这次的set之前首先把之前的配置情况，否则会干扰这次的写入
        conf_name = friends[0][self.conf_name_parm]
        conf_name = str(conf_name)
        path = self.confFilePath + '//' + conf_name + '.txt'
        self.conf.read(path)
        s = self.conf.sections()
        section = self.friend_section
        if not section in s:
            self.conf.add_section(section)
        keys = []
        items = self.conf.items(section)
        for item in items:
            keys.append(item[0])
        for i in range(1, len(friends)):
            # 这里有些字符会干扰配置文件的读写，所以要处理一下
            remark_name = Util.standard_name(friends[i]['RemarkName'])
            nick_name = Util.standard_name(friends[i]['NickName'])
            key = remark_name + '—' + nick_name
            if not key in keys:
                self.conf.set(section, key, '')
        with open(path, 'w') as fw:  # 循环写入
            self.conf.write(fw)
        # self.conf.clear()

    def init_group(self, myself, group):
        '''
        初始化群自动回复配置文件，如果当前用户第一次登录，那么所有的群都默认设置为不自动回复
        :param myself: 用户的个人信息
        :param group: 用户的所有群
        :return:
        '''
        self.conf.clear()  # 在开始这次的set之前首先把之前的配置情况，否则会干扰这次的写入
        conf_name = myself[self.conf_name_parm]
        conf_name = str(conf_name)
        path = self.confFilePath + '//' + conf_name + '.txt'
        self.conf.read(path)
        s = self.conf.sections()
        section = self.group_section
        if not section in s:
            self.conf.add_section(section)
        keys = []
        items = self.conf.items(section)
        for item in items:
            keys.append(item[0])
        for i in range(0, len(group)):
            # 这里有些字符会干扰配置文件的读写，所以要处理一下
            key = Util.standard_name(group[i]['NickName'])
            if key == '':
                key = '无群名'
            if not key in keys:
                self.conf.set(section, key, '')
        with open(path, 'w') as fw:  # 循环写入
            self.conf.write(fw)

    def get_all_friends_reply(self, myself):
        '''
        获取当前用户的所有好友的自动回复
        :param myself: 当前用户的个人信息
        :return: 以dict形式返回用户的所有好友的自动回复
        '''
        conf_name = myself[self.conf_name_parm]
        conf_name = str(conf_name)
        path = self.confFilePath + '//' + conf_name + '.txt'
        self.conf.read(path)
        section = self.friend_section
        items = self.conf.items(section)
        res = {}
        for item in items:
            res[item[0]] = item[1]
        return res

    def get_all_group_reply(self, myself):
        '''
        获取当前用户的所有群的自动回复
        :param myself: 当前用户的个人信息
        :return: 以dict形式返回用户的所有好友的自动回复
        '''
        conf_name = myself[self.conf_name_parm]
        conf_name = str(conf_name)
        path = self.confFilePath + '//' + conf_name + '.txt'
        self.conf.read(path)
        section = self.group_section
        items = self.conf.items(section)
        res = {}
        for item in items:
            res[item[0]] = item[1]
        return res

    def get_specific_friends_reply(self, seciton, name):
        path = self.confFilePath + '//' + self.friend_conf
        self.conf.read(path)
        reply = self.conf.get(seciton, name)
        return reply

    def set_friends_reply(self, section, sets):
        replys = self.get_auto_friends_reply()
        path = self.confFilePath + '//' + self.friend_conf
        self.conf.read(path)
        section = sets['nick_name']
        if sets['remark_name'] != '':
            section = sets['remark_name']
        else:
            section = sets['nick_name']
            if section in replys:
                # EDIT
                pass  # 防止报错
            else:
                # ADD
                self.conf.add_section(section)  # 添加conf节点
            try:
                for s in sets:
                    self.conf.set(section, s[0], s[1])
                with open(path, 'w') as fw:  # 循环写入
                    self.conf.write(fw)
            except:
                return False
            return True

    def get_path(self, myself):
        conf_name = myself[self.conf_name_parm]
        conf_name = str(conf_name)
        path = path = self.confFilePath + '//' + conf_name + '.txt'
        return path