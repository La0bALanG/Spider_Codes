# -*- coding:utf-8 _*-
"""
@version:
author:安伟超
@time: 2020/09/07
@file: demo01_baidutieba_simple.py
@environment:virtualenv
@email:awc19930818@outlook.com
@github:https://github.com/La0bALanG
@requirement:1.输入贴吧名称 2.输入起始页 3.输入终止页 4.保存响应的页面内容至txt文档
"""

from urllib import request,parse

"""
思路：
1.分析页面URL规律
2.构造查询参数
3.发起请求获得响应
4.写入文件

"""
"""
1.分析页面URL规律

打开百度贴吧，随便搜索一个吧，进入，提取出URL：

https://tieba.baidu.com/f?kw=%E9%95%BF%E6%B2%99&ie=utf-8&pn=0
https://tieba.baidu.com/f?kw=%E6%9D%8E%E6%AF%85&ie=utf-8&pn=0
...

查找规律：
    1.kw查询关键字，需要实时传参；
    2.pn页码参数，单位50，代表当前第几页
    3.查询参数因为是汉字，传入时需要先转成urlencode编码
    
总结URL基本格式：
https://tieba.baidu.com/f?kw={}&ie=utf-8&pn={}

所以，总结思路如下：
    1.构造基本URL格式
    2.构造查询起始页及终止页页码数
    3.构造查询参数及页码参数
    4.字符串拼接，完成最终URL确定格式
"""

"""

确定URL后：
    1.伪造headers
    2.发起正式请求

"""

"""

获得具体响应内容后：
写入文件

"""

#伪造headers
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
}



#构造基本URL格式
url = 'https://tieba.baidu.com/f?kw={}&ie=utf-8&pn={}'

#构造起始页及终止页
begin = int(input('请输入起始页：'))
end = int(input('请输入终止页：'))
#查询页码数量：end - begin
# page = end - begin

#构造查询参数并转urlencode编码
kw = input('请输入您想搜索的贴吧名称>>>:')
parmas = parse.quote(kw)
#依据页码构造最终n个URL
for page in range(begin,end + 1):
    pn = (page - 1) * 50
    # print(pn)
    finall_url = url.format(parmas,pn)
    #测试URL格式
    # print(finall_url)


    #发请求
    #1.创建请求对象
    print('开始爬取第%d页...'%page)

    reqs = request.Request(url=finall_url,headers = headers)
    #2.发起正式请求并解码请求内容
    resp = request.urlopen(reqs).read()
    # print(resp)

    print('第%d页爬取完成，稍等，马上开始写入文件内容...'%page)
    # 写入文件：

    filename = kw + '吧' + '_第%d页.html'%page
    with open(filename,'wb') as f:
        f.write(resp)

    f.close()
    print('文件写入完毕，开始下一页爬取...')


print('程序结束。')


