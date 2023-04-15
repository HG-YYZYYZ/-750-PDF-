import ctypes
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
from multiprocessing import *
import sys
sys.setrecursionlimit(10**8)


def dew(im):
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    vis = np.zeros_like(im, dtype=np.bool_)
    visr = np.zeros_like(im, dtype=np.bool_)
    m = (im > 180) & (im < 235)

    def Dfs(x, y, rm=3):
        if x < 0 or x >= im.shape[0] or y < 0 or y >= im.shape[1] or vis[x, y]:
            return 0
        vis[x, y] = True
        if not m[x, y]:
            rm -= 1
            if rm <= 0:
                return 0
        tot = 1
        tot += Dfs(x+1, y, rm)
        tot += Dfs(x-1, y, rm)
        tot += Dfs(x, y-1, rm)
        tot += Dfs(x, y+1, rm)
        return tot

    def Rmv(x, y, rm=3):
        if x < 0 or x >= im.shape[0] or y < 0 or y >= im.shape[1] or visr[x, y]:
            return
        visr[x, y] = True
        if not m[x, y]:
            rm -= 1
            if rm <= 0:
                return
        m[x, y] = False
        im[x, y] = 255
        Rmv(x+1, y, rm)
        Rmv(x-1, y, rm)
        Rmv(x, y-1, rm)
        Rmv(x, y+1, rm)

    for i in range(im.shape[0]):
        for j in range(im.shape[1]):
            if not vis[i, j] and Dfs(i, j) > 100:
                Rmv(i, j)
    return im


def dlimg(x):
    i, item, pat = x
    pic = requests.get(item[0])
    # 以当前时间为前缀
    currentTime = strftime("%Y%m%d%H%M%S", localtime())
    im = cv2.imdecode(np.asarray(
        bytearray(pic.content), dtype="uint8"), cv2.IMREAD_COLOR)
    if im is not None:
        ime = cv2.imencode('.jpg', im)[1]
        ime.tofile(
            pat + '/opic/' + currentTime + str(i) + '.jpg')
        res = [i, bytes(ime)]
        im = dew(im)
        m = (200 < im) & (im < 207)
        im[m] = 255
        ime = cv2.imencode('.jpg', im)[1]
        ime.tofile(
            pat + '/pics/' + currentTime + str(i) + '.jpg')
        res.append(bytes(ime))
        return res
    return None


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

        self.txt_url = Entry(self.frame2, width=36)
        self.txt_url.pack(padx=2, pady=2, side=LEFT)

        self.btn_download = Button(
            self.frame2, text="立即下载", command=self.download)
        self.btn_download.pack(padx=2, pady=2, side=LEFT)

        self.label_progress = Label(self.frame3, text="当前进度：")
        self.label_progress.pack(padx=2, pady=2, side=LEFT)

        self.bar = Progressbar(self.frame3, length=750)
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
        self.length = len(items)
        self.oimage_list = []
        self.image_list = []
        pat = self.path.get()
        os.makedirs(pat + '/pics/', exist_ok=True)
        os.makedirs(pat + '/opic/', exist_ok=True)
        with Pool() as p:
            self.ims = []
            for i, result in zip(range(self.length), p.imap_unordered(dlimg, zip(
                    range(self.length), items, [pat]*self.length))):
                if result is not None:
                    self.ims.append(result)
                    self.set_progress((i + 1) / self.length * 100)
                    pro = str(i + 1) + '/'+str(self.length)
                    self.set_progress_text(pro)
            self.ims = sorted(self.ims)
            for x in self.ims:
                self.oimage_list.append(x[1])
                self.image_list.append(x[2])
        with open(self.path.get()+"/原.pdf", "wb") as f:
            f.write(img2pdf.convert(self.oimage_list))
        with open(self.path.get()+"/全.pdf", "wb") as f:
            f.write(img2pdf.convert(self.image_list))


if __name__ == "__main__":
    freeze_support()
    try:  # >= win 8.1
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:  # win 8.0 or less
        ctypes.windll.user32.SetProcessDPIAware()
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    messagebox.showinfo("免责声明", "本软件所下载内容均来自互联网，任\n何侵权及涉及内容正确性的问题，均\n与软件编写者无关！")
    window = Tk()
    window.tk.call('tk', 'scaling', ScaleFactor/75)
    window.title("神墙试卷多进程下载去水印转PDF三合一 v8.8 — Sewed by CaoYang")
    app = App(window)
    window.geometry("1300x250+500+100")
    window.mainloop()
