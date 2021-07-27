import json, re, sys, uuid, requests, youtube_dl, logging, time
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
        print('->下载 ', url[0])
        filename = str(uuid.uuid4())[0:8]   #经充分测试，如果保留原视频title明，那下载下来的文件名可能包含特殊字符，有可能导致邮件附件发送失败
        ydl_opts = {                        #替换掉特殊字符也一样，原因未知，因此通过生成uid做文件名
            'format': 'worstaudio/worst',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '64',
            }],
            'outtmpl':  filename + '.m4a'
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url[1]])
        except Exception as e:
            fails.append(url)
            logging.error(e); print(e)
            continue
        else:
            files.append([url[0], url[1], filename + '.mp3'])

        #增加间隔时间，防止过频访问
        time.sleep(10)  
        
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
        urls = geturls(config['config']['urls'])
        urls = self.urlp.filter(urls)
        if len(urls) > 0 and (self.startup == False):
            files, fails = urltomp3(urls)
            self.urlp.remove(fails)
            for file in files:   #为防止附件过大，mp3邮件单个发送  file=[tilte, link, videoname]
                content = '【1】'+ file[0] + ' ' + file[1] + '\n'
                sendmail('YouTube订阅！', [file[2]], config, content)
                deleltefiles([file[2]])
        else:
            print('->油管无新订阅，不发送！\n\n\n')
        self.urlp.dump()
        self.startup = False

if __name__ == '__main__':
    zzh_subs_youtube = subs_youtube('subs_youtube.config', 'subs_youtube.json')
    zzh_subs_youtube.subs()


   




