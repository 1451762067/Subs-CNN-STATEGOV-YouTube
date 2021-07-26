import time
from subs_youtube import subs_youtube
from subs_stategov import subs_stategov
from subs_cnn import subs_cnn


if __name__ == '__main__':
    #如果有新增订阅，不同人员，不同频道，不同邮件，只需做好配置文件，在下面新增订阅实例即可
    zzh_subs_youtube = subs_youtube('subs_youtube.config', 'subs_youtube.json')
    zzh_my_subs_cnn = subs_cnn('cnn.config', 'cnn.json')
    zzh_my_subs_stategov =  subs_stategov('stategov.config', 'stategov.json')

    while True:
        try:
            zzh_subs_youtube.subs()
        except Exception as e:
            print(e)

        try:
            zzh_my_subs_cnn.subs()
        except Exception as e:
            print(e)

        try:
            zzh_my_subs_stategov.subs()
        except Exception as e:
            print(e)


        print('->此次订阅结束 sleep=1800s')
        time.sleep(1800)
    pass