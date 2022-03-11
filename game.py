from tkinter import *
from tkinter import font
from random import randint, choice
from math import sqrt
from collections import OrderedDict
from time import time
from math import floor

#-------- globals--------#
world_scrollx = -256  # px/speed
mob_speed = 64  # not including world scroll
t = 0  # for object t0 init
t_p = 0
t_n = time()

kill_count = 0
score = 0


class _move(object):
    # required functions:
    # draw()

    def __init__(self, t0, x, y, vx=0, vy=0, ax=0, ay=0, *args):
        self.t0 = t0
        self.pos_t0 = [x, y]
        self.position = [x, y]
        self.speed = [vx, vy]
        self.accel = [ax, ay]
        super().__init__(*args)

    def move(self, t):
        # we can store position as float and still draw in tkinter accurately (int cast)
        self.position[0] = self.pos_t0[0]+self.speed[0] * \
            (t-self.t0)+0.5*self.accel[0]*(t-self.t0)**2
        self.position[1] = self.pos_t0[1]+self.speed[1] * \
            (t-self.t0)+0.5*self.accel[1]*(t-self.t0)**2

        self.draw()

    # note x and y are for pos_t0
    def update(self, t0, x=None, y=None, vx=None, vy=None, ax=None, ay=None):
        self.t0 = t0
        if x == None:
            self.pos_t0[0] = self.position[0]
        else:
            self.pos_t0[0] = x

        if y == None:
            self.pos_t0[1] = self.position[1]
        else:
            self.pos_t0[1] = y

        if vx != None:
            self.speed[0] = vx
        if vy != None:
            self.speed[1] = vy
        if ax != None:
            self.accel[0] = ax
        if ay != None:
            self.accel[1] = ay

def collidechk(obj1, xspace1, yspace1, obj2, xspace2, yspace2, calc_side=False):
    # automatically resolves, returns side touching if needed
    collides = False
    if obj2.position[0] <= obj1.position[0] < obj2.position[0]+xspace2 or obj2.position[0] <= obj1.position[0]+xspace1 < obj2.position[0]+xspace2:
        if obj2.position[1] <= obj1.position[1] < obj2.position[1]+yspace2 or obj2.position[1] <= obj1.position[1]+yspace1 < obj2.position[1]+yspace2:
            collides = True
    if calc_side != True:
        return collides
    else:
        if collides == True:
            def ymxc(xn, c1, c2):
                return(c2[1]-c1[1])/(c2[0]-c1[0])*(xn-c1[0])

            center = [obj1.position[0]+xspace1/2, obj1.position[1]+yspace1/2]
            c2 = [obj1.position[0]+xspace1, obj1.position[1]]
            c3 = [obj1.position[0]+xspace1, obj1.position[1]+yspace1]
            c4 = [obj1.position[0], obj1.position[1]+yspace1]

            if (center[1]-obj2.position[1]) < ymxc(center[0], obj2.position, c3) and (center[1]-c4[1]) < ymxc(center[0], c2, c4):
                side = 1
            elif (center[1]-obj2.position[1]) < ymxc(center[0], obj2.position, c3) and (center[1]-c4[1]) > ymxc(center[0], c2, c4):
                side = 2  # unused
            elif (center[1]-obj2.position[1]) > ymxc(center[0], obj2.position, c3) and (center[1]-c4[1]) > ymxc(center[0], c2, c4):
                side = 3  # unused
            elif (center[1]-obj2.position[1]) > ymxc(center[0], obj2.position, c3) and (center[1]-c4[1]) < ymxc(center[0], c2, c4):
                side = 4
            else:
                side = 0
            return collides, side
        else:
            return collides, 0


