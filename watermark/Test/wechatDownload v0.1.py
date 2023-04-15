# 功能：爬取微信公众号图片2.0
# 调整结构，面向对象编程
import requests
import re
from tkinter import *
from tkinter.ttk import Progressbar
from tkinter import messagebox
from tkinter import filedialog
from time import localtime, strftime
import numpy as np
import os
import cv2
import img2pdf


class App(object):
    def __init__(self, object):
        self.path = StringVar()
        self.progress = StringVar()
        self.frame1 = Frame(object)
        self.frame1.pack()

        self.frame2 = Frame(object)
        self.frame2.pack()

        self.frame3 = Frame(object)
        self.frame3.pack()

        self.label_path = Label(self.frame1, text="目标路径：")
        self.label_path.pack(padx=2, pady=2, side=LEFT)

        self.entry_path = Label(self.frame1, width=34,
                                relief=GROOVE, textvariable=self.path)
        self.entry_path.pack(padx=2, pady=2, side=LEFT)

        self.btn_select = Button(
            self.frame1, text="路径选择", height=1, command=self.select)
        self.btn_select.pack(padx=2, pady=2, side=LEFT)

        self.label_url = Label(self.frame2, text="输入链接：")
        self.label_url.pack(padx=2, pady=2, side=LEFT)

        self.txt_url = Entry(self.frame2, width=34)
        self.txt_url.pack(padx=2, pady=2, side=LEFT)

        self.btn_download = Button(
            self.frame2, text="立即下载", command=self.download)
        self.btn_download.pack(padx=2, pady=2, side=LEFT)

        self.label_progress = Label(self.frame3, text="当前进度：")
        self.label_progress.pack(padx=2, pady=2, side=LEFT)

        self.bar = Progressbar(self.frame3, length=242)
        self.bar.pack(padx=2, pady=2, side=LEFT, fill=X)
        self.bar['value'] = 0

        self.label = Label(self.frame3, textvariable=self.progress, width=8)
        self.label.pack(padx=2, pady=2, side=LEFT)

    # 设置进度条
    def set_progress(self, value):
        self.bar['value'] = value
        self.bar.update()

    # 显示路径
    def set_label_path(self, strs):
        self.path.set(strs)

    # 当前下载进度 ，形式为 xx/x, 如10/20
    def set_progress_text(self, strs):
        self.progress.set(strs)

    # 选择文件路径
    def select(self):
        path_ = filedialog.askdirectory()
        self.set_label_path(path_)

    # 开始下载
    def download(self):
        self.set_progress(0)
        url = self.txt_url.get()
        if url == '':
            messagebox.showinfo("提醒", "链接不能为空！")
        elif self.path.get() == '':
            messagebox.showinfo("提醒", "路径不能为空！")
        else:
            html = self.get_html_page(url)
            items = self.parse_page(html)
            self.save_picture(items)
            messagebox.showinfo("Title", "下载完成！")

    def get_html_page(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return None

    def parse_page(self, html):
        pattern = re.compile(
            '<img [^>]*data-src="([^>]+?)wx_fmt=(.+?)"[^>]*?>', re.S)
        # pattern = re.compile('<img.*?>', re.S)
        items = re.findall(pattern, str(html))
        for item in items:
            if item[1] == "other":
                items.remove(item)
        return items

    def save_picture(self, items):
        num = 0
        length = len(items)
        oimage_list = []        
        image_list = []
        os.makedirs(self.path.get() + '/pics/', exist_ok=True)
        os.makedirs(self.path.get() + '/opic/', exist_ok=True)
        for item in items:
            pic = requests.get(item[0])
            # 以当前时间为前缀
            currentTime = strftime("%Y%m%d%H%M%S", localtime())
            im = cv2.imdecode(np.asarray(
                bytearray(pic.content), dtype="uint8"), cv2.IMREAD_COLOR)
            if im is not None:
                ime=cv2.imencode('.jpg', im)[1]
                ime.tofile(
                    self.path.get() + '/opic/' + currentTime + str(num) + '.jpg')
                oimage_list.append(bytes(ime))
                im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                m = (200 < im) & (im < 207)
                im[m] = 255
                # cv2.imwrite(self.path.get() + '/' + currentTime + str(num) + '.' + item[1],im)

                ime = cv2.imencode('.jpg', im)[1]
                ime.tofile(
                    self.path.get() + '/pics/' + currentTime + str(num) + '.jpg')
                image_list.append(bytes(ime))
            self.set_progress((num + 1) / length * 100)
            pro = str(num + 1) + '/'+str(length)
            self.set_progress_text(pro)
            num = num + 1
        with open(self.path.get()+"/原.pdf", "wb") as f:
            f.write(img2pdf.convert(oimage_list))
        with open(self.path.get()+"/全.pdf", "wb") as f:
            f.write(img2pdf.convert(image_list))


if __name__ == "__main__":
    window = Tk()
    window.title("神墙试卷下载去水印 v0.1")
    app = App(window)
    window.mainloop()
