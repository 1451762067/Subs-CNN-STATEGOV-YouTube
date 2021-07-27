import time, re, requests, json, os, logging
from subs_utils import  getconfig, deleltefiles, sendmail, datapool
requests.packages.urllib3.disable_warnings()

'''
下载网页并筛选出目标链接
'''
def geturls(url:str):
    # proxies={
    #     "http":"http://127.0.0.1:7070",
    #     "https":"http://127.0.0.1:7070",
    # }
    print('->从 %s 下载网页' % (url))
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'}

    try:
        req = requests.Session()
        resp = req.get(url, verify=False, headers=headers)
        items = re.findall(r'(<li class="collection-result">.+?href.+?</li>)', resp.text, flags=re.DOTALL)
        urls=[]
        for item in items:
            href =  re.findall(r'<a href="(.+?)"(.+?)>', item, flags=re.DOTALL)
            urls.append(href[0][0])
            print(' ',href[0][0])
    except Exception as e:
        logging.error(e);print(e)
        return []
    else:
        return urls

'''
网页转pdf
'''
def urltopdf(urls:list):
    import weasyprint
    files=[]
    fails=[]
    for url in urls:
        filename = url.split('/')[-2]+ '.pdf'
        print('->下载网页并转成pdf:', url, '\n  文件名:', filename)
        try:
             weasyprint.HTML(url).write_pdf(filename)
        except Exception as e:
            fails.append(url)
            logging.error(e);print(e)
        else:
            files.append(filename)
            print('下载并转换完成')
    return files, fails

class subs_stategov():
    def __init__(self, cfgfile, jsonfile):
        self.urlp = datapool(jsonfile)
        self.urlp.load()
        self.cfgfile = cfgfile
        self.startup = True

    def subs(self):
        config = getconfig(self.cfgfile)
        url = 'https://www.state.gov/countries-areas-archive/china/'
        urls = geturls(url)
        urls = self.urlp.filter(urls)
        if len(urls) > 0 and (self.startup == False):
            files, fails = urltopdf(urls)
            if len(files) > 0:
                sendmail('state.gov邮件订阅!', files, config)
                deleltefiles(files)
            self.urlp.remove(fails)
            self.urlp.dump()
        else:
            print('->stategov无新订阅，不发送\n\n\n')

        self.startup = False