def collisionhdl():
    global kill_count
    global jump_count
    # check bullet collisions
    bullet_id_rm = []
    mob_id_rm = []
    for i in bullets.keys():
        id_rm = False
        for j in platforms.keys():
            if collidechk(bullets[i], 16, 16, platforms[j], 256*platforms[j].chunks, 64):
                bullet_id_rm.append(i)
                id_rm = True
        if id_rm == True:
            continue
        for j in mobs.keys():
            if collidechk(bullets[i], 16, 16, mobs[j], 64, 64):
                kill_count += 1
                mob_id_rm.append(j)
                bullet_id_rm.append(i)
                id_rm = True
    for i in bullet_id_rm:
        bullet_id_pool.append(i)
        bullets.pop(i)
    for i in mob_id_rm:
        p_i = mobs[i].plat_id
        mob_id_pool.append(i)
        mobs.pop(i)
        platforms[p_i].mob_ids.remove(i)

    # handle player collisions with platforms & mobs and bottom
    if player.position[1]+64 >= winApp.rescr[1] or player.position[0] <= 0:
        player.die()
    for i in platforms.keys():
        ret = collidechk(
            player, 64, 64, platforms[i], 256*platforms[i].chunks, 64, True)
        side = ret[1]
        if ret[0]:
            if side == 1:
                player.update(
                    t, None, platforms[i].position[1]-64, None, 0, None, 2048)
                jump_count = 0
            elif side == 2:
                player.update(
                    t, platforms[i].position[0]+(platforms[i].chunks*256)+64)
            elif side == 3:
                player.update(t, None, platforms[i].position[1]+65)
            elif side == 4:
                player.update(
                    t, platforms[i].position[0]-65, None, world_scrollx, 0, None, 2048)
                # u dont make it, you die :)
                winApp.root.bind_all("<KeyPress-space>", lambda a: None)

    mob_id_rm = []
    for i in mobs.keys():
        if collidechk(player, 64, 64, mobs[i], 64, 64):
            mob_id_rm.append(i)
            player.hit()
    for i in mob_id_rm:
        plat_id = mobs[i].plat_id
        platforms[plat_id].mob_ids.remove(i)
        mobs.pop(i)
        mob_id_pool.append(i)


# -------- bullets --------
class _bullet(_move):
    # requires player is instantiated first
    def __init__(self):
        super().__init__(t, player.position[0]+64, player.position[1]+40, 256)
        self.img_src = PhotoImage(file="bullet.png")
        self.img_id = winApp.canvas.create_image(
            self.position[0], self.position[1], image=self.img_src, anchor='nw')

    def draw(self):
        winApp.canvas.coords(self.img_id, self.position[0], self.position[1])


bullet_id_pool = []
for i in range(0, 1000):
    bullet_id_pool.append(i)

bullets = OrderedDict()


def bullet_spawn(event):  # tkinter will pass event info as arg
    if t > player.last_fire_t+0.15 or konami_code.cheat == True:
        player.last_fire_t = t
        id = bullet_id_pool.pop()
        bullets[id] = _bullet()


def bullets_clean():
    try:
        last_b = list(bullets.keys())[0]
        pos = bullets[last_b].position
        if pos[0] > winApp.rescr[0]:
            del bullets[last_b]
            bullet_id_pool.append(last_b)
    except IndexError:
        pass


class _konami_code():
    def __init__(self):
        self.cheat = False
        self.key = ['u', 'u', 'd', 'd', 'l', 'r', 'l', 'r', 'b', 'a']
        self.log = []

    def keyin(self, char):
        self.log.append(char)
        if self.log != self.key[:len(self.log)]:
            self.log = []
        else:
            if len(self.log) == len(self.key):
                self.cheat = True
                player.health = 10
                for i in player.health_ids:
                    winApp.canvas.delete(i)
                player.health_ids = []
            for i in range(0, player.health):
                x = winApp.rescr[0]-(i*64)-64
                id = winApp.canvas.create_image(
                    x, 0, image=player.health1_src, anchor='nw')
                player.health_ids.append(id)


konami_code = _konami_code()

jump_count = 0


def player_jump(events):
    global jump_count
    if jump_count <= 1 or konami_code.cheat == True:
        player.update(t, None, None, None, -724, None, 2048)
        jump_count += 1
# --------


