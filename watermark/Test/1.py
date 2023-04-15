import cv2
import numpy as np
import sys
sys.setrecursionlimit(10**8)
im = cv2.imread('1.png')
def dew(im):
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    vis = np.zeros_like(im, dtype=np.bool_)
    visr = np.zeros_like(im, dtype=np.bool_)
    # m = (180 < im) & (im < 215)
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
im=dew(im)
cv2.imencode('.png', im)[1].tofile('2.png')