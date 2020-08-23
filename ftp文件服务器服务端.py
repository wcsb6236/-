"""
ftp 文件服务器
1. 功能
【1】 分为服务端和客户端,要求可以有多个客户端同时操作。
【2】 客户端可以查看服务器文件库中有什么文件。
【3】 客户端可以从文件库中下载文件到本地。
【4】 客户端可以上传一个本地文件到文件库。
【5】 使用print在客户端打印命令输入提示,引导操作

"""
"""
思路分析：
1. 技术点分析
    并发模型，多线程并发模式
    数据传输 TCP传输

2. 结构设计
    客户端发起请求，打印请求提示界面
    文件传输功能封装为类
    
2. 功能分析
    网络搭建
    查看文件库信息
    下载文件
    上传文件
    客户端退出
"""
from socket import *
import os, sys
import signal
from threading import Thread
from time import sleep


HOST = "127.0.0.1"
PORT = 8888
ADDR = (HOST,PORT)
FTP = "/home/lei/python_study/03_concurrence/02_多进程|线程网络并发/文件服务器/filebox/"
# 文件库路经

class FtpServer:
    def __init__(self,c,FTP_PATH):
        self.c = c
        self.path = FTP_PATH

    def do_get(self,filename):
        try:
            fl = open(self.path + filename,'rb')
        except Exception:
            self.c.send("文件不存在".encode())
            return
        else:
            self.c.send(b"OK")
            sleep(0.1)
        # 发送文件内容
        while True:
            data = fl.read()
            if not data:
                sleep(0.1)
                self.c.send(b"##")
                break
            self.c.send(data)

    def do_put(self,filename,):
        # dir = os.listdir(self.path)
        # while True:
        #     if filename in dir:
        #         self.c.send("文件名已存在，请重新输入")
        #     else:
        #         break
        if os.path.exists(self.path + filename):
            self.c.send("文件名已存在，请重新输入".encode())
            return
        self.c.send(b"OK")
        fl = open(self.path + filename, 'wb')
        while True:
            data = self.c.recv(1024)
            if data == b"##":
                break
            fl.write(data)
        fl.close()

    def do_list(self):
        dir = os.listdir(self.path)
        if not dir:
            self.c.send("no file yet".encode())
            return
        else:
            self.c.send(b"OK")  # 发送1次
            sleep(0.1) # 防止粘包，这里停顿一下

        fs = "" # 一个空值
        for file in dir: # 有几个文件就发送几次
            # 判断文件不是隐藏文件，同时是一个普通文件
            if file[0] != "." and \
                    os.path.isfile(self.path+file):
                fs += file + '\n' # 在后面加一个消息边界，'\n'，
                # 其他的逗号或者任何标志都行，发送N次，客户端接收一次就行
        self.c.send(fs.encode())
                # 发送1次，每次发送可以停顿0.1秒，
                # 或者更好的办法是增加消息边界，使信息看起来没有粘包
        # self.c.send(b"##")  # 这里是作为发送完成的标志，发送1次给客户端，让客户端停止接受.修改后可以不需要了
        # 这个函数连续向客户端发送4次以上，这样在客户端接收的时候，
        # 会产生粘包现象，就是所有发送信息都在一个地方显示，
        # 所以可以在每次发送前停顿0.1秒，或者人为的给发送内容设定一个消息边界


def handle(c):
    cls = c.recv(1024).decode()
    FTP_PATH = FTP + cls + '/'  # 方便后面传文件过来拼接
    fs = FtpServer(c, FTP_PATH)
    while True:
        # 接受客户端请求
        data = c.recv(1024).decode()
        # 放在最前面，可以先检测data为空的情况，以免客户端崩溃或者强行退出导致data[0]报错
        if not data or data[0] == '4':  # 客户端崩溃，或者强行退出，data即是空值，程序退出
            return  # 客户端传来‘4’，正常退出，这样写，两种情况都可以包含,
            # 而服务端是不会退出的，所以在这里也不用执行什么，直接return就行了

        elif data[0] == '1': # date[0]
            fs.do_list()

        elif data[0] == "G":
            filename = data.split(" ")[-1]
            fs.do_get(filename)

        elif data[0] == "P":
            filename = data.split(" ")[-1]
            fs.do_put(filename)




    #     # if data == 2:
        #     fl.download()



    # c.close()


def main():
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    s.bind(ADDR)
    s.listen(5)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    print("listen the port 8888...")

    while True:
        try:
            c,addr = s.accept()
        except KeyboardInterrupt:
            print("退出服务")
            return
        except Exception as e:
            print(e)
            continue
        print("客户端：", c.getpeername())
        t = Thread(target=handle,args=(c,))
        t.setDaemon(True)
        t.start()

if __name__ == '__main__':
    main()

