import json, re, requests
import time

from   subs_stategov import sendmail, getconfig
requests.packages.urllib3.disable_warnings()

config =''
'''
获取网页里的连接
'''
keyword=['china']

def geturls(url: str):
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
                # return urls
                continue

    return urls

'''
选择是否过滤url，比如从数据库中比对是否已经发送过，
如发送过，则remove，考虑下列封装成class
'''
URLPOOL=[]  #已经发送的url池

def filterUrls(urls: list):
    urlret=[]
    for url in urls:
        #此处判断是否需要过
        if url not in URLPOOL:
            urlret.append(url)
            URLPOOL.append(url)

    return urlret

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

if __name__ == '__main__':

    while True:
        try:
            config = getconfig('cnn.config')
            url = 'https://edition.cnn.com/'
            urls = geturls(url)
            urls = filterUrls(urls)

            if len(urls) > 0:
                pass
                # files = urltopdf(urls)
                # sendmail('cnn.com邮件订阅!', files, config)
            else:
                print('->无新订阅，不发送')
        except Exception as e:
            print(e)
        else:
            print('->此次订阅结束.')
        finally:
            time.sleep(config['config']['sleep'])
    pass
    pass