class _winApp():

    def quit(self):
        self.destroyed = True
        # will quit at while loop

    def pauser(self, event):
        global t_p
        global t_n
        if not self.paused:
            t_p = time()
        else:
            t_n += time()-t_p
        self.paused = not self.paused

    def __init__(self):
        self.destroyed = False

        self.rescr = (1280, 720)

        self.root = Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.title("SPACE ATTXK")
        self.root.geometry(str(self.rescr[0]) + 'x' + str(self.rescr[1]))
        self.root.configure(background='#000')
        self.root.resizable(False, False)

        self.canvas = Canvas(
            self.root, width=self.rescr[0], height=self.rescr[1], background='#000', borderwidth=0, highlightthickness=0)
        self.canvas.place(x=0, y=0)

        self.paused = False

        self.root.bind_all('<KeyPress-Return>', bullet_spawn)
        self.root.bind_all('<KeyPress-space>', player_jump)
        self.root.bind_all('<KeyPress-Left>', lambda a: konami_code.keyin('l'))
        self.root.bind_all('<KeyPress-Right>',
                           lambda a: konami_code.keyin('r'))
        self.root.bind_all('<KeyPress-Up>', lambda a: konami_code.keyin('u'))
        self.root.bind_all('<KeyPress-Down>', lambda a: konami_code.keyin('d'))
        self.root.bind_all('<KeyPress-b>', lambda a: konami_code.keyin('b'))
        self.root.bind_all('<KeyPress-a>', lambda a: konami_code.keyin('a'))
        self.root.bind_all('<KeyPress-Escape>', self.pauser)

        self.font = font.Font(family='Arial', size=24)
        self.scr_id = self.canvas.create_text(8, 8, text=str(
            score), fill='#FFD700', anchor='nw', width=256, font=self.font)

    def score_update(self, t):
        global score
        global kill_count
        score = round(t)+kill_count
        self.canvas.itemconfigure(self.scr_id, text=score)


winApp = _winApp()
# -------- player --------


class _player(_move):

    def hit(self):
        self.health -= 1
        h_id = self.health_ids[self.health]
        winApp.canvas.itemconfig(h_id, image=self.health0_src)
        if self.health == 0:
            self.dead = True

    def __init__(self, winApp, x, y):
        self.dead = False
        self.last_fire_t = t
        self.release_fire = False
        super().__init__(t, x, y, 0, 0, 0, 2048)
        self.img_src = PhotoImage(file="player.png")
        self.img_id = winApp.canvas.create_image(
            self.position[0], self.position[1], image=self.img_src, anchor='nw')

        self.health0_src = PhotoImage(file="health0.png")
        self.health1_src = PhotoImage(file="health1.png")
        self.health = 5
        self.health_ids = []
        for i in range(0, self.health):
            x = winApp.rescr[0]-(i*64)-64
            id = winApp.canvas.create_image(
                x, 0, image=self.health1_src, anchor='nw')
            self.health_ids.append(id)

    def draw(self):
        winApp.canvas.coords(self.img_id, self.position[0], self.position[1])

    def die(self):
        self.dead = True


player = _player(winApp, 320, 296)
# -------- mobs --------


class _mob(_move):
    def __init__(self, plat_id, x, y, min_x, max_x):
        super().__init__(t, x, y, -128+world_scrollx)
        self.plat_id = plat_id  # platform id to which mob belongs

        self.min_x = min_x  # for moving back and forth
        self.max_x = max_x
        fnames = ["mob1.png", "mob2.png", "mob3.png", "mob4.png"]
        fname = choice(fnames)
        self.img_src = PhotoImage(file=fname)
        self.img_id = winApp.canvas.create_image(
            self.position[0], self.position[1], image=self.img_src, anchor='nw')

    def draw(self):
        winApp.canvas.coords(self.img_id, self.position[0], self.position[1])

    def move(self, t):
        plat_pos = platforms[self.plat_id].position
        if self.position[0] >= self.max_x+plat_pos[0]:
            self.update(t, plat_pos[0]+self.max_x-10, None, -128+world_scrollx)
        if self.position[0] <= self.min_x+plat_pos[0]:
            self.update(t, plat_pos[0]+self.min_x+10, None, 128+world_scrollx)
        super().move(t)


