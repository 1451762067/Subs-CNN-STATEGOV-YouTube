from __future__ import unicode_literals
import json, re, sys, requests, youtube_dl, logging
import time

from subs_utils import getconfig, sendmail, deleltefiles, datapool
requests.packages.urllib3.disable_warnings()

'''
此文件除了依赖上面的import包外，还需要安装音视频转换工具,ffmpeg，
下载地址：https://www.gyan.dev/ffmpeg/builds/ windows server2007上工作良好
安装好之后将几个exe文件拷贝至系统目录即可，或者设置PATH
Python使用os.system调用该命令进行格式转换
或者搜索'ffmpeg windows'
'''

'''
下载mp3音频
'''
def urltomp3(urls:list):
    files = []
    fails = []
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
            fails.append(url)
            logging.error(e); print(e)
            continue
        else:
            files.append(url[0] + '.mp3')

        time.sleep(10)  #增加间隔时间，防止过频访问

    return files, fails

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
            logging.error(e); print(e)
            continue

        if resp.ok:
            print('ok')
            res = re.findall(r'(\{\"responseContext\".+?\}\]\}\}\});</script>', resp.text)
            videos =  json.loads(res[0])['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']\
                                        ['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']\
                                        ['contents'][0]['gridRenderer']['items']
            for v in videos:
                if 'gridVideoRenderer' in v.keys():
                    tup= [v['gridVideoRenderer']['title']['runs'][0]['text'],
                          'https://www.youtube.com/watch?v='+ v['gridVideoRenderer']['videoId']]
                    returls.append(tup)
                    # print(tup)
    req.close()
    return returls

class subs_youtube():
    def __init__(self, cfgfile, jsonfile):
        self.urlp = datapool(jsonfile)
        self.urlp.load()
        self.cfgfile = cfgfile
        self.startup = False

    def subs(self):
        config = getconfig(self.cfgfile)
        urls = config['config']['urls']
        urls = geturls(urls)
        urls = self.urlp.filter(urls)
        if len(urls) > 0 and (self.startup == False):
            files, fails = urltomp3(urls)
            print(files)
            print(fails)
            logging.error('before')
            logging.error(str(self.urlp))
            self.urlp.remove(fails)
            logging.error('after')
            logging.error(str(self.urlp))
            for file in files:   #为防止附件过大，mp3邮件单个发送
                # content = ''; cnt = 1
                for url in urls:
                    if file[:-4] == url[0]:
                        content = '【1】'+ url[0] + ' ' + url[1] + '\n'
                        break
                        # cnt = cnt + 1
                sendmail('YouTube订阅！', [file], config, content)

            deleltefiles(files)
            logging.error(str(self.urlp))
            self.urlp.dump()
        else:
            print('->油管无新订阅，不发送！\n\n\n')
        self.urlp.dump()
        self.startup = False

if __name__ == '__main__':
    zzh_subs_youtube = subs_youtube('subs_youtube.config', 'subs_youtube.json')
    zzh_subs_youtube.subs()




