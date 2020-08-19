"""
ftp 文件服务 服务端
多线程并发模型训练
"""

from socket import *
from threading import Thread
import os, time

# 全局变量
HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST, PORT)  # 服务器地址

# 文件库位置
FTP = "/home/tarena/FTP/"


# 处理客户端请求
class FTPServer(Thread):
    def __init__(self, connfd):
        super().__init__()
        self.connfd = connfd

    def do_list(self):
        # 判断文件库是否为空
        file_list = os.listdir(FTP)
        if not file_list:
            self.connfd.send(b'FAIL')  # 列表为空
            return
        else:
            self.connfd.send(b'OK')
            time.sleep(0.1)
            data = "\n".join(file_list)
            self.connfd.send(data.encode())

    # 处理下载
    def do_get(self, filename):
        try:
            f = open(FTP + filename, 'rb')
        except:
            # 文件不存在报异常
            self.connfd.send(b"FAIL")
            return
        else:
            # 文件打开成功
            self.connfd.send(b"OK")
            time.sleep(0.1)
            # 发送文件
            while True:
                data = f.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.connfd.send(b"##")  # 文件发送完毕
                    break
                self.connfd.send(data)
            print("下载成功")
            f.close()


    # 处理上传
    def do_put(self, filename):
        if os.path.exists(FTP + filename):
            self.connfd.send(b"FAIL")
            return
        else:
            self.connfd.send(b"OK")
            # 接收文件
            f = open(FTP + filename, 'wb')
            while True:
                data = self.connfd.recv(1024)
                if data == b"##":
                    break
                f.write(data)
            print("上传成功")
            f.close()


    # 作为一个线程内容处理某一个客户端的请求
    def run(self):
        # 总分模式
        while True:
            # 某个客户端所有的请求
            data = self.connfd.recv(1024).decode()
            print("Request:", data)  # 调试
            # 根据不同的请求做不同处理
            if not data or data == 'EXIT':
                self.connfd.close()
                return
            elif data == 'LIST':
                self.do_list()
            elif data[:3] == 'GET':
                filename = data.split(' ')[-1]
                self.do_get(filename)
            elif data[:3] == 'PUT':
                filename = data.split(' ')[-1]
                self.do_put(filename)


def main():
    # tcp套接字创建
    sock = socket()
    sock.bind(ADDR)
    sock.listen(5)
    print("Listen the port %s" % PORT)

    # 循环连接客户端
    while True:
        try:
            connfd, addr = sock.accept()
            print("Connect from", addr)
        except KeyboardInterrupt:
            sock.close()
            return
        # 为连接进来的客户端创建单独的线程
        t = FTPServer(connfd)  # 使用自定义线程类创建线程
        t.setDaemon(True)  # 主线程退出，分之线程终止服务
        t.start()


if __name__ == '__main__':
    main()


"""
ftp 文件服务器

需求分析：
    【1】 分为服务端和客户端，要求可以有多个客户端同时操作。
    【2】 客户端可以查看服务器文件库中有什么文件。
    【3】 客户端可以从文件库中下载文件到本地。
    【4】 客户端可以上传一个本地文件到文件库。
    【5】 使用print在客户端打印命令输入提示，引导操作

技术点分析 ： C / S
    * 并发模型　：　多线程
    * 网络：　ＴＣＰ网络
    * 文件传输　：　　边读边发　　　边收边写

功能模块划分和封装　：　拆
　　　
　　　函数　　＋　　　类
　　　　

　　　* 搭建整体结构框架

　　　* 查看文件目录

     * 下载文件

     * 上传文件

通信协议：
    　　　　　　　　　　　　请求类型　　　　数据参量
    　获取文件列表　　　　　　LIST
      下载文件　　　　　　　　RETR　　　　　filename
      上传文件     　　　　　STOR　　     filename
      退出　　　　　　　　　　EXIT

具体功能逻辑

    　* 搭建整体结构框架
         服务端 ： tcp多线程并发模型

　　　* 查看文件目录

         客户端 ： 输入指令 list
                  发送请求
                  等待回复，根据回复请求做下一步处理
                  OK : 接收文件列表
                  FAIL : 结束

         服务端 ： 接收请求
                  判断请求是否可以满足
                  给出回复
                  OK ： 发送文件列表
                  FAIL : 结束

     * 下载文件
          客户端 ：　发送请求
          　　　　　　等待反馈
          　　　　　　OK  接收文件
          　　　　　　FAIL　结束

          服务端 ： 接收请求
                   判断文件是否存在，给出结果
                   ok 发送文件
                   FAIL 结束

     * 上传文件
          客户端 ：　选择要上传的文件
                    发送请求
          　　　　　　等待反馈
          　　　　　　OK  上传文件
          　　　　　　FAIL　结束

          服务端 ： 接收请求
                   判断文件是否存在，给出结果
                   OK 接收送文件
                   FAIL 结束


"""
