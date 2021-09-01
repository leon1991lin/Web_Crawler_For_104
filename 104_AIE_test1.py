# import os
# import ssl
# # used to fix Python SSL CERTIFICATE_VERIFY_FAILED
# if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
#     ssl._create_default_https_context = ssl._create_unverified_context
# ####################################
import requests, os , json, time
from bs4 import BeautifulSoup

#建立移除特殊字元但保留換行符號的函式
def remove_w(text):
    import re
    tmp1 = re.sub("\n+","ZZZ",text) #要保留換行符號，故先置換為其他字元
    tmp2 = re.sub("\W+"," ",tmp1)
    result = re.sub("[Z][Z][Z]","\n",tmp2)
    return result

#透過 requests 取得網頁原始碼
index = 1
for i in range(1,6): #設定預計的爬取頁數，目前先設置為5頁
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
               "Referer": "https://www.104.com.tw/job"}
    url = 'https://www.104.com.tw/jobs/search/?ro=0&keyword=AI工程師&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&order=1&asc=0&page={}&mode=s&jobsource=2018indexpoc'.format(i)
    res = requests.get(url, headers = headers)
    soup = BeautifulSoup(res.text,'html.parser')

    #取得公司名稱

    comp =soup.findAll('ul',class_ = 'b-list-inline b-clearfix')
    comp_name = [remove_w(i.find("a").text).split("\n")[0] for i in comp]

    #取得職稱

    job = soup.findAll('a',class_ = 'js-job-link')
    job_titles = [ remove_w(i.text) for i in job]

    #取得工作內容，須進入每個職缺的頁面內才能爬取到完整工作內容
    #每個職缺的網址差別在職缺ID，故先取得每個職缺頁面的ＩＤ

    job_info = []
    jodLinks = soup.select("a.js-job-link")
    for jobLink in jodLinks:
        jobId = jobLink["href"].split("/")[-1].split("?")[0]
        jubUrl = "https://www.104.com.tw/job/ajax/content/{}".format(jobId)

        #　requests　取得　json檔
        resJob = requests.get(jubUrl,headers = headers)
        jobJson = json.loads(resJob.text)
        jobDet = jobJson["data"]['jobDetail']['jobDescription']
        job_info.append(jobDet)
        time.sleep(2)

#############################################
#輸出個別職缺資料，存為TXT檔

    if not os.path.exists("C:\\Users\\Tibame\\PycharmProjects\\PyETL_HW_104\\jobInfo"):
        os.mkdir("C:\\Users\\Tibame\\PycharmProjects\\PyETL_HW_104\\jobInfo")

    for com, opening, info in zip(comp_name,job_titles,job_info):
        with open ("C:\\Users\\Tibame\\PycharmProjects\\PyETL_HW_104\\jobInfo\\{}-{}-{}.txt".format(index,com,opening),"w",encoding = "utf-8") as w:
            w.write(info)
        index += 1

        
print("Finish!")
