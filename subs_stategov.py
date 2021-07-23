import time, re, requests, json
requests.packages.urllib3.disable_warnings()

'''
读取配置文件
'''
def getconfig(conf:str):
    with open(conf, "r+", encoding='utf-8_sig') as f:
        config = json.load(f)

    return config

'''
下载网页并筛选出目标链接
'''
def geturls(url:str):
    # proxie={
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


'''
发送邮件  考虑封装成class
'''
def sendmail(Subject:str, files:list, config):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.header import Header

    HOST = 'smtp.qq.com'
    PORT = '465'
    FROM = config['config']['mailuser']
    USER = config['config']['mailuser']
    TOs = config['config']['mails']
    PWD = config['config']['mailpwd']
    # 邮件列表，需要订阅的话往列表添加邮箱即可

    #如果使用第三方客户端登录，要求使用授权码，不能使用真实密码，防止密码泄露。
    smtp_obj = smtplib.SMTP_SSL(host=HOST, port=PORT)
    # smtp_obj = smtp_obj.connect(host=HOST, port=PORT)
    res = smtp_obj.login(user=USER, password=PWD)

    if res[0] != 235:
        print('->登录邮箱stmp.qq.com 失败')
        return
    else:
        print('->登录邮箱stmp.qq.com成功:', res)

    #准备附件
    message = MIMEMultipart()
    message['From'] = Header(FROM, 'utf-8')
    message['Subject'] = Header(Subject, 'utf-8')

    Content=''; cnt=1
    for file in files:
        #发送带附件的邮件
        att1 = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        att1["Content-Disposition"] = 'attachment; filename="{file}"'.format(file=file)
        message.attach(att1)
        print('->发送邮件附件:', file)
        Content = Content + '附件' + str(cnt) + ': ' + file + '\n'
        cnt = cnt + 1
        # time.sleep(1)

    #正文信息
    body = MIMEText(Content)
    message.attach(body)

    #分发
    try:
        message['To'] = Header(','.join(TOs), 'utf-8')
        smtp_obj.sendmail(from_addr=FROM, to_addrs=TOs, msg=message.as_string())
    except Exception as e:
        print(e)
    else:
        print('->发送附件至%s完成, 附件数:%d' % (TOs, len(files)))


if __name__ == '__main__':
    while True:
        try:
            config = getconfig('stategov.config')
            url = 'https://www.state.gov/countries-areas-archive/china/'
            urls = geturls(url)
            urls = filterUrls(urls)
            if len(urls) > 0:
                files = urltopdf(urls)
                sendmail('state.gov邮件订阅!', files, config)
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