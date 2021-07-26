import time, re, requests, json, os
from subs_utils import  getconfig, deleltefiles, sendmail
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

    req = requests.Session()
    resp = req.get(url, verify=False, headers=headers)
    items = re.findall(r'(<li class="collection-result">.+?href.+?</li>)', resp.text, flags=re.DOTALL)
    urls=[]
    for item in items:
        href =  re.findall(r'<a href="(.+?)"(.+?)>', item, flags=re.DOTALL)
        urls.append(href[0][0])
        print(' ',href[0][0])

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

startup=True
def sub_stategov():
    config = getconfig('stategov.config')
    url = 'https://www.state.gov/countries-areas-archive/china/'
    urls = geturls(url)
    urls = filterUrls(urls)

    global startup
    if len(urls) > 0 and ( startup == False):
        files = urltopdf(urls)
        sendmail('state.gov邮件订阅!', files, config)
        deleltefiles(files)
    else:
        print('->stategov无新订阅，不发送\n\n\n')

    startup = False
# if __name__ == '__main__':
#     while True:
#         try:
#             config = getconfig('stategov.config')
#             url = 'https://www.state.gov/countries-areas-archive/china/'
#             urls = geturls(url)
#             urls = filterUrls(urls)
#             if len(urls) > 0:
#                 files = urltopdf(urls)
#                 sendmail('state.gov邮件订阅!', files, config)
#                 deleltefiles(files)
#             else:
#                 print('->无新订阅，不发送')
#         except Exception as e:
#             print(e)
#         else:
#             print('->此次订阅结束.')
#         finally:
#             time.sleep(config['config']['sleep'])
#     pass
#     pass