# _*_ encoding:utf-8 _*_
import pygame
from pygame.locals import *
import sys
import math
import storn
from socket import *
import select
import numpy as np

class Chessboard():

    def __init__(self):
        # 棋盘坐标
        self.x = []
        self.y = []
        for i in range(0, 15):
            self.x.append(28 + i * 40)
            self.y.append(28 + i * 40)

        # 记录棋盘每个坐标的属性，没有棋子为0，白棋为1，黑棋为2
        self.map_chess = np.zeros((15, 15), dtype = int)

        # storn lists
        self.white_chesses = []
        self.black_chesses = []
        
        # black's turn?
        self.is_black = True
    
        
    
    def clear(self):
        for i in range(15):
            for j in range(15):
                self.map_chess[i][j] = 0
                
        self.white_chesses = []
        self.black_chesses = []
        self.is_black = True

    def getPixel(self, pos):
        return (pos[0] * 40 + 28, (14 - pos[1]) * 40 + 28)
    
    def getPos(self, pixel):
        x = 0
        y = 0
        for i in range(15):
            if abs(pixel[0] - (i * 40 + 28)) < 20:
                x = i
                break
        
        for i in range(15):
            if abs(pixel[1] - (i * 40 + 28)) < 20:
                y = 14 - i
                break
                
        return (x, y)

    def addChess(self, pos):
        if self.map_chess[pos[0]][pos[1]] != 0:
            raise Exception('occupied')
        if self.is_black:
            chess = storn.Storn_Black(self.getPixel(pos))
            self.black_chesses.append(chess)
            self.map_chess[pos[0]][pos[1]] = 2
        else:
            chess = storn.Storn_White(self.getPixel(pos))
            self.white_chesses.append(chess)
            self.map_chess[pos[0]][pos[1]] = 1

        self.is_black = not self.is_black
    
    # 判断是否有子
    def is_valid(self, pos):
        return pos[0] >= 0 and pos[0] <= 14 and pos[1] >= 0 and pos[1] <= 14 and self.map_chess[pos[0]][pos[1]] == 0

    # 判断是否有五子连线
    def isWin(self):
        '''
        for i in range(0, 15):
            tmp = str(i)+':'
            for j in range(0, 15):
                tmp += str(self.map_chess[i][j])
            print(tmp)
        '''
        linked = 1
        for i in range(0, 15):
            for j in range(1, 15):
                if self.map_chess[i][j] != 0 and self.map_chess[i][j] == self.map_chess[i][j-1]:
                    linked += 1
                else:
                    linked = 1
                if linked == 5:
                    return True
        
        linked = 1
        for j in range(0, 15):
            for i in range(1, 15):
                if self.map_chess[i][j] != 0 and self.map_chess[i][j] == self.map_chess[i-1][j]:
                    linked += 1
                else:
                    linked = 1
                if linked == 5:
                    return True
                    
        linked = 1
        for i in range(0, 15):
            for j in range(1, 15-i):
                if self.map_chess[i+j][j] != 0 and self.map_chess[i+j][j] == self.map_chess[i+j-1][j-1]:
                    linked += 1
                else:
                    linked = 1
                if linked == 5:
                    return True
        
        linked = 1
        for i in range(0, 15):
            for j in range(1, 15-i):
                if self.map_chess[i+j][14-j] != 0 and self.map_chess[i+j][14-j] == self.map_chess[i+j-1][14-(j-1)]:
                    linked += 1
                else:
                    linked = 1
                if linked == 5:
                    return True
                    
        linked = 1
        for i in range(0, 15):
            for j in range(1, i):
                if self.map_chess[i-j][j] != 0 and self.map_chess[i-j][j] == self.map_chess[i-(j-1)][j-1]:
                    linked += 1
                else:
                    linked = 1
                if linked == 5:
                    return True
        
        linked = 1
        for i in range(0, 15):
            for j in range(1, i):
                if self.map_chess[i-j][14-j] != 0 and self.map_chess[i-j][14-j] == self.map_chess[i-(j-1)][14-(j-1)]:
                    linked += 1
                else:
                    linked = 1
                if linked == 5:
                    return True
        
        return False
        
        
    # 判断每个点的价值
    def point_value(self, pos, identify1, identify2):
        value = 0
        for i in range(1,9):
            # *1111_ 活四
            if self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == identify1 and \
                self.get_point(pos, i, 3) == identify1 and \
                self.get_point(pos, i, 4) == identify1 and \
                self.get_point(pos, i, 5) == 0:
                value += 40000
            # *11112 死四1
            if self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == identify1 and \
                self.get_point(pos, i, 3) == identify1 and \
                self.get_point(pos, i, 4) == identify1 and \
                self.get_point(pos, i, 5) == identify2:
                value += 30000
            # 1*111 死四2
            if self.get_point(pos, i, -1) == identify1 and \
                self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == identify1 and \
                self.get_point(pos, i, 3) == identify1:
                value += 30000
            # 11*11 死四3
            if self.get_point(pos, i, -2) == identify1 and \
                self.get_point(pos, i, -1) == identify1 and \
                self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == identify1:
                value += 30000
            # *111_ 活三1
            if self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == identify1 and \
                self.get_point(pos, i, 3) == identify1 and \
                self.get_point(pos, i, 4) == 0:
                value += 20000
            # *1_11_ 活三2
            if self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == 0 and \
                self.get_point(pos, i, 3) == identify1 and \
                self.get_point(pos, i, 4) == identify1 and \
                self.get_point(pos, i, 5) == 0:
                value += 20000
            # *1112 死三1
            if self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == identify1 and \
                self.get_point(pos, i, 3) == identify1 and \
                self.get_point(pos, i, 4) == identify2:
                value += 15000
            # _1_112 死三2
            if self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == 0 and \
                self.get_point(pos, i, 3) == identify1 and \
                self.get_point(pos, i, 4) == identify1 and \
                self.get_point(pos, i, 5) == identify2:
                value += 15000
            # _11_12 死三3
            if self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == identify1 and \
                self.get_point(pos, i, 3) == 0 and \
                self.get_point(pos, i, 4) == identify1 and \
                self.get_point(pos, i, 5) == identify2:
                value += 15000
            # 1__11 死三4
            if self.get_point(pos, i, -1) == identify1 and \
                self.get_point(pos, i, 1) == 0 and \
                self.get_point(pos, i, 2) == identify1 and \
                self.get_point(pos, i, 3) == identify1:
                value += 15000
            # 1_1_1 死三5
            if self.get_point(pos, i, -1) == identify1 and \
                self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == 0 and \
                self.get_point(pos, i, 3) == identify1:
                value += 15000
            # 2_111_2 死三6
            if self.get_point(pos, i, -1) == identify2 and \
                self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == identify1 and \
                self.get_point(pos, i, 3) == identify1 and \
                self.get_point(pos, i, 4) == 0 and \
                self.get_point(pos, i, 5) == identify2:
                value += 15000
            # __11__ 活二1
            if self.get_point(pos, i, -1) == 0 and \
                self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == identify1 and \
                self.get_point(pos, i, 3) == 0 and \
                self.get_point(pos, i, 4) == 0:
                value += 1000
            # _1_1_ 活二2
            if self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == 0 and \
                self.get_point(pos, i, 3) == identify1 and \
                self.get_point(pos, i, 4) == 0:
                value += 1000
            # *1___
            if self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == 0 and \
                self.get_point(pos, i, 3) == 0 and \
                self.get_point(pos, i, 4) == 0:
                value += 50
            # *1_
            if self.get_point(pos, i, 1) == identify1 and \
                self.get_point(pos, i, 2) == 0:
                value += 20
        return value

    # 电脑选取落子的位置
    def ai(self):
        value = max1 = max2 = -1
        pos1 = pos2 = ()
        # 进攻时
        for i in range(0,15):
            for j in range(0,15):
                pos = (i,j)
                if not self.is_valid(pos):
                    continue
                value = self.point_value(pos, 1, 2)
                if value > max1:
                    max1 = value
                    pos1 = pos

        # 防守时
        for i in range(0,15):
            for j in range(0,15):
                pos = (i,j)
                if not self.is_valid(pos):
                    continue
                value = self.point_value(pos, 2, 1)
                if value > max2:
                    max2 = value
                    pos2 = pos
        
        if max1 > max2:
            return pos1
        else:
            return pos2


    # 获取当前坐标的属性，返回1代表白棋，返回2代表黑棋，返回3代表没有棋
    def get_point(self, pos, src, offset):
        # 8个方向
        directions = [[0,1],[1,1],[1,0],[1,-1],[0,-1],[-1,-1],[-1,0],[-1,1]]
        x1,y1 = pos
        x1 = x1 + directions[src-1][0] * offset
        y1 = y1 + directions[src-1][1] * offset
        if x1 > 14 or y1 > 14 or x1 < 0 or y1 < 0:
            return 5
        else:
            return self.map_chess[x1][y1]
