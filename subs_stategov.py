import time, re, requests
requests.packages.urllib3.disable_warnings()

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
如发送过，则remove
'''
def filterUrls(urls: list):
    for url in urls:
        #此处判断是否需要过滤
        ret = False
        if ret:
            urls.remove(url)

    return urls

'''
发送邮件
'''
def sendmail(Subject:str, files:list):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.header import Header

    HOST = 'smtp.qq.com'
    PORT = '465'
    FROM = '1451762067@qq.com'
    # 邮件列表，需要订阅的话往列表添加邮箱即可
    TOs = ['1451762067@qq.com', ]

    #如果使用第三方客户端登录，要求使用授权码，不能使用真实密码，防止密码泄露。
    smtp_obj = smtplib.SMTP_SSL(host=HOST).connect(host=HOST, port=PORT)
    res = smtp_obj.login(user=FROM, password='')
    print('登录邮箱stmp.qq.com:', res)

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
        print('发送邮件附件:', file)
        Content = Content + '附件' + str(cnt) + ': ' + file + '\n'
        cnt = cnt + 1
        time.sleep(1)

    #正文信息
    body = MIMEText(Content)
    message.attach(body)

    #分发
    for to in TOs:
        try:
            message['To'] = Header(to, 'utf-8')
            smtp_obj.sendmail(from_addr=FROM, to_addrs=[to], msg=message.as_string())
        except Exception as e:
            print(e)
        else:
            print('->发送附件至%s完成, 附件数:%d' % (to, len(files)))

if __name__ == '__main__':
    url = 'https://www.state.gov/countries-areas-archive/china/'
    urls = geturls(url)
    urls = filterUrls(urls)
    files = urltopdf(urls)
    sendmail('state.gov邮件订阅!', files)
    print('->此次订阅结束.')