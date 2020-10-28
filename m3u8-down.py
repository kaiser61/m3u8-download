import requests
import re
from concurrent.futures import ThreadPoolExecutor
import time
from operator import itemgetter
import sys

class Down_Ts:
    __url="http://www.zuidazy4.com/?m=vod-detail-id-49187.html"
    __m3u8_url="https://yushou.qitu-zuida.com/20180530/6407_25ca716b/index.m3u8"
    __index_m3u8="index.m3u8"
    __true_m3u8=""
    __max_workers=15
    __thread_name="down_file"
    __content_list=list()
    __ts_length=0
    __file_size=0
    __temp_length=0

    def __init__(self,m3u8_url,threads):
        self.__m3u8_url=m3u8_url
        self.__max_workers=threads



    def __map_fun(self,arg):
        return self.__true_m3u8.replace(self.__index_m3u8,arg)+".ts"

    def get_ts_list(self):

        temp_m3u8=requests.get(self.__m3u8_url)
        print(temp_m3u8.status_code)

        print(temp_m3u8.text)
        last_index=temp_m3u8.text.split("\n")[-1]
        self.__true_m3u8=self.__m3u8_url.replace(self.__index_m3u8,last_index)
        print(self.__true_m3u8)

        temp_m3u8_2=requests.get(self.__true_m3u8)
        print(temp_m3u8_2.status_code)
        # print(temp_m3u8_2.text)
        list_ts=re.findall(",\n(.*?).ts",temp_m3u8_2.text)
        # for ts in list_ts:
        #     # print(ts)
        #     temp_ts=true_m3u8.replace(self.__index_m3u8,ts)+".ts"
        #     # print(temp_ts)
        #     list_true_ts.append(temp_ts)
        list_true_ts=list(map(self.__map_fun,list_ts))
        # print(list_true_ts[0])
        self.__ts_length=list_true_ts.__len__()
        print("ts_len：",self.__ts_length)
        return list_true_ts

    def __down_content(self,ts_url,num):
        temp_time1=time.time()
        temp_ts=requests.get(ts_url)
        temp_time=time.time()-temp_time1

        if (temp_ts.status_code!=200):
            print(ts_url,"失败")
            exit()
        else:
            temp_dict=dict()
            temp_dict["index"]=num
            self.__temp_length+=1
            temp_dict["content"]=temp_ts.content
            self.__file_size+=int(temp_ts.headers['Content-Length'])
            j=(self.__temp_length / self.__ts_length) * 100
            s=int(temp_ts.headers['Content-Length'])/1024/1024/temp_time*self.__max_workers
            temp_str="进度：%3.2f"%j+"%"+",网速：%3.2f"%s+"M/s"
            print("\r%s"%temp_str, end="")
            self.__content_list.append(temp_dict)


    def get_content_list(self,list_true_ts):
        threadpool=ThreadPoolExecutor(max_workers=self.__max_workers,
                                      thread_name_prefix=self.__thread_name)
        # with open(file,"wb") as f:
        #     for temp_ts in list_true_ts:
        #         # content=threadpool.submit(self.__down_content,temp_ts)
        #         # f.write(content)
        #         ts= threadpool.submit(self.__down_content, temp_ts)
        #         print(ts.url)
        #     f.close()
        num=0
        for temp_ts in list_true_ts:
            # content=threadpool.submit(self.__down_content,temp_ts)
            # f.write(content)
            num+=1
            threadpool.submit(self.__down_content,temp_ts,num)

        threadpool.shutdown(wait=True)


    def write_content_list(self,file):
        self.__content_list=sorted(self.__content_list,key=itemgetter("index"))

        with open(file,"wb") as f:
            for content in self.__content_list:
                f.write(content["content"])
        f.close()

    def get_file_size(self):
        return self.__file_size/1024/1024

if __name__=="__main__":
    opt= sys.argv[1]
    if opt=='-h':
        print("argv1(参数1)：m3u8_url(m3u8文件链接)\nargv2(参数2)：filename(文件名)\n"
              "argv3(参数3)：threads(线程数)")
        sys.exit()
    m3u8_url=opt
    threads=int(sys.argv[-1])
    file_name=sys.argv[2]
    file_index=".mp4"
    tiem1=time.time()
    down=Down_Ts(m3u8_url,threads)
    ts_list= down.get_ts_list()
    down.get_content_list(ts_list)
    down.write_content_list(file_name+file_index)
    time=time.time()-tiem1
    print("\n总耗时：%.1d"%time+"s")
    file_size=down.get_file_size()
    print("文件大小总计：%.2fM"%file_size)
    s=file_size/time
    print("平均下载速度：%2.fM/s"%s)


