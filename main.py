from tkinter import *
from tkinter import font
from tkinter import ttk
from importlib import reload


game_loadonce = False


def play():
    global game
    global menuApp, game_loadonce
    menuApp.save_scores("leaderboard.txt")
    menuApp.root.destroy()
    if game_loadonce == False:
        import game
        game_loadonce = True
    else:
        reload(game)
    menuApp = _menuApp()
    menuApp.fnh_ttl.configure(text="Score: "+str(game.score))
    menuApp.getname1()


class _menuApp():

    def sortf(self, scr):
        i2 = 0
        for i in range(len(scr), 0, -1):
            if scr[i:i+2] == '- ':
                i2 = i
                break
        i2 += 2
        return -int(scr[i2:])

    def load_scores(self, fname):
        try:
            file = open(fname, mode='r')
        except FileNotFoundError:
            file = open(fname, 'a')
            file.close()
            return
        for line in file.readlines():
            line = line.strip()
            self.scores.append(line)
        self.scores.sort(key=self.sortf)
        file.close()

    def save_scores(self, fname):
        file = open(fname, mode='w')
        for line in self.scores:
            file.write(line+'\n')
        file.close()

    def update_scores(self, name=None, score=None):
        if name != None and score != None:
            msg = name+' - '+str(score)
            self.scores.append(msg)
        self.scores.sort(key=self.sortf)
        self.scr_lst_v.set(value=self.scores)
        self.save_scores("leaderboard.txt")

    def quit(self):
        self.destroyed = True
        self.root.quit()

    def leaderboard(self, prev_f):
        prev_f.place_forget()
        self.main.place_forget()
        self.ldr_brd.place(x=0, y=0)

    def mainmenu(self, prev_f):
        prev_f.place_forget()
        self.main.place(x=0, y=0)

    def getname1(self):
        self.main.place_forget()
        self.finish.place(x=0, y=0)

    def getname2(self):
        self.finish.place_forget()
        self.main.place(x=0, y=0)
        if menuApp.txtname.get() == '':
            menuApp.txtname.set('Anonymous')
        menuApp.update_scores(menuApp.txtname.get(), game.score)

    def __init__(self):

        self.rescr = (512, 512)
        self.root = Tk()
        self.root.title("SPACE ATTXK")
        self.root.geometry(str(self.rescr[0]) + 'x' + str(self.rescr[1]))
        self.root.resizable(False, False)

        self.font1 = font.Font(family='Arial', size=24)
        self.font2 = font.Font(family='Arial', size=12)

        self.s = ttk.Style()
        self.s.configure('TButton', font=self.font2)

        self.main = ttk.Frame(
            self.root, width=self.rescr[0], height=self.rescr[1])
        self.main.columnconfigure(0, weight=1)
        self.main.columnconfigure(3, weight=1)
        self.main.rowconfigure(0, weight=1)
        self.main.rowconfigure(6, weight=1)
        self.main.grid_propagate(0)
        self.main.place(x=0, y=0)

        self.title = ttk.Label(
            self.main, text="SPACE ATTXCK", font=self.font1, padding=32)
        self.title.grid(row=1, column=0, columnspan=4)

        self.strt_btn = ttk.Button(self.main, text="Play", command=play)
        self.strt_btn.grid(row=2, column=2, sticky=S+E+W)

        self.ldr_btn = ttk.Button(
            self.main, text="Leaderboard", command=lambda: self.leaderboard(self.main))
        self.ldr_btn.grid(row=3, column=2, sticky=N+E+S+W)
        self.settings = ttk.Button(
            self.main, text="Exit", command=lambda: exit())
        self.settings.grid(row=4, column=2, sticky=N+E+W)

        ctl_txt = "Controls:\nJump - Space\n Fire - Enter\nEscape - Pause Game"
        self.controls = ttk.Label(
            self.main, text=ctl_txt, font=self.font2, justify=CENTER, padding=32)
        self.controls.grid(row=5, column=2, sticky=N+E+W)

        self.scores = []
        self.scr_lst_v = StringVar(value=self.scores)
        self.load_scores("leaderboard.txt")
        self.update_scores()

        self.ldr_brd = ttk.Frame(
            self.root, width=self.rescr[0], height=self.rescr[1])
        self.ldr_brd.columnconfigure(0, weight=1)
        self.ldr_brd.columnconfigure(3, weight=1)
        # self.ldr_brd.rowconfigure(0,weight=1)
        self.ldr_brd.grid_propagate(0)

        self.ldr_ttl = ttk.Label(
            self.ldr_brd, text="Leaderboard", font=self.font1, padding=32, justify=CENTER)
        self.ldr_ttl.grid(row=1, column=2)
        self.ldr_lst = Listbox(self.ldr_brd, listvariable=self.scr_lst_v,
                               height=10, selectmode='browse', font=self.font2)
        self.ldr_lst.grid(row=2, column=2, padx=16, pady=16)

        self.ldr_exit = ttk.Button(
            self.ldr_brd, text="Main Menu", command=lambda: self.mainmenu(self.ldr_brd))
        self.ldr_exit.grid(row=3, column=2)

        self.finish = ttk.Frame(
            self.root, width=self.rescr[0], height=self.rescr[1])
        self.finish.rowconfigure(0, weight=1)
        self.finish.rowconfigure(5, weight=1)
        self.finish.columnconfigure(1, weight=1)
        self.finish.columnconfigure(3, weight=3)
        self.finish.grid_propagate(0)

        self.txtname = StringVar()
        self.fnh_ttl = ttk.Label(self.finish, text="",
                                 font=self.font1, justify=CENTER)
        self.fnh_ttl.grid(row=1, column=2, padx=16, pady=16)
        self.fnh_lbl1 = ttk.Label(
            self.finish, text="Enter name:", font=self.font2, justify=CENTER)
        self.fnh_lbl1.grid(row=3, column=1, padx=16)
        self.fnh_txtin = ttk.Entry(
            self.finish, font=self.font2, justify=CENTER, textvariable=self.txtname)
        self.fnh_txtin.grid(row=3, column=2)
        self.fnh_btn = ttk.Button(
            self.finish, text="OK", command=self.getname2)
        self.fnh_btn.grid(row=4, column=2, padx=16, pady=16)


menuApp = _menuApp()
menuApp.root.mainloop()
