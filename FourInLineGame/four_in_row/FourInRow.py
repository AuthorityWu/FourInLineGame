
# origin: https://www.shiyanlou.com/courses/746
# notice: 本人并不会用pygame，这里的代码基本来源以上的资源网
# content：4子棋的游戏窗口，界面显示

import random, copy, sys, pygame
from pygame.locals import *
from game.boardstate import *

class GameWindow(object):

    def __init__(self):
        self.BOARDWIDTH = 6  # 棋子盘的宽度栏数
        self.BOARDHEIGHT = 5  # 棋子盘的高度栏数
        assert self.BOARDWIDTH >= 4 and self.BOARDHEIGHT >= 4, 'Board must be at least 4x4.'

        # python assert断言是声明其布尔值必须为真的判定，如果发生异常就说明表达示为假。
        # 可以理解assert断言语句为raise-if-not，用来测试表示式，其返回值为假，就会触发异常。

        # DIFFICULTY = 2 # 难度系数，计算机能够考虑的移动级别
        # 这里2表示，考虑对手走棋的7种可能性及如何应对对手的7种走法

        self.SPACESIZE = 50  # 棋子的大小

        self.FPS = 30  # 屏幕的更新频率，即30/s
        self.WINDOWWIDTH = 640  # 游戏屏幕的宽度像素
        self.WINDOWHEIGHT = 480  # 游戏屏幕的高度像素

        self.XMARGIN = int((self.WINDOWWIDTH - self.BOARDWIDTH * self.SPACESIZE) / 2)  # X边缘坐标量，即格子栏的最左边
        self.YMARGIN = int((self.WINDOWHEIGHT - self.BOARDHEIGHT * self.SPACESIZE) / 2)  # Y边缘坐标量，即格子栏的最上边
        self.BRIGHTBLUE = (0, 50, 255)  # 蓝色
        self.WHITE = (255, 255, 255)  # 白色

        self.BGCOLOR = self.BRIGHTBLUE
        self.TEXTCOLOR = self.WHITE

        self.RED = 'red'
        self.BLACK = 'black'
        self.EMPTY = None
        self.HUMAN = 'human'
        self.COMPUTER = 'computer'

        # 初始化pygame的各个模块
        pygame.init()

        # 初始化了一个Clock对象
        self.FPSCLOCK = pygame.time.Clock()

        # 创建游戏窗口
        self.DISPLAYSURF = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT))

        # 游戏窗口标题
        pygame.display.set_caption(u'four in row')

        # Rect(left,top,width,height)用来定义位置和宽高
        self.REDPILERECT = pygame.Rect(int(self.SPACESIZE / 2), self.WINDOWHEIGHT - int(3 * self.SPACESIZE / 2), self.SPACESIZE, self.SPACESIZE)

        # 这里创建的是窗口中左下角和右下角的棋子
        self.BLACKPILERECT = pygame.Rect(self.WINDOWWIDTH - int(3 * self.SPACESIZE / 2), self.WINDOWHEIGHT - int(3 * self.SPACESIZE / 2),
                                              self.SPACESIZE, self.SPACESIZE)
        # 载入红色棋子图片
        self.REDTOKENIMG = pygame.image.load('../images/4row_red.png')

        # 将红色棋子图片缩放为SPACESIZE
        self.REDTOKENIMG = pygame.transform.smoothscale(self.REDTOKENIMG, (self.SPACESIZE, self.SPACESIZE))

        # 载入黑色棋子图片
        self.BLACKTOKENIMG = pygame.image.load('../images/4row_black.png')

        # 将黑色棋子图片缩放为SPACESIZE
        self.BLACKTOKENIMG = pygame.transform.smoothscale(self.BLACKTOKENIMG, (self.SPACESIZE, self.SPACESIZE))

        # 载入棋子面板图片
        self.BOARDIMG = pygame.image.load('../images/4row_board.png')

        # 将棋子面板图片缩放为SPACESIZE
        self.BOARDIMG = pygame.transform.smoothscale(self.BOARDIMG, (self.SPACESIZE, self.SPACESIZE))

        # 载入人胜利时图片
        self.HUMANWINNERIMG = pygame.image.load('../images/4row_humanwinner.png')

        # 载入AI胜时图片
        self.COMPUTERWINNERIMG = pygame.image.load('../images/4row_computerwinner.png')

        # 载入平局提示图片
        self.TIEWINNERIMG = pygame.image.load('../images/4row_tie.png')

        # 返回一个Rect实例
        self.WINNERRECT = self.HUMANWINNERIMG.get_rect()

        # 游戏窗口中间位置坐标
        self.WINNERRECT.center = (int(self.WINDOWWIDTH / 2), int(self.WINDOWHEIGHT / 2))

        # 载入操作提示图片
        self.ARROWIMG = pygame.image.load('../images/4row_arrow.png')

        # 返回一个Rect实例
        self.ARROWRECT = self.ARROWIMG.get_rect()

        # 操作提示的左位置
        self.ARROWRECT.left = self.REDPILERECT.right + 10

        # 将操作提示与下方红色棋子实例在纵向对齐
        self.ARROWRECT.centery = self.REDPILERECT.centery

        self.board = self.getNewBoard()
        self.drawBoard()


    def move_and_update(self, action: MoveAction):
        """ 根据 下棋动作 更新棋盘

        :param action: 利用下棋动作跟新棋盘
        """
        if action.chess_type == 1:                  # 判断是红色棋子还是黑色棋子
            self.board[action.x][action.y] = self.BLACK  # 根据下棋动作的位置 更新 对应棋盘位置的棋子
        else:
            self.board[action.x][action.y] = self.RED    # 根据下棋动作的位置 更新 对应棋盘位置的棋子
        self.drawBoard()                            # 重画棋盘
        pygame.display.update()                     # 窗口更新

    def drawBoard(self, extraToken=None):
        # DISPLAYSURF 是我们的界面，在初始化变量模块中有定义
        self.DISPLAYSURF.fill(self.WHITE)  # 将游戏窗口背景色填充为蓝色
        spaceRect = pygame.Rect(0, 0, self.SPACESIZE, self.SPACESIZE)  # 创建Rect实例
        for x in range(self.BOARDWIDTH):
            # 确定每一列中每一行中的格子的左上角的位置坐标
            for y in range(self.BOARDHEIGHT):
                spaceRect.topleft = (self.XMARGIN + (x * self.SPACESIZE), self.YMARGIN + (y * self.SPACESIZE))

                # x =0,y =0时，即第一列第一行的格子。
                if self.board[x][y] == self.RED:  # 如果格子值为红色
                    # 则在在游戏窗口的spaceRect中画红色棋子
                    self.DISPLAYSURF.blit(self.REDTOKENIMG, spaceRect)
                elif self.board[x][y] == self.BLACK:  # 否则画黑色棋子
                    self.DISPLAYSURF.blit(self.BLACKTOKENIMG, spaceRect)

        # extraToken 是包含了位置信息和颜色信息的变量
        # 用来显示指定的棋子
        if extraToken != None:
            if extraToken['color'] == self.RED:
                self.DISPLAYSURF.blit(self.REDTOKENIMG, (extraToken['x'], extraToken['y'], self.SPACESIZE, self.SPACESIZE))
            elif extraToken['color'] == self.BLACK:
                self.DISPLAYSURF.blit(self.BLACKTOKENIMG, (extraToken['x'], extraToken['y'], self.SPACESIZE, self.SPACESIZE))

        # 画棋子面板
        for x in range(self.BOARDWIDTH):
            for y in range(self.BOARDHEIGHT):
                spaceRect.topleft = (self.XMARGIN + (x * self.SPACESIZE), self.YMARGIN + (y * self.SPACESIZE))
                self.DISPLAYSURF.blit(self.BOARDIMG, spaceRect)

        # 画游戏窗口中左下角和右下角的棋子
        self.DISPLAYSURF.blit(self.REDTOKENIMG, self.REDPILERECT)  # 左边的红色棋子
        self.DISPLAYSURF.blit(self.BLACKTOKENIMG, self.BLACKPILERECT)  # 右边的黑色棋子

    def getNewBoard(self):
        board = []
        for x in range(self.BOARDWIDTH):
            board.append([self.EMPTY] * self.BOARDHEIGHT)
        return board  # 返回board列表，其值为BOARDHEIGHT数量的None

    def isValidMove(self, row, col):
        # 判断棋子移动有效性
        if (col < 0 or col >= (self.BOARDWIDTH) or row < 0 or
                row >= (self.BOARDHEIGHT) or self.board[col][row] != self.EMPTY):
            # 判断范围是否在棋盘内，以及位置是否为空
            return False
            # 则为无效的移动，否则有效
        return True

    def getHumanMove(self):
        draggingToken = False
        tokenx, tokeny = None, None
        while True:
            # pygame.event.get()来处理所有的事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # 停止，退出
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and not draggingToken and self.REDPILERECT.collidepoint(event.pos):
                    # 如果事件类型为鼠标按下，notdraggingToken为True，鼠标点击的位置在REDPILERECT里面
                    draggingToken = True
                    tokenx, tokeny = event.pos
                elif event.type == pygame.MOUSEMOTION and draggingToken:  # 如果开始拖动了红色棋子

                    tokenx, tokeny = event.pos  # 更新被拖拽的棋子的位置
                elif event.type == pygame.MOUSEBUTTONUP and draggingToken:
                    # 如果鼠标松开，并且棋子被拖拽

                    # 如果棋子被拖拽在board的正上方
                    if (tokeny > self.YMARGIN and tokenx > self.XMARGIN and
                            tokenx < self.WINDOWWIDTH - self.XMARGIN and tokeny < self.WINDOWHEIGHT - self.YMARGIN):
                        col = int((tokenx - self.XMARGIN) / self.SPACESIZE)   # 根据棋子的x坐标确定棋子会落的列（0,1...6)
                        row = int((tokeny - self.YMARGIN) / self.SPACESIZE)   # 根据棋子的y坐标确定棋子会落的列（0,1...5)
                        if self.isValidMove(row, col):          # 如果棋子移动有效

                            action = MoveAction(row, col, -1)   # 获取下棋动作( -1 代表红色棋子)
                            self.move_and_update(action)        # 根据 下棋动作 更新棋盘
                            return action                       # 返回移动动作
                    tokenx, tokeny = None, None
                    draggingToken = False
            if tokenx != None and tokeny != None:  # 如果拖动了棋子,则显示拖动的棋子
                self.drawBoard({'x': tokenx - int(self.SPACESIZE / 2), 'y': tokeny - int(self.SPACESIZE / 2), 'color': self.RED})
            # 并且通过调整x,y的坐标使拖动时，鼠标始终位于棋子的中心位置。
            else:
                self.drawBoard()  # 当为无效移动时，鼠标松开后，因为此时board中所有格子的值均为none
            # 调用drawBoard时，进行的操作是显示下面的两个棋子，相当于棋子回到到开始拖动的地方。
            pygame.display.update()
            self.FPSCLOCK.tick()