mob_id_pool = []
for i in range(0, 50):
    mob_id_pool.append(i)

mobs = OrderedDict()


def gen_mobs(platform):
    mob_n = randint(1, round(platform.chunks*1.2))
    if mob_n == 0:
        return
    interval = floor(platform.chunks*256/mob_n)

    for i in range(0, mob_n):
        # relative px from start of platform, requires position[0] for absolute
        ivl_strt = (interval*i)
        ivl_end = ivl_strt+interval-65
        if i==0:
            ivl_strt+=96
        # 64px of sprite + -1 non inclusive
        x = randint(
            ivl_strt+round(platform.position[0]), ivl_end+round(platform.position[0]))
        y = platform.position[1]-64

        mob_id = mob_id_pool.pop()
        mobs[mob_id] = _mob(platform.id, x, y, ivl_strt, ivl_end)
        platform.mob_ids.append(mob_id)

# -------- platforms --------


class _platform(_move):
    img_start = PhotoImage(file="platform.png")

    def __init__(self, id, x, y, chunks):
        super().__init__(t, x, y, world_scrollx)
        self.chunks = chunks
        self.mob_ids = []
        self.id = id  # id of itself in platforms[]
        self.img_ids = []
        for i in range(0, chunks):
            # x offset for platform part, 256x32
            x_c = self.position[0]+(256*i)
            self.img_ids.append(winApp.canvas.create_image(
                x_c, self.position[1], image=self.img_start, anchor='nw'))

    def draw(self):
        for i in range(0, self.chunks):
            x_c = self.position[0]+(256*i)
            y_c = self.position[1]
            winApp.canvas.coords(self.img_ids[i], x_c, y_c)


plat_id_pool = []
for i in range(0, 8):
    plat_id_pool.append(i)

platforms = OrderedDict()
i = plat_id_pool.pop()
platforms[i] = _platform(i, 0, 640, 5)  # inital platform to start


def platform_add():
    space = randint(128, 256)
    space_x = randint(64, space)  # elon musk incoming
    space_y = round(sqrt(space**2-space_x**2))
    last_plat = list(platforms.items())[-1][1]
    last_x, last_y = last_plat.position
    last_x = last_x+(last_plat.chunks*256)
    r = randint(0, 1)
    if last_y+space_y > 540:
        y = last_y-space_y
    elif last_y-space_y < 180:
        y = last_y+space_y
    else:
        r = randint(0, 1)
        if r:
            y = last_y+space_y
        else:
            y = last_y-space_y
    x = last_x+space_x
    chunks = randint(2, 5)
    plat_id = plat_id_pool.pop()
    platforms[plat_id] = _platform(plat_id, x, y, chunks)
    gen_mobs(platforms[plat_id])


for i in range(0, 5):  # initialise platforms
    platform_add()


def platform_swapchk():
    end_plat = list(platforms.items())[0][1]
    end_posx = end_plat.position[0]+(end_plat.chunks*256)
    if end_posx < 0:
        id_free = list(platforms.keys())[0]
        for mob_id in platforms[id_free].mob_ids:
            del mobs[mob_id]
            mob_id_pool.append(mob_id)
        plat_id_pool.append(id_free)
        del platforms[id_free]
        platform_add()


def move(t):
    player.move(t)
    for id in platforms:
        platforms[id].move(t)
    for id in bullets:
        bullets[id].move(t)
    for id in mobs:
        mobs[id].move(t)

 # -------- gameloop --------


while not winApp.destroyed and not player.dead:
    if winApp.paused:
        winApp.root.update()
    else:
        t = (time()-t_n)**1.1
        platform_swapchk()
        bullets_clean()
        move(t)
        collisionhdl()
        winApp.score_update(t)
        winApp.root.update()
winApp.root.destroy()
