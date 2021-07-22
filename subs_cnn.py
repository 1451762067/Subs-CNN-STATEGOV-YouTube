import json, re, requests
from   subs_stategov import sendmail
requests.packages.urllib3.disable_warnings()

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
        print('  ', item['uri'])
        for word in keyword:
            if item['uri'].lower().find(word) > -1:
                urls.append('https://edition.cnn.com' + item['uri'])
                print('https://edition.cnn.com' + item['uri'])
                continue

    return urls

'''
选择是否过滤url，比如从数据库中比对是否已经发送过，
如发送过，则remove
'''
def filterUrls(urls: list):
    for url in urls:
        #此处判断是否需要过滤
        ret = False
        if ret:
            urls.remove(url)

    return urls

def urltopdf(urls: list):
    import weasyprint
    files =[]
    for url in urls:
        try:
            filename = url.split('/')[-2] + '.pdf'
            files.append(filename)
            print('->下载网页并转成pdf:', url, '\n  文件名:', filename)
            weasyprint.HTML(url).write_pdf(filename)
            break
        except Exception as e:
            print(e)
        else:
            print(filename, "下载完成")

    return files

if __name__ == '__main__':
    url = 'https://edition.cnn.com/'
    urls = geturls(url)
    urls = filterUrls(urls)
    files = urltopdf(urls)
    sendmail('cnn.com邮件订阅!', files)
    print('->此次订阅结束.')