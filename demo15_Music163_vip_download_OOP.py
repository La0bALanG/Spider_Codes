# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/16
@file: demo15_Music163_vip_download_OOP.py.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:抓取网易云音乐任意付费音乐，下载到本地保存
"""

import requests
import random
import base64
import json
import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from fake_useragent import UserAgent



"""

实现思路

1.目标：
    1.输入任意歌手或歌曲名称，列出所有查询结果；
    2.自行选择其中想要的结果下载至本地
    3.搜索结果包含可能的vip付费歌曲，也要实现下载功能

2.需求实现所需突破的难点：
    1.网易云歌曲播放的XHR异步加载数据包其URL请求参数form_data的加密破解；
    2.具体每一首歌曲的歌曲id(网易云每一首歌都有一个单独的歌曲id，获取该id，用于构造上述加密破解)
    
3.请求、参数及其加密分析
    1.歌曲文件请求
        请求接口(URL):https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token=
        请求方式：POST
        请求参数：parmas和encSecKey
        参数加密：AES及RSA加密算法
        具体实现：详见加密算法实现及其注解
    2.歌曲id请求：
        请求接口：https://music.163.com/weapi/cloudsearch/get/web?csrf_token=
        请求方式:POST
        请求参数：parmas和encSecKey
        参数加密：AES及RSA加密算法
        具体实现：详见加密算法实现及其注解

附经过js逆向分析后的js加密算法代码：

var bVZ7S = window.asrsea(JSON.stringify(i9b), bqN9E(["流泪", "强"]), bqN9E(Wx4B.md), bqN9E(["爱心", "女孩", "惊恐", "大笑"]));
            e9f.data = j9a.cs0x({
                params: bVZ7S.encText,
                encSecKey: bVZ7S.encSecKey
            })



!function() {
    function a(a) {
        var d, e, b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", c = "";
        for (d = 0; a > d; d += 1)
            e = Math.random() * b.length,
            e = Math.floor(e),
            c += b.charAt(e);
        return c
    }
    function b(a, b) {
        var c = CryptoJS.enc.Utf8.parse(b)
          , d = CryptoJS.enc.Utf8.parse("0102030405060708")
          , e = CryptoJS.enc.Utf8.parse(a)
          , f = CryptoJS.AES.encrypt(e, c, {
            iv: d,
            mode: CryptoJS.mode.CBC
        });
        return f.toString()
    }
    function c(a, b, c) {
        var d, e;
        return setMaxDigits(131),
        d = new RSAKeyPair(b,"",c),
        e = encryptedString(d, a)
    }
    function d(d, e, f, g) {
        var h = {}
          , i = a(16);
        return h.encText = b(d, g),
        h.encText = b(h.encText, i),
        h.encSecKey = c(i, e, f),
        h
    }
    function e(a, b, d, e) {
        var f = {};
        return f.encText = c(a + e, b, d),
        f
    }
    window.asrsea = d,
    window.ecnonasr = e
}();

4.实现步骤：
    1.调用加密算法类模拟js加密过程将parmas及encSecKey完成加密并放入form_data格式返回。其中留下接口：参数d，用于请求歌曲id和请求歌曲文件时的不同传参。
    2.请求歌曲id
    3.请求歌曲文件
    4.下载保存至本地


测试数据：一次XHR接口请求的response:

{
  "data": [
    {
      "id": 1356499052,
      "url": "http://m10.music.126.net/20200917152750/c6a5d97c3aa529eeb5f08237fae3f412/ymusic/030f/0659/0652/4eeba3ec67139de17412186b850c3a70.mp3",
      "br": 128000,
      "size": 3971074,
      "md5": "4eeba3ec67139de17412186b850c3a70",
      "code": 200,
      "expi": 1200,
      "type": "mp3",
      "gain": 0.0,
      "fee": 8,
      "uf": null,
      "payed": 0,
      "flag": 64,
      "canExtend": false,
      "freeTrialInfo": null,
      "level": "standard",
      "encodeType": "mp3"
    }
  ],
  "code": 200
}




