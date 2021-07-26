import subs_cnn, subs_stategov, subs_youtube,time


if __name__ == '__main__':
    while True:
        try:
            subs_youtube.subs_youtube()
        except Exception as e:
            print(e)

        try:
            subs_cnn.sub_cnn()
        except Exception as e:
            print(e)

        try:
            subs_stategov.sub_stategov()
        except Exception as e:
            print(e)


        print('->此次订阅结束 sleep=3600s')
        time.sleep(3600)
    pass