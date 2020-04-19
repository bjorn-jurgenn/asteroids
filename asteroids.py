import math, pyglet
from pyglet.window import key
from pyglet import gl, clock
from random import randint, uniform

ASTEROID_IMG = ['./img/asteroids/00.png','./img/asteroids/01.png','./img/asteroids/02.png','./img/asteroids/03.png',
'./img/asteroids/04.png','./img/asteroids/05.png','./img/asteroids/06.png']

HEIGHT = 600
WIDTH = 800
LABEL_SIZE = HEIGHT // 20
LEVEL_SIZE = HEIGHT // 40
ROTATION_SPEED = 4
ACCELERATION = 300
LASER_SPEED = 300
LASER_SIZE = 8
MAX_LEVEL = 3
ASTEROIDS = [3, 5, 8] #number of asteroids generated in level

status = '.'
objects = []
level = 1
level_speed = [(5, 10), (8, 20), (12, 30)] #max and min speed of asteroid in each level
pressed_keys = set()
batch = pyglet.graphics.Batch()
window = pyglet.window.Window(width=WIDTH, height=HEIGHT)

label = pyglet.text.Label(f'LEVEL {level}',
                          font_size=LABEL_SIZE,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

level_label = pyglet.text.Label('LEVEL 1',
                        font_size=LEVEL_SIZE,
                        x=window.width - LEVEL_SIZE // 2, y=LEVEL_SIZE // 2,
                        anchor_x='right', batch=batch)

class SpaceObject:
    """Class containgn all space objects"""
    def __init__(self, x, y, rotation, img):
        """Initialize space object - coordinates, speed, anchor and rotation, creates sprite"""
        self.x = x
        self.y = y
        self.x_speed = 0
        self.y_speed = 0
        self.rotation = rotation
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        self.sprite = pyglet.sprite.Sprite(img, batch=batch)

    def tick(self, dt):
        """Moves object during time"""
        self.x = self.x + dt * self.x_speed
        self.y = self.y + dt * self.y_speed

        #adds arguments also to sprite
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.rotation = 90 - math.degrees(self.rotation)
        self.sprite.x_speed = self.x_speed
        self.sprite.y_speed = self.y_speed

        #moves object back to canvas when the object moves out of it
        if self.x > WIDTH:
            self.x -= WIDTH
            if isinstance(self, Laser):
                self.x_start -= WIDTH
        if self.x < 0:
            self.x += WIDTH
            if isinstance(self, Laser):
                self.x_start += WIDTH
        if self.y > HEIGHT:
            self.y -= HEIGHT
            if isinstance(self, Laser):
                self.y_start -= HEIGHT
        if self.y < 0:
            self.y += HEIGHT
            if isinstance(self, Laser):
                self.y_start += HEIGHT

    def delete(self):
        """Delete space object and its sprite"""
        self.sprite.delete()
        objects.remove(self)

class Spaceship(SpaceObject):
    """Class containing spaceship"""
    def __init__(self):
        """Initialize spaceship, adds shooting ability (in seconds), calculates radius"""
        self.ingame = False
        self.shooting_ability = float(0.3) #ability to shoot once 0.3 second
        img = pyglet.image.load('img/spaceship.png')
        if img.height > img.width:
            self.radius = img.height // 2
        else:
            self.radius = img.width // 2
        super().__init__(WIDTH // 2, HEIGHT // 2, uniform(-(math.pi) / 2, math.pi / 2), img)

    def set_ingame(self, *args):
        """Changes ingame status of Spaceship (ship can be now destroyed by asteroid)"""
        pyglet.clock.unschedule(self.set_ingame)
        self.ingame = True
        return self

    def shoot(self):
        """Posibility to shoots laser creates instance of class laser"""
        laser = Laser(self.x, self.y, self.rotation)
        objects.append(laser)

    def hit_by_asteroid(self):
        """Returns true if Spaceship is hit by asteroid"""
        for item in objects:
                if isinstance(item, Asteroid):
                    a = abs(self.x - item.x)
                    b = abs(self.y - item.y)
                    distance = math.sqrt(a**2 + b**2)
                    if (self.radius + item.radius) > distance:
                        print('Hit by asteroid')
                        return True


    def tick(self, dt):
        """Operates the ship - moving, rotating, controls
        checks if ship is hit by asteroid and if it is, deletes the ship"""
        self.shooting_ability -=  dt
        if 'UP' in pressed_keys:
            self.x_speed += dt * ACCELERATION * math.cos(self.rotation)
            self.y_speed += dt * ACCELERATION * math.sin(self.rotation)
        if 'DOWN' in pressed_keys:
            self.x_speed -= dt * ACCELERATION * math.cos(self.rotation)
            self.y_speed -= dt * ACCELERATION * math.sin(self.rotation)
        if 'LEFT' in pressed_keys:
            self.rotation = self.rotation + dt * ROTATION_SPEED
        if 'RIGHT' in pressed_keys:
            self.rotation = self.rotation - dt * ROTATION_SPEED
        if ('SPACE' in pressed_keys) and (self.shooting_ability < 0):
            self.shooting_ability = float(0.3)
            self.shoot()
        super().tick(dt)
        if self.hit_by_asteroid() and self.ingame == True:
            self.delete()

class Laser(SpaceObject):
    """Class containing laser"""
    def __init__(self, x, y, rotation):
        """Initilizes laser which duration is limited"""
        img = pyglet.image.load('img/laser.png')
        self.length = img.height
        self.duration = math.sqrt((HEIGHT ** 2) + (WIDTH ** 2)) // 2.5
        self.x_start = x
        self.y_start = y
        super().__init__(x, y, rotation, img)

    def tick(self, dt):
        """Movement of laser,
        if duration expires, the laser disappears"""
        self.x_speed = dt * LASER_SPEED * ACCELERATION * math.cos(self.rotation)
        self.y_speed = dt * LASER_SPEED * ACCELERATION * math.sin(self.rotation)
        super().tick(dt)

        # laser travel lenght
        a = abs(self.x - self.x_start)
        b = abs(self.y - self.y_start)
        self.travelled = math.sqrt(a**2 + b**2)

        if self.duration <= self.travelled:
            self.delete()

class Asteroid(SpaceObject):
    """Class containing laser"""
    def __init__(self):
        """Initialize asteroid
        add image, count radius, set direction and speed coeficient"""
        img_path = ASTEROID_IMG[randint(0,6)]
        img = pyglet.image.load(img_path) #img_path

        #finding radius
        if img.height > img.width:
            self.radius = img.height // 2
        else:
            self.radius = img.width // 2
        #generate asteroids on axis (randomly) x or y, with direction up or left with some random angle
        if randint(0, 1) == 0:
            super().__init__(randint(self.radius,WIDTH - self.radius), self.radius, uniform(0, math.pi), img)
        else:
            super().__init__(self.radius, randint(self.radius, HEIGHT - self.radius), uniform(-(math.pi) / 2, math.pi / 2), img)

        #random speed coeficient depends on level (for each level is tuple in 'level_speed' list)
        self.speed_coef = randint(level_speed[level - 1][0], level_speed[level - 1][0])

    def tick(self, dt):
        """Movement of asteroid
        checks if asteroid was hit by laser"""
        self.x_speed = dt * self.speed_coef * ACCELERATION * math.cos(self.rotation)
        self.y_speed = dt * self.speed_coef * ACCELERATION * math.sin(self.rotation)
        super().tick(dt)

        #check if the asteroid was hit by some of the laser
        for item in objects:
            if isinstance(item, Laser):
                shortest = math.sqrt(WIDTH ** 2 + HEIGHT ** 2)
                #finds shortest distance between laser and center of asteroid
                for i in range((item.length // 2) + 1):
                    for k in (-1,1):
                        x = item.x + (k * i * math.cos(item.rotation))
                        y = item.y + (k * i * math.sin(item.rotation))
                        a = abs(self.x - x)
                        b = abs(self.y - y)
                        distance = math.sqrt(a**2 + b**2)
                        if distance < shortest:
                            shortest = distance
                # if the distance is shorter then radius of asteroid - the asteroid was hit
                if shortest <= self.radius + LASER_SIZE:
                    self.delete()

class Lives:
    """Class containing count of lives and its sprite"""
    def __init__(self, count):
        """Adds image visualisation of given number of lives in left-bottom corner to batch"""
        self.count = count
        self.sprites = list()
        for i in range(self.count):
            img = pyglet.image.load('img/spaceship.png')
            scale = 0.4
            indentation = (img.height // 4) * scale + (i * img.height * scale * 1.5)
            self.sprites.append(pyglet.sprite.Sprite(img, x=indentation, y=(img.height // 4) * scale,batch=batch))
            self.sprites[i].scale = scale

    def remove(self):
        """Remove one life and its sprite"""
        if self.count > 0:
            sprite = self.sprites.pop()
            sprite.delete()
            self.count -= 1


def get_status():
    """Returns current status of the game

    '+': no asteroids - next level
    '-': no ship, one more remaining live
    'x': no ship, but no more remaining live
    '*': no asteroids in last level
    '.': no ship, no asteroid - game is getting ready
    if game is running returns None"""
    if status == '.':
        return '.'

    ship_count = 0
    asteroid_count = 0
    for item in objects:
        if isinstance(item, Spaceship):
            ship_count += 1
        if isinstance(item, Asteroid):
            asteroid_count += 1

    if ship_count == 0:
        if asteroid_count == 0:
            return '.'
        elif lives.count <= 1:
            return('x')
        else:
            return('-')

    if asteroid_count == 0:
        global level
        if level == MAX_LEVEL:
            return('*')
        else:
            return('+')

def refresh(dt):
    """Depending on status, refreshes game"""
    global status, label
    status = get_status()
    if status == '+':
        pyglet.clock.schedule_once(restart_game, 3, '+')
        label.text = 'NEXT LEVEL'
        status = '.'
    elif status == '-':
        pyglet.clock.schedule_once(restart_game, 3, '-')
        label.text = 'SPACESHIP DESTROYED'
        lives.remove()
        status = '.'
    elif status == 'x':
        label.text = 'GAME OVER'
        lives.remove()
        status = '.'
    elif status == '*':
        label.text = 'VICTORY'
    else:
        for item in objects:
            item.tick(dt)

def press_key(symbol, modificator):
    """Checks if pressed key is one of control keys and add it to the 'pressed_key' variable"""
    if symbol == key.UP:
        pressed_keys.add('UP')
    if symbol == key.DOWN:
        pressed_keys.add('DOWN')
    if symbol == key.LEFT:
        pressed_keys.add('LEFT')
    if symbol == key.RIGHT:
        pressed_keys.add('RIGHT')
    if symbol == key.SPACE:
        pressed_keys.add('SPACE')

def release_key(symbol, modificator):
    """Checks if released key is one of control keys and removes it from the 'pressed_key' variable"""
    if symbol == key.UP:
        pressed_keys.discard('UP')
    if symbol == key.DOWN:
        pressed_keys.discard('DOWN')
    if symbol == key.LEFT:
        pressed_keys.discard('LEFT')
    if symbol == key.RIGHT:
        pressed_keys.discard('RIGHT')
    if symbol == key.SPACE:
        pressed_keys.discard('SPACE')

def on_draw():
    """draws all the items on canvas, duplicates the canvas to invisible areas"""
    window.clear()
    for x_offset in (-window.width, 0, window.width):
        for y_offset in (-window.height, 0, window.height):
            # Remember the current state
            gl.glPushMatrix()
            # Move everything drawn from now on by (x_offset, y_offset, 0)
            gl.glTranslatef(x_offset, y_offset, 0)

            # Draw
            batch.draw()
            global status, level
            if status != None:
                label.draw()

            # Restore remembered state (this cancels the glTranslatef)
            gl.glPopMatrix()

def set_game(*args):
    """Create ships, and asteroids"""
    pyglet.clock.unschedule(set_game)

    objects.clear()
    ship = Spaceship()
    pyglet.clock.schedule_once(ship.set_ingame, 3)
    objects.append(ship)

    global level, status
    for i in range(ASTEROIDS[level - 1]):
        objects.append(Asteroid())

    status = None

def restart_game(dt, status):
    """Restarts after end of level or losing life"""
    global level
    pyglet.clock.unschedule(restart_game)

    if status == '+':
        level += 1

    label.text = f'LEVEL {level}'
    level_label.text = f'LEVEL {level}'
    pyglet.clock.schedule_once(set_game, 3)



window.push_handlers(
    on_draw=on_draw,
    on_key_press=press_key,
    on_key_release=release_key
)
lives = Lives(3)
on_draw()
pyglet.clock.schedule_once(set_game, 3)
pyglet.clock.schedule(refresh)
pyglet.app.run()


#dodělat životy a rozstřelení