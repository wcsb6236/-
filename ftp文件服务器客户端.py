"""
TCP 客户端程序
"""
from socket import *
import sys,os
from time import sleep

class FtpClient:
    def __init__(self,sockfd):
        self.sockfd = sockfd

    def do_quit(self):
        self.sockfd.send(b"4")
        self.sockfd.close()
        sys.exit("谢谢使用")

    def do_get(self,filename):
        self.sockfd.send(("G "+filename).encode())
        # 等待回复
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            fd = open(filename,"wb")
            # 接收内容写入文件
            while True:
                data = self.sockfd.recv(1024)
                if data == b"##":
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)

    def do_put(self,filename):
        # dir = os.listdir("../文件服务器")
        # if filename not in dir:
        #     print("上传文件不存在")
        #     return
        try:
            fl = open(filename, "rb")
        except Exception:
            print("上传文件不存在")
            return
        # 如果文件名是一个路经，那就需要分割解析，取最后面的文件名
        filename = filename.split('/')[-1]
        self.sockfd.send(("P " + filename).encode())
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            sleep(0.1)
            while True:
                data = fl.read(1024)
                self.sockfd.send(data)
                if not data:
                    sleep(0.1)
                    self.sockfd.send(b"##")
                    break
            fl.close()
        else:
            print(data)

    def do_list(self):
        self.sockfd.send(b'1') # 发送请求
        # 等待回复
        data = self.sockfd.recv(1028).decode()
        # Ok 表示请求成功
        if data == "OK":  # 为了防止粘包，这里也不要循环接受了，
            # 把服务端的多次发送，一次性接受就行，也就不需要判断循环结束，这样非常好
            # 接受文件列表
            data = self.sockfd.recv(4096) # 如果文件比较多，4096接收不完，可以用循环接受，
                                          # 但是循环结束前，应该调用sleep函数停顿一下
            print(data.decode())
        else:
            print(data)


def request(sockfd):
    fc = FtpClient(sockfd)
    while True:
        print("命令选项：", end=" ")
        print("""
        1.文件列表 
        2.文件下载  输入get+文件名
        3.文件上传  输入put+文件名
        4.退出""")
        cmd = input("输入命令：")
        if cmd == '1':
            fc.do_list()
        elif cmd == '4':
            fc.do_quit()
        elif cmd[:3] == 'get':
            filename = cmd.strip().split(" ")[-1]
            fc.do_get(filename)
        elif cmd[:3] == 'put':
            filename = cmd.strip().split(" ")[-1]
            fc.do_put(filename)


def main():
    sockfd = socket()
    server_addr = ('127.0.0.1', 8888)
    try:
        sockfd.connect(server_addr)
    except Exception as e:
        print("链接服务器失败！")
    else:
        print("""**********************
Data    File   Image
**********************
        """)
        cls = input("请输入文件种类：")
        if cls not in ['Data','File','Image']:
            print("种类不存在，请重新输入")
            return
        else:
            sockfd.send(cls.encode())
            request(sockfd)
        sockfd.close()


if __name__ == '__main__':
    main()