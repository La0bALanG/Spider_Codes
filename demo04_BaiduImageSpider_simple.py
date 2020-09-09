
#导入所需模块
import requests
from urllib import parse
import re
import os
from lxml import etree
#------第一步：确定目标url，伪造headers，为正式发起请求作准备------
# 1.确定基本url格式
# 即你要向哪个网站发起请求，本案例中，我们要在百度图片网站上搜索明星图片
# 即需要向百度图片网站发起请求
url = 'https://image.baidu.com/search/index?tn=baiduimage&word={}'

# 2.明确目标url基本格式
# 目标关键词：你想搜谁的图片，就输入谁的名字，该关键词最后要拼接进基本url
word = input('你想要谁的照片？请输入:')
# 3.因为直接输入的字符类型为字符串，并不能直接使用，所以需要转unicode码
# 转unicode码
params = parse.quote(word)

# 4.拼接得到最终请求url
url = url.format(params)
# 5.伪造headers：说白了就是骗浏览器“我们不是机器，我们是人～”
headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

#------第二步：发请求------
#向网站正式发起请求，获取页面数据，转为字符文本
html = requests.get(url=url,headers=headers).text

#------第三步：数据筛选
# 响应结果中的html文本内容很多，需要从中找出我们所需的图片url文本并采用合适的方式保存以备后续使用
# 筛选、解析方式很多，介绍两种基本方式
# 1.使用xpath匹配
# dom = etree.HTML(html)
# link_list = dom.xpath('//ul[@class="imglist clearfix pageNum0"]/li[@class="imgitem"]/@data-thumburl')
# 从得到的响应结果中可以看到，目标图片的路径不在html元素的属性或内容中，而是在js的传参数据中
# 结论：此案例中无法使用xpath解析，因为解析出来的html元素中不存在目标图片路径，xpath解析内容为空
# 2.使用正则匹配
# 找到js中存在的目标图片的路径，因为此时js代码也是属于响应内容的文本之一，可以使用正则表达式进行匹配。
# 编写正则表达式，采用compile方法匹配，参数1：正则表达式，参数2：匹配包括换行在内的所有字符
# p = re.compile('"thumbURL":"(.*?)"',re.S)
# link_list = p.findall(html)
# 直接使用findall()
link_list = re.findall('"thumbURL":"(.*?)"',html)
# 使用search()方法
# link_list = re.search('"thumbURL":"(.*?)"',html).group(1)

# # 验证是否获取到url
# print(link_list)
# link_list: ['xxx.jpg','xxx.jpg']

#------第四步：对目标图片发起请求并将响应内容进行持久化存储
# 1.创建图片保存路径，保存图片到本地
directory = '/home/anwc/桌面/{}/'.format(word)

#os.path.exists(directory)表示目录存在
#如果目录不存在(即先判断是否已存在目标目录)
if not os.path.exists(directory):
    # 创建空目录并命名
    os.makedirs(directory)
# 2.循环的对目标图片发起请求获得响应
for link in link_list:
    # 请求图片获得响应
    html = requests.get(url=link, headers=headers).content
    # 拼接我们想要的图片文件名(包含路径)
    filename = directory + '{}.jpg'.format(link[-24:-15])
    # 写入文件
    with open(filename, 'wb') as f:
        f.write(html)
    f.close()
    print(filename, '下载成功')