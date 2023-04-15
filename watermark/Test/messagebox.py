from tkinter import messagebox
import ctypes
try:  # >= win 8.1
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:  # win 8.0 or less
    ctypes.windll.user32.SetProcessDPIAware()
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
messagebox.showinfo("免责声明", "本软件所下载内容均来自互联网，任\n何侵权及涉及内容正确性的问题，均\n与软件编写者无关！")
