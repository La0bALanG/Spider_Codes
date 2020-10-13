
import re

s_url = '新式“火腿圈蛋”，好看又好吃#自制美食 @抖音小助手  https://v.douyin.com/Jf2NMTv/ 复制此链接，打开抖音，直接观看视频！'
s = re.findall('(https?://[^\s]+)', s_url)[0]
print(s)