"""



class EncryptAlgorithm(object):
    """
    加密算法类:处理form_data所需的parmas及encSecKey参数的加密
    :return:form_data

    """

    def __init__(self):

        #固定字符库，用于从中随机抽取字符完成加密
        self.__init_str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        self.__init_num = '0102030405060708'

        #模拟参数d所需的三个固定参数
        #模拟参数e
        self.__e = '010001'

        #模拟参数f
        self.__f = '00e0b509f6259df8642dbc35662901477df22677ec152b' \
                       '5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417' \
                       '629ec4ee341f56135fccf695280104e0312ecbda92557c93' \
                       '870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b' \
                       '424d813cfe4875d3e82047b97ddef52741d546b8e289dc69' \
                       '35b3ece0462db0a22b8e7'

        #模拟参数g
        self.__g = '0CoJUm6Qyw8W8jud'

    def __make16randomstr(self):
        """
        # 产生16位随机字符, 对应函数a
        :return:
        """
        # generated_string = get_random_bytes(16)
        # return generated_string

        generate_string = random.sample(self.__init_str, 16)
        generated_string = ''.join(generate_string)
        return generated_string

    def __AES_encrypt_alogorithm(self, clear_text, key):
        """
                AES加密, 对应函数b
                :param clear_text: 需要加密的数据
                :return:
                """
        # 数据填充:传入的所需加密数据进行填充处理并重写clear_text变量

        clear_text = pad(data_to_pad=clear_text.encode(), block_size=AES.block_size)
        key = key.encode()
        iv = self.__init_num.encode()
        aes = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
        cipher_text = aes.encrypt(plaintext=clear_text)
        # 字节串转为字符串
        cipher_texts = base64.b64encode(cipher_text).decode()
        return cipher_texts

    def __RSA_encrypt_alogorithm(self, i, e, n):
        """
        RSA加密, 对应函数c
        :param i:
        :return:
        """
        # num = pow(x, y) % z
        # 加密C=M^e mod n
        num = pow(int(i[::-1].encode().hex(), 16), int(e, 16), int(n, 16))
        result = format(num, 'x')
        return result

    def __get_encrypt_result(self, input_text):
        """
        对应函数d
        :param input_text:
        :return:
        """
        i = self.__make16randomstr()
        # print(i) #输出一个生成的16位随机字符串

        encText = self.__AES_encrypt_alogorithm(input_text, self.__g)
        encText = self.__AES_encrypt_alogorithm(encText, i)
        encSecKey = self.__RSA_encrypt_alogorithm(i, self.__e, self.__f)
        from_data = {
            'params': encText,
            'encSecKey': '0' + encSecKey
        }
        # print(encText) #输出encText加密结果
        # print(len(encText)) #返回其长度，验证是否正确
        # print(encSecKey) #输出encSecKey加密结果
        # print(len(encSecKey)) #验证其长度是否正确
        return from_data

    def return_form_data(self,input_text):
        return self.__get_encrypt_result(input_text)


# res = EncryptAlgorithm().display('{"ids":"[1456238192]","level":"standard","encodeType":"aac","csrf_token":""}')
# print(res)
#


class CrackMusic163VipMusicSpider(object):
    '''
    爬虫请求类：负责请求所需数据
    :return:response

    '''

    def __init__(self):

        self.__headers = {
            'User-Agent':UserAgent().random
        }

    #请求数据(响应内容)
    def get_html(self,url,method = 'GET',form_data = None):
        try:
            if method == 'GET':
                response = requests.get(url=url,headers = self.__headers)
            else:
                response = requests.post(url=url,data=form_data,headers=self.__headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except Exception as err:
            print(err)
            return '请求异常'

    def parse_text(self,text):
        #1.将得到response(json格式数据)转为Python字典
        ids_list = json.loads(text)['result']['songs']
        info_list = []
        for id_info in ids_list:
            song_name = id_info['name']
            id = id_info['id']
            singer = id_info['ar'][0]['name']
            info_list.append([id,song_name,singer])
        return info_list

    def save_music(self,music_url,id_info):
        dir = 'D:\musicSpider'
        if not os.path.exists(dir):
            os.mkdir(dir)
        filename = id_info[1] + '-' + id_info[2]
        response = requests.get(music_url,headers=self.__headers)
        with open(os.path.join(dir,filename) + '.mp3','wb') as f:
            f.write(response.content)
            print('下载完毕！')





def test():
    #创建加密工厂
    ea = EncryptAlgorithm()
    #创建爬虫工厂
    crack_spider = CrackMusic163VipMusicSpider()

    #接口URL
    song_url = 'https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token='
    id_url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='

    #获取歌曲id的加密模拟所需的d参数
    id_d = {
        "hlpretag": "<span class=\"s-fc7\">",
        "hlposttag": "</span>",
        "s": input("请输入歌名或歌手: "),
        "type": "1",
        "offset": "0",
        "total": "true",
        "limit": "30",
        "csrf_token": ""
    }
    #根据id的d参数构造加密后的form_data
    id_form_data = ea.return_form_data(json.dumps(id_d))
    #发请求获取歌曲id响应
    id_text = crack_spider.get_html(id_url,method='POST',form_data=id_form_data)

    #解析相应内容，摘出歌曲id，歌名，歌手名
    id_infos = crack_spider.parse_text(id_text)
    music_info = []

    #多条记录，for循环遍历依次取出歌曲id
    for id_info in id_infos:
        #请求歌曲的加密模拟所需的d参数
        music_d = {
            #ids根据上一步摘出的id值获取
            "ids": str(id_info[0]),
            "level": "standard",
            "encodeType": "aac",
            "csrf_token": ""
        }
        #根据歌曲的d参数构造加密后的form_data
        music_form_data = ea.return_form_data(json.dumps(music_d))
        #发请求获取歌曲响应
        music_reps = crack_spider.get_html(song_url,method='POST',form_data=music_form_data)
        #解析出响应内容中的歌曲下载的URL，再加上歌曲名称，一同作为参数穿给保存文件方法
        crack_spider.save_music(json.loads(music_reps)['data'][0]['url'],id_info[1])
    print(music_info)

    # 无关测试
# print(type(id_text))
    # print(res)
    # print(type(res))
    # music_d = {
    #     "ids": "[1334327077]",
    #     "level": "standard",
    #     "encodeType": "aac",
    #     "csrf_token": ""
    # }
    # music_form_data = ea.display(json.dumps(music_d))
    # music_reps = crack_spider.display(song_url,method='POST',form_data=music_form_data)
    # print(music_reps)
    # print(type(music_reps))

if __name__ == '__main__':
    test()