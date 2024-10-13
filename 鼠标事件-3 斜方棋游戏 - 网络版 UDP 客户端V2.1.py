from tkinter import *
from tkinter.messagebox import *
import socket
import threading
import os


root = Tk()
root.title(" 网络五子棋V2.1--UDP 客户端")
# 五子棋--夏敏捷2016-2-11,仨个小时 网络版 UDP 客户端
imgs = [PhotoImage(file='C:\\Users\\J\\Desktop\\黑棋.png'), PhotoImage(file='C:\\Users\\J\\Desktop\\白棋.png')]
turn = 0
Myturn = -1


def callexit(event):  # 退出
    pos = "exit|"
    sendMessage(pos)
    os._exit(0)


def calljoin(event):  # 连接服务器
    pos = 'join|'  # "连接服务器"命令
    sendMessage(pos);  # 发送连接服务器请求
    startNewThread()  # 启动线程接收服务器端的消息receiveMessage();


selected_chess = None  # 在函数外部初始化选中的棋子

def is_adjacent(start, end, valid_moves):
    # 检查 end 是否是 start 的有效邻接点之一
    return end in valid_moves.get(start, [])

def is_adjacent(src, dest, valid_moves):
    # 检查dest是否在src的有效移动位置列表中
    return dest in valid_moves.get(src, [])


