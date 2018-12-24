from django.shortcuts import render

# Create your views here.
import os
import time
from mysite import settings

def show_static(request):
    print(request.META['REMOTE_ADDR'])  # 客户端ｉｐ
    return render(request, 'index.html')


def show_qr(request):
    remote_addr = request.META['REMOTE_ADDR']
    print(remote_addr)

    img_path = 'static//%s.png' % remote_addr
    if os.path.exists(img_path):
        os.remove(img_path)
    app_dir = 'wechat//wechatHelper'
    img_path = '..//..//' + img_path  # 这个是要传入的参数，因为在WeChatHelper.py文件中要切换目录，所以这里要向上跳两个目录级别
    cmd = 'python3 wechat/wechatHelper/WeChatHelper.py --base_dir %s --pro_dir %s --img_path %s &' \
          % (settings.BASE_DIR, app_dir, img_path)
    os.system(cmd)
    time.sleep(3)  # 这里必须要给时间去下载二维码
    context = {}
    context['url'] = '/static/%s.png' % remote_addr
    return render(request, 'showqr.html', context)