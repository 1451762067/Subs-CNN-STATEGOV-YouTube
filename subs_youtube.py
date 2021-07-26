from __future__ import unicode_literals
import json, re, sys, requests,youtube_dl
from subs_utils import getconfig, sendmail, deleltefiles
requests.packages.urllib3.disable_warnings()

'''
下载mp3音频
'''
def urltomp3(urls:list):
    files= []
    for url in urls:
        # url=(title, link)
        # 替换其中不规范字符
        # filename = re.sub(r'[\\\/\:\*\?\"\<\>\|？“”：]', '_', url[0], count=0, flags=0)
        # filename = url[0]
        ydl_opts = {
            'format': 'worstaudio/worst',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '64',
            }],
            'outtmpl':  url[0] + '.m4a'
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url[1]])
        except Exception as e:
            print(e)
            continue
        else:
            files.append(url[0] + '.mp3')

    return files

'''
下载urls
'''
def geturls(urls:list):
    proxies={
        "http":"http://127.0.0.1:7070",
        "https":"http://127.0.0.1:7070",
    }
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
               'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'}

    returls=[]
    req = requests.Session()
    for url in urls:
        print('->从 %s 下载网页' % (url))
        try:
            # resp = req.get(url, verify=False, headers=headers, proxies=proxies)
            resp = req.get(url, verify=False, headers=headers)
        except Exception as e:
            print(e)
            continue

        if resp.ok:
            print('ok')
            res = re.findall(r'(\{\"responseContext\".+?\}\]\}\}\});</script>', resp.text)
            videos =  json.loads(res[0])['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']\
                                        ['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']\
                                        ['contents'][0]['gridRenderer']['items']
            for v in videos:
                if 'gridVideoRenderer' in v.keys():
                    tup= (v['gridVideoRenderer']['title']['runs'][0]['text'],
                          'https://www.youtube.com/watch?v='+ v['gridVideoRenderer']['videoId'])
                    returls.append(tup)
                    print(tup)
    req.close()
    return returls

'''
过滤掉已发送过的
'''
URLPOOL=[]
def filterUrls(urls: list):
    urlret = []
    for url in urls:
        # 此处判断是否过滤
        if url not in URLPOOL:
            urlret.append(url)
            URLPOOL.append(url)

    return urlret


startup = True
def subs_youtube():
# if __name__ == '__main__':
    config = getconfig('subs_youtube.config')
    urls= config['config']['urls']
    urls = geturls(urls)
    urls = filterUrls(urls)

    global startup
    if len(urls) > 0 and (startup == False):
        files = urltomp3(urls)
        content =''
        cnt = 1
        for url in urls:
            content = content + '【{cnt}】'.format(cnt=cnt) + url[0] + ' ' + url[1] + '\n'
            cnt = cnt + 1
        sendmail('YouTube订阅！', files, config, content)
        deleltefiles(files)
    else:
        print('->油管无新订阅，不发送！\n\n\n')

    startup = False




