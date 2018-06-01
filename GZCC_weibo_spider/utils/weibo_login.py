# coding:utf-8

import re
import rsa
import json
import base64
import logging
import binascii
import requests
from urllib.parse import quote, unquote

# 日志系统
logger = logging.getLogger(__name__)

# 登录URL
login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'


# 获取cookie
def get_cookie(account, password):
    en_user = base64.b64encode(bytes(quote(account), "utf-8"))
    prelogin_url = '''https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=
    sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.19)''' % en_user
    r = requests.get(prelogin_url)
    pre_data = re.search(r'{.+\}', r.content.decode("UTF-8")).group()
    pre_data = json.loads(pre_data)
    servertime = pre_data['servertime']
    nonce = pre_data['nonce']
    rsakv = pre_data['rsakv']
    pubkey = pre_data['pubkey']
    pubkey = int(pubkey, 16)
    e = int('10001', 16)
    pub = rsa.PublicKey(pubkey, e)

    en_pwd = rsa.encrypt((str(servertime) + '\t' + str(nonce) + '\n' + password).encode("utf-8"), pub)
    en_pwd = binascii.b2a_hex(en_pwd)

    form_data = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '30',
        'useticket': '0',
        'ssosimplelogin': '1',
        'pagerefer': '',
        'vsnf': '1',
        'su': en_user,
        'service': 'miniblog',
        'servertime': servertime,
        'nonce': nonce,
        'pwencode': 'rsa2',
        'rsakv': rsakv,
        'sp': en_pwd,
        'sr': '1440*900',
        'encoding': 'UTF-8',
        'cdult': '3',
        'domain': 'weibo.com',
        'prelt': '0',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META'
    }
    # 获取Session对象
    session = requests.Session()
    r1 = session.post(login_url, data=form_data)
    url2 = re.search('location.replace\(\"(.*?)\"\)', r1.content.decode("gb2312")).group(1)
    retcode = re.search('retcode=(\d+)', unquote(url2)).group(1)
    if retcode == '0':
        logger.warning('Succeed to get cookie of account(%s).' % account)
        r2 = session.get(url2)
        url3 = re.search('location.replace\(\'(.*?)\'\)', r2.content.decode("gb2312")).group(1)
        r3 = session.get(url3)
        return json.dumps(r3.cookies.get_dict())
    else:
        reason = re.search('reason=(.+)$', unquote(url2)).group(1)
        logger.warning('Failed to get cookie of account(%s).Reason:%s.' % (account, reason))
        return None


# 多个cookies
def get_cookies(is_username=False):
    """
    获取cookie
    :param is_username: 是否返回用户名
    :return: 一个或多个list
    """
    # 可以多个用户
    Accounts = {
        '': ''
        # 满足json格式即可
    }
    cookies_list = []
    if is_username is not True:
        for account in Accounts:
            cookie = get_cookie(account, Accounts[account])
            if cookie:
                cookies_list.append(cookie)
        return cookies_list
    else:
        user_list = []
        for account in Accounts:
            cookie = get_cookie(account, Accounts[account])
            if cookie:
                cookies_list.append(cookie)
                user_list.append(account)
        return cookies_list, user_list

