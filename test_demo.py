# #
# # import requests
# # from selenium import webdriver
# #
# # url = 'https://www.dytt8.net/html/gndy/index.html'
# # headers = {
# #             'Connection': 'close',
# #             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
# #         }
# #
# # driver = webdriver.Chrome()
# # driver.get(url)
# #
# # s = driver.page_source
# # print(s)
# res =[['国内电影', '日韩影片', '欧美影片', '2020精品专区'], ['/html/gndy/china/index.html', '/html/gndy/rihan/index.html', '/html/gndy/oumei/index.html', '/html/gndy/dyzz/index.html']]
#
# ls = [4,6,7,23]
# num = 4
# # for sec in res[1]:
# #     for i in ls:
# #         for j in range(1,num + 1):
# #             second_url = 'https://www.dytt8.net' + sec[0:-10] + 'list_{}_{}.html'.format(i,j)
# #             print(second_url)
# for j in range(1,5):
#     for (sec,i) in zip(res[1],ls):
#         second_url = 'https://www.dytt8.net' + sec[0:-10] + 'list_{}_{}.html'.format(i,j)
#         print(second_url)
# # for sec in res[1]:
# #     second_url = 'https://www.dytt8.net' + sec[0:-10]
# #     for i in ls:
# #         second_url += 'list_{}_'.format(i)
# #         for j in range(1,num + 1):
# #             second_url += '{}.html'.format(j)
# #             print(second_url)



l1 = [1,2,3,4]
l2 = [2,3,4,5]
print(zip(l1,l2))