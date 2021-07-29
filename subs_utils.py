import logging
import  os, json

'''
读取配置文件
'''
def getconfig(conf:str):
    with open(conf, "r+", encoding='utf-8_sig') as f:
        config = json.load(f)

    return config


'''
删除文件
'''
def deleltefiles(files: list):
    for file in files:
        try:
            print('删除文件:', file)
            os.remove(file)
        except Exception as e:
            pass

'''
发送邮件  考虑封装成class
'''
def sendmail(Subject:str, files:list, config, content=''):
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


    for file in files:
        #发送带附件的邮件
        if not os.path.exists(file):
            continue
        att1 = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        att1.add_header('Content-Disposition', 'attachment', filename=file)  #用此代码，用下行代码时，中文附件名将会变成tcmime.*.bin的格式
        # att1["Content-Disposition"] = 'attachment; filename="{file}"'.format(file=file)
        message.attach(att1)
        print('->发送邮件附件:', file)

    #正文信息
    content = MIMEText(content)
    message.attach(content)

    #分发
    message['To'] = Header(','.join(TOs), 'utf-8')
    smtp_obj.sendmail(from_addr=FROM, to_addrs=TOs, msg=message.as_string())
    print('->发送附件至%s完成, 附件数:%d' % (TOs, len(files)))

class datapool():
    def __init__(self, datafile:str):
        self.datafile = datafile
        self.data=[]

    def load(self, datafile=''):
        if len(datafile) == 0:
            file = self.datafile
        else:
            file = datafile

        try:
            with open(file, "r+", encoding='utf-8_sig') as f:
                self.data = json.load(f)
        except Exception as e:
            pass

    def dump(self, datafile=''):
        if len(datafile) == 0:
            file = self.datafile
        else:
            file = datafile
        with open(file, "w+", encoding='utf-8_sig') as f:
            json.dump(self.data, f, sort_keys=True, indent=2, ensure_ascii=False)

    def filter(self, data:list):
        datar = []
        for d in data:
            if d not in  self.data:
                datar.append(d)
                self.data.append(d)
        return datar

    def remove(self, data:list):
        for d in data:
            if d in self.data:
                self.data.remove(d)

    def __repr__(self):
        return str(self.data)
