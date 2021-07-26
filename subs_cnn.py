import json, re, requests, time
import os

from subs_utils import getconfig, sendmail, deleltefiles, datapool
requests.packages.urllib3.disable_warnings()

'''
获取网页里的连接
'''
def geturls(url: str, keyword: list):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'}

    req = requests.Session()
    resp = req.get(url, verify=False, headers=headers)
    print('->从 %s 下载网页' % (url))
    res = re.search('\{"articleList":\[\{.*\}\]\}', resp.text)
    js= json.loads(res.group())
    urls=[]
    print('->使用正则筛序链接，关键字=', keyword)
    for item in js['articleList']:
        # print('  ', item['uri'])
        for word in keyword:
            if item['uri'].lower().find(word) > -1:
                urls.append('https://edition.cnn.com' + item['uri'])
                print('https://edition.cnn.com' + item['uri'])
                continue

    return urls

'''
网页转pdf
'''
def urltopdf(urls:list):
    import weasyprint
    files=[]
    for url in urls:
        filename = url.split('/')[-2]+ '.pdf'
        files.append(filename)
        print('->下载网页并转成pdf:', url, '\n  文件名:', filename)
        try:
             weasyprint.HTML(url).write_pdf(filename)
        except Exception as e:
            print(e)
        else:
            print('下载并转换完成')
    return files

class subs_cnn():
    def __init__(self, cfgfile, jsonfile):
        self.urlp = datapool(jsonfile)
        self.urlp.load()
        self.cfgfile = cfgfile
        self.startup = True

    def subs(self):
        global startup
        config = getconfig(self.cfgfile)
        url = 'https://edition.cnn.com/'
        urls = geturls(url, config['config']['keyword'])
        urls = self.urlp.filter(urls)
        if len(urls) > 0 and (self.startup == False):
            files = urltopdf(urls)
            sendmail('cnn.com邮件订阅!', files, config)
            deleltefiles(files)

        else:
            print('->cnn无新订阅，不发送\n\n\n')
        self.startup = False
        self.urlp.dump()
