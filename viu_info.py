# -*-coding:utf8-*-

import requests
import json
import sys
import random
import re

def getApiAppUrl(s):
    regex = r'"api_app_url": "(.*?)",'
    matches = re.compile(regex, re.X).findall(s)
    
    url = matches[0].replace("\\/", "/").encode().decode('unicode_escape') + r"search/video&language_flag_id=1"

    print(url)
    return url

def loadUserAgents(uafile):
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[:-1])
    random.shuffle(uas)
    return uas

def initHeader():
    uas = loadUserAgents("user_agents.txt")
    head = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh-HK;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    }
    def getHeader():
        ua = random.choice(uas)
        head['User-Agent'] = ua
        return head

    return getHeader

def search(keyword="", proxy=None):
    getHeader = initHeader()
    s = requests.Session()
    s.headers.update(getHeader())

    proxies = None
    if proxy!= None:
        proxies = {'http': proxy, 'https': proxy}        

    searchDataPage = {
        "r": "search",
        "keyword": keyword
    }

    apiKeywords = keyword.split()
    searchDataApi = {
        "keyword" : apiKeywords,
        "limit": 12,
        "page": 1,
        "platform_flag_label": "web",
        "url": ""
    }

    print(searchDataPage, proxies)

    # index
    indexPage = s.get("https://www.viu.com/ott/hk/", proxies=proxies)
    print(proxies)
    # search php
    searchPage = s.get("https://www.viu.com/ott/hk/zh-hk", params=searchDataPage, proxies=proxies)

    # search api
    searchDataApi["url"] = getApiAppUrl(searchPage.text)
    searchDataJson = json.dumps(searchDataApi)
    print(searchDataJson)
    searchRes = s.post('https://www.viu.com/ott/hk/index.php?r=vod/jsonp', json=searchDataApi, proxies=proxies)

    data = json.loads(searchRes.text)

    series = data['data']['series']

    tags = ['cover_image_url', 'category_id', 'product_number', 'status', 'is_movie', 'series_image_url', 'product_image_url', 'synopsis']

    print(type(series))
    if (isinstance(series, (dict,list))):
        for i in range(len(series)):
            for j in range(len(tags)):
                del series[i][tags[j]]
    else:
        series = []
    
    print(series)
    
    return series

def episode(id="", proxy=None):
    getHeader = initHeader()
    s = requests.Session()
    s.headers.update(getHeader())

    proxies = None
    if proxy!= None:
        proxies = {'http': proxy, 'https': proxy}        

    epApiData = {
        "r": "vod/ajax-detail",
        "platform_flag_label": "web",
        "area_id": 1,
        "language_flag_id": 1,
        "product_id": id,
        "ut": 0
    }

    print(epApiData, proxies)

    # ep data api
    epApi = s.get("https://www.viu.com/ott/hk/index.php", params=epApiData, proxies=proxies)

    epData = json.loads(epApi.text)

    seriesName = epData['data']['series']['name']
    epData = epData['data']['series']['product']

    epData_new = {}
    for i in range(len(epData)):
        product_id = epData[i]['product_id']
        number = epData[i]['number']
        link = "https://downsub.com/?url=" + "https://www.viu.com/ott/hk/zh-hk/vod/" + product_id + "/"
        epData_new[number] = [{
            'number' : number,
            'link' : link,
        }]
    
    epData_new['name'] = seriesName

    print(epData_new)

    return epData_new