def check_all_pieces_for_capture(map, valid_moves, valid_points):
    for color in ["0", "1"]:  # 假设0为白棋，1为黑棋
        for point in valid_points:
            if map[point[1] // 40][point[0] // 40] == color:
                check_and_remove_if_captured(point, map, valid_moves, valid_points)

    # 更新游戏状态并检查是否有玩家获胜
    if win_lose(map, valid_moves):
        showinfo(title="游戏结束")


def check_and_remove_if_captured(point, map, valid_moves, valid_points):
    current_piece = map[point[1] // 40][point[0] // 40]
    opponent_color = "1" if current_piece == "0" else "0"

    # 获取当前点周围的有效移动位置
    adjacent_positions = valid_moves.get(point, [])
    # 筛选出同时也在有效点列表中的邻近位置
    valid_adjacent_positions = [pos for pos in adjacent_positions if pos in valid_points]

    # 检查所有邻近有效位置是否都被对手棋子占据
    if all(map[pos[1] // 40][pos[0] // 40] == opponent_color for pos in valid_adjacent_positions):
        # 消除被完全包围的棋子
        cv.create_rectangle(point[0] - 20, point[1] - 20, point[0] + 20, point[1] + 20, fill='green', outline='green')
        drawQiPan()
        map[point[1] // 40][point[0] // 40] = " "
        showinfo(title="提示", message=f"棋子被消除")

valid_points = [(20, 20), (20, 580), (580, 20), (580, 580),
                    (300, 300),
                    (160, 160), (160, 440), (440, 160), (440, 440),
                    (20, 300), (300, 20), (580, 300), (300, 580)]
valid_moves = {
    (20, 20): [(300, 20), (20, 300)],
    (20, 580): [(300, 580), (20, 300)],
    (580, 20): [(300, 20), (580, 300)],
    (580, 580): [(300, 580), (580, 300)],
    (300, 300): [(160, 160), (440, 160), (160, 440), (440, 440)],
    (20, 300): [(20, 580), (20, 20), (160, 440), (160, 160)],
    (160, 160): [(20, 300), (300, 20), (300, 300)],
    (300, 20): [(160, 160), (440, 160), (20, 20), (580, 20)],
    (440, 160): [(300, 20), (580, 300), (300, 300)],
    (580, 300): [(440, 440), (440, 160), (580, 580), (580, 20)],
    (440, 440): [(300, 580), (580, 300), (300, 300)],
    (300, 580): [(20, 580), (580, 580), (180, 440), (440, 440)],
    (160, 440): [(300, 580), (20, 300), (300, 300)],
}

def perform_move(selected_chess, close_point, map):
    global cv, imgs, turn

    # 向服务器发送移动信息
    pos = f"move|{close_point[0]},{close_point[1]}"
    sendMessage(pos)

    # 在客户端的棋盘上绘制移动
    cv.create_image(close_point[0], close_point[1], image=imgs[turn])
    cv.create_rectangle(selected_chess[0] - 20, selected_chess[1] - 20, selected_chess[0] + 20,
                        selected_chess[1] + 20, fill='green', outline='green')
    drawQiPan()
    map[selected_chess[1] // 40][selected_chess[0] // 40] = " "
    map[close_point[1] // 40][close_point[0] // 40] = str(turn)

    # 检查消除
    check_all_pieces_for_capture(map, valid_moves, valid_points)

def callback(event):
    global turn, selected_chess, map, valid_moves, valid_points

    clicked_point = (event.x, event.y)
    close_point = None
    for point in valid_points:
        if abs(clicked_point[0] - point[0]) <= 20 and abs(clicked_point[1] - point[1]) <= 20:
            close_point = point
            break

    if close_point is None:
        showinfo(title="提示", message="无效的位置")
        return

    if selected_chess is None:
        if map[close_point[1] // 40][close_point[0] // 40] == str(turn):
            selected_chess = close_point
        else:
            showinfo(title="提示", message="还没轮到该棋子动")
    else:
        if is_adjacent(selected_chess, close_point, valid_moves):
            if map[close_point[1] // 40][close_point[0] // 40] == " ":
                # 进行棋子移动
                perform_move(selected_chess, close_point, map)

                # 如果双方各走一步后，再执行检查
                if turn == 1 or turn == 0:  # 假设0开始，1结束，代表一个完整的回合
                    check_all_pieces_for_capture(map, valid_moves, valid_points)

                turn = 1 - turn
                selected_chess = None
                if win_lose(map, valid_moves):
                    showinfo(title="游戏结束")
            else:
                showinfo(title="提示", message="这个位置已经有棋子了")
                selected_chess = None
        else:
            showinfo(title="提示", message="只能移动到周围线相连的端点")
            selected_chess = None


def drawQiPan():  # 画棋盘
    cv.create_line(20, 580, 580, 580, width=2)
    cv.create_line(20, 580, 20, 20, width=2)
    cv.create_line(20, 20, 580, 20, width=2)
    cv.create_line(580, 20, 580, 580, width=2)
    cv.create_line(20, 300, 300, 580, width=2)
    cv.create_line(300, 580, 580, 300, width=2)
    cv.create_line(580, 300, 300, 20, width=2)
    cv.create_line(20, 300, 300, 20, width=2)
    cv.create_line(160, 160, 440, 440, width=2)
    cv.create_line(160, 440, 440, 160, width=2)
    cv.pack()

def drawQizhi():
    initial_points = [(20, 20), (20, 580), (580, 20), (580, 580),
                      (160, 160), (160, 440), (440, 160), (440, 440),
                      (300, 20), (300, 580)]
    for i, point in enumerate(initial_points):
        img = imgs[i % 2]  # 交替放置黑白棋子
        cv.create_image(point[0], point[1], image=img)
        # 更新棋盘状态
        map[point[1] // 40][point[0] // 40] = str(i % 2)

def count_pieces(map):
    pieces = {'0': 0, '1': 0}  # '0' 代表白棋，'1' 代表黑棋
    for row in map:
        for cell in row:
            if cell in pieces:
                pieces[cell] += 1
    return pieces
def win_lose(map, valid_moves):
    pieces = count_pieces(map)
    if pieces['0'] == 0:
        showinfo(title="游戏结束", message="黑棋胜利，白棋全部被消除！")
        return True
    elif pieces['1'] == 0:
        showinfo(title="游戏结束", message="白棋胜利，黑棋全部被消除！")
        return True
    elif (pieces['0'] <= 2 or pieces['1'] <= 2) and not has_valid_moves(map, valid_moves):
        winner = '白棋' if pieces['0'] > pieces['1'] else '黑棋'
        showinfo(title="游戏结束", message=f"{winner}胜利，对方棋子不足并且无路可走")
        return True
    return False

# End Function
def print_map():  # 输出map地图
    for j in range(0, 15):  # 0--14
        for i in range(0, 15):  # 0--14
            print(map[i][j], end=' ')
        print('w')


def drawOtherChess(x, y):
    global turn, map, valid_points, imgs, cv, selected_chess

    # 计算最接近的有效点
    close_point = None
    for point in valid_points:
        if abs(x - point[0]) <= 20 and abs(y - point[1]) <= 20:
            close_point = point
            break

    if close_point is None:
        print("收到无效的坐标:", x, y)
        return

    # 判断是否已有棋子占据此位置
    if map[close_point[1] // 40][close_point[0] // 40] != " ":
        print("该位置已经有棋子了:", close_point[0], close_point[1])
        return

    # 绘制棋子
    img1 = imgs[turn]
    cv.create_image(close_point, image=img1)
    cv.pack()

    # 更新棋盘状态
    map[close_point[1] // 40][close_point[0] // 40] = str(turn)

    # 如果有选中的棋子并且是移动操作，清除原位置
    if selected_chess and selected_chess != close_point:
        # 清除原来棋子的位置
        original_x, original_y = selected_chess
        cv.create_rectangle(original_x - 20, original_y - 20, original_x + 20, original_y + 20, fill='green', outline='green')
        map[original_y // 40][original_x // 40] = " "  # 清空原棋子的地图状态

    # 切换玩家
    turn = 1 - turn

    # 更新选中棋子的位置，移动后应取消选中状态
    selected_chess = None

    # 如果需要，这里可以添加检查游戏是否结束的逻辑
    # if win_lose(map, valid_moves):
    #     messagebox.showinfo(title="游戏结束", message="游戏已经结束！")

# 接收消息
def receiveMessage():
    global s
    while True:
        # 接收客户端发送的消息
        global addr
        data = s.recv(1024).decode('utf-8')
        a = data.split("|")  # 分割数据
        if not data:
            print('client has exited!')
            break
        elif a[0] == 'join':  # 连接服务器请求
            print('client 连接服务器!')
            label1["text"] = 'client 连接服务器成功，请你走棋！'
        elif a[0] == 'exit':  # 对方退出信息
            print('client 对方退出!')
            label1["text"] = 'client 对方退出，游戏结束！'
        elif a[0] == 'over':  # 对方赢信息
            print('对方赢信息!')
            label1["text"] = data.split("|")[0]
            showinfo(title="提示", message=data.split("|")[1])
        elif a[0] == 'move':  # 客户端走的位置信息
            print('received:', data, 'from', addr)
            p = a[1].split(",")
            x = int(p[0]);
            y = int(p[1]);
            print(p[0], p[1])
            label1["text"] = "客户端走的位置" + p[0] + p[1]
            drawOtherChess(x, y)  # 画对方棋子
    s.close()

# 发送消息
def sendMessage(pos):
    global s
    s.sendto(pos.encode(), (host, port))


# 启动线程接收端的消息
def startNewThread():
    # 启动一个新线程来接收服务器端的消息
    # thread.start_new_thread(function,args[,kwargs])函数原型，
    # 其中function参数是将要调用的线程函数，args是传递给线程函数的参数，它必须是个元组类型，而kwargs是可选的参数
    # receiveMessage函数不需要参数，就传一个空元组
    thread = threading.Thread(target=receiveMessage, args=())
    thread.daemon=True
    thread.start();


# map = [[" "," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
#       [" "," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
#       [" "," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
#       [" "," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
#       [" "," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
#       [" "," "," "," "," "," "," "," "," "," "," "," "," "," "," "],]

# map =  [[" "," "," "," "," "," "," "," "," "," "," "," "," "," "," "]] * 15错误

map = [[" "] * 580 for _ in range(580)]
cv = Canvas(root, bg='green', width=610, height=610)
drawQiPan()
drawQizhi()
cv.bind("<Button-1>", callback)
cv.pack()
label1 = Label(root, text="客户端....")
label1.pack()

v = StringVar()
entryServerIP = Entry(root, textvariable=v)  # Entry组件
v.set("127.0.0.1")  # 设置StringVar变量的值，Entry组件文本自动更新
entryServerIP.pack()

f = Frame(root)
button0 = Button(f, text="连接服务器")
button0.bind("<Button-1>", calljoin)
button0.pack(side='left')
button1 = Button(f, text="退出游戏")
button1.bind("<Button-1>", callexit)
button1.pack(side='left')
f.pack()
# 创建UDP SOCKET
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = 8000  # 服务器端口
host = entryServerIP.get()  # 服务器地址 192.168.0.101
# host = 'localhost'   #服务器地址127.0.0.1
root.mainloop()