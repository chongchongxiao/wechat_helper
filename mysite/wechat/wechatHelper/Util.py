import re
import random
def check_contain_chinese(check_str):
    '''
    判断一个字符串中是否含有中文字符
    :param check_str: 待判断的字符串
    :return: true表示含有中文字符
    '''
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
        else:
            return False

def sort_dict(dict, sort_type):
    '''
    对字典类型进行排序
    :param dict: 待排序的字典
    :param sort_type: 排序规则，0表示按key进行排序，1表示按value进行排序
    :return: 排序后的两个链表，分别是keys和values
    '''
    lt = sorted(dict.items(), key=lambda x: x[sort_type], reverse=True)
    # 排序之后是list(tuple(key,value))的类型
    data = {}
    keys = []
    values = []
    for m in lt:
        keys.append(m[0])
        values.append(m[1])
    return [keys, values]


def standard_name(name):
    '''
    因为昵称或者备注里有一些字符会干扰读配置文件，所以需要过滤一下
    :param name: 待处理的名字
    :return: 处理后的名字
    '''
    char = [':', '=', ' ']
    for ch in char:
        name = name.replace(ch, '')

    name = name.lower()

    return name


def get_quanpin(str):
    '''
    根据中文生成全拼
    :param str:传入的中文
    :return:中文全拼，如果没有中文，那么随机生成一个10位的随机字符串
    '''
    letter = list(range(ord('a'), ord('z')))
    Letter = list(range(ord('A'), ord('Z')))
    letter += Letter
    res = ''
    for r in str:
        for ch in r:
            if ord(ch) in letter:
                res += ch
    if res != '':
        return res
    for i in range(10):
        num =random.randint(0, 9)
        res += chr(num+ord('a'))
    return res



def remove_BOM(config_path):
    '''
    文件在用其他软件打开之后，会增加一个BOM头部，例如我用wps打开并修改保存后，会在文件头部加上\ufeff
    这会影响configparser读取配置文件，所以在这里去掉BOM头部
    :param config_path:配置文件路径
    :return:去掉BOM头部的配置文件
    '''
    # content = open(config_path).read()
    # content = re.sub(r"\xfe\xff", "", content)
    # content = re.sub(r"\xff\xfe", "", content)
    # content = re.sub(r"\xef\xbb\xbf", "", content)
    # open(config_path, 'w').write(content)

    # 这里用utf-8方式读取会带有\ufeff,但是用utf-8-sig读取就没有，所以用这种编码格式读取一次再重新写入来去掉\ufeff
    f = open(config_path, encoding='UTF-8-sig')
    con = f.read()
    f.close()
    f = open(config_path, 'w')
    f.write(con)
    f.close()
