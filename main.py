# _*_ encoding:utf-8 _*_
import os
def installlibs():
    libs = {"numpy","requests","pygame"}
    try:
        for lib in libs:
            os.system("pip3 install "+lib)
        print("Successful")
    except Exception as err:
        print("Failed:", Exception)
        
try:
    import pygame
    from pygame.locals import *
    import sys
    import math
    import storn
    from socket import *
    import select
    import chessboard
    import time
    import danmuji
except:
    installlibs()

roomID = '646'

pygame.init()

bg_size = 615, 615

WHITE = (255, 255, 255)

font1 = pygame.font.Font('font/12345.TTF', 35)
win_text = font1.render(u"黑棋胜利", True, WHITE)
win_text_rect = win_text.get_rect()
win_text_rect.left, win_text_rect.top = (bg_size[0] - win_text_rect.width) // 2, \
                                        (bg_size[1] - win_text_rect.height) // 2
lose_text = font1.render(u"白棋胜利", True, WHITE)
lose_text_rect = lose_text.get_rect()
lose_text_rect.left, lose_text_rect.top = (bg_size[0] - lose_text_rect.width) // 2, \
                                          (bg_size[1] - lose_text_rect.height) // 2



class StateMachine():
    def __init__(self):
        # state constant
        self.BLACKTURN = 'BLACKTURN'
        self.WHITETURN = 'WHITETURN'
        self.BLACKWIN = 'BLACKWIN'
        self.WHITEWIN = 'WHITEWIN'
        self.GAMEOVER = 'GAMEOVER'
        
        # current state
        self.state = self.GAMEOVER
        
        # Players ('all' or 'any' or some nickname, or 'ai' for white)
        self.black = 'all'
        self.white = 'mouse'
        
        # deadlines
        self.deadline = 0
        self.allDeadline = 0
        self.promptCountdown = 0
        
        # new chess data, [[pos1, num1], [pos2, num2], ...]
        self.data = []
        
        # chessboard
        self.board = chessboard.Chessboard()
        
        # render screen
        self.screen = pygame.display.set_mode(bg_size)
        
        # danmuji
        self.dmj = danmuji.Gift(roomID)
        self.dmj.run()
        
        print('hello')


    def newGame(self):
        self.state = self.BLACKTURN
        self.setDeadline()
        self.board.clear()


    def setDeadline(self):
        self.deadline = time.time() + 120
        self.allDeadline = time.time() + 60


    def player(self):
        if self.state == self.WHITETURN:
            return self.white
        elif self.state == self.BLACKTURN:
            return self.black


    def nextTurn(self):
        # add chess
        print('data =', self.data)
        print('add Chess to', self.data[0][0])
        self.board.addChess(self.data[0][0])
        
        # check who wins
        if self.board.isWin():
            if self.state == self.WHITETURN:
                self.state = self.WHITEWIN
            else:
                self.state = self.BLACKWIN
        
        # init for next turn
        if self.state == self.WHITETURN:
            self.state = self.BLACKTURN
        elif self.state == self.BLACKTURN:
            self.state = self.WHITETURN
        self.setDeadline()
        self.data = []


    def addData(self, pos):
        for i in self.data:
            if i[0] == pos:
                i[1] += 1
                return
        self.data.append([pos, 1])

    def getData(self):
        # get data from danmuji
        if self.player() == 'ai':
            self.data.append([self.board.ai(), 1])
        elif self.player() == 'mouse':
            return
        else:
            self.dmj.lock.acquire()
            for danmu in self.dmj.danmuList:
                if (self.player() == 'all' or self.player() == 'any' or self.player() == danmu[0]) and self.board.is_valid(danmu[1]):
                    self.addData(danmu[1])
            self.dmj.danmuList = []
            self.dmj.lock.release()
        
        self.data.sort(key=lambda a:a[1], reverse = True)


    def update(self):
        if self.state == self.GAMEOVER or self.state == self.WHITEWIN or self.state == self.BLACKWIN:
            if self.promptCountdown == 0:
                self.promptCountdown = time.time() + 10
            elif time.time() > self.promptCountdown:
                self.promptCountdown = 0
                self.newGame()
        else:
            self.getData()
            if len(self.data) == 0:
                if time.time() > self.deadline or (self.player() == 'all' and time.time() > self.allDeadline):
                    if self.state == self.BLACKTURN:
                        self.state = self.WHITEWIN
                    else:
                        self.state = self.BLACKWIN
            elif self.player() != 'all' or time.time() > self.allDeadline:
                self.nextTurn()


    def renderScreen(self):
        # 绘制棋盘
        screen.blit(bg_image, (0, 0))
        
        for i in self.board.black_chesses:
            screen.blit(i.image, i.image_rect())
            
        for i in self.board.white_chesses:
            screen.blit(i.image, i.image_rect())
        
        # draw gameover prompt
        if self.state == self.BLACKWIN:
            screen.blit(win_text, win_text_rect)
        elif self.state == self.WHITEWIN:
            screen.blit(lose_text, lose_text_rect)
        
        # draw countdown
        if self.player() == 'all':
            text_countdown = font1.render('倒计时:'+str(int(self.allDeadline - time.time())), True, WHITE)
        else:
            text_countdown = font1.render('倒计时:'+str(int(self.deadline - time.time())), True, WHITE)
        text_countdown_rect = text_countdown.get_rect()
        text_countdown_rect.left, text_countdown_rect.top = (20, 0)
        screen.blit(text_countdown, text_countdown_rect)
        
        # draw player 'all' statistic
        if self.player() == 'all':
            for danmu in self.data:
                tmp = font1.render(str(danmu[1]), True, WHITE)
                tmp_rect = tmp.get_rect()
                tmp_rect.left, tmp_rect.top = self.board.getPixel(danmu[0])
                tmp_rect.left -= tmp_rect.width/2
                tmp_rect.top -= 20
                screen.blit(tmp, tmp_rect)
        
        pygame.display.flip()



clock = pygame.time.Clock()
screen = pygame.display.set_mode(bg_size)
pygame.display.set_caption('五子棋')
bg_image = pygame.image.load('image/bg.png').convert_alpha()  # 背景图片

def main():
    state_machine = StateMachine()
    state_machine.newGame()

    running = True
    while running:
        
        state_machine.renderScreen()
        
        state_machine.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                client_socket.close()
                server_socket.close()
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    print('click', event.pos)
                    if state_machine.player() == 'mouse' and state_machine.board.is_valid(state_machine.board.getPos(event.pos)):
                        state_machine.data = []
                        state_machine.data.append([state_machine.board.getPos(event.pos), 1])
                        state_machine.nextTurn()
                                
        clock.tick(60)


if __name__ == '__main__':
    main()
