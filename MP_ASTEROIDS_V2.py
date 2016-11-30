# program template for Spaceship
import simpleguitk as simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0

started = False

# explosions
EXPLOSION_TIME = 0
EXPLOSION_DIM = 24

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 40)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# alternative upbeat soundtrack by composer and former IIPP student Emiel Stopler
# please do not redistribute without permission from Emiel at http://www.filmcomposer.nl
#soundtrack = simplegui.load_sound("https://storage.googleapis.com/codeskulptor-assets/ricerocks_theme.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        # if thrust is off, it will draw first tiled image. 
        # if thrust is on , it will draw the second tiles image 
        if not self.thrust:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0] , self.image_center[1]], self.image_size, self.pos, self.image_size, self.angle)

    def turn(self, direction):
        # moves the ship left and right when key is down 
        if direction == "left":
            self.angle_vel = -.05
        else:
            self.angle_vel = .05

    def turn_stop(self):
        # stops the angular left and right movememt when key_up
        self.angle_vel = 0

    def thruster(self, on):
        # updates thrust on/off in response to the key_up/key_down handler
        if on:
            self.thrust = True
            ship_thrust_sound.play()

        else:
            self.thrust = False
            ship_thrust_sound.rewind()

    def update(self):
        # update the turn response
        self.angle += self.angle_vel

        # compute forward vector > angle_to_vector
        velocity_vector = angle_to_vector(self.angle)

        # class velocity update by means of vector velocity in vector direction
        if self.thrust:
            self.vel[0] += velocity_vector[0] * .048
            self.vel[1] += velocity_vector[1] * .048
        else:
            self.vel[0] *= .98
            self.vel[1] *= .98
        
        # position update 
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) %  HEIGHT

    def shoot(self):
        #global a_missile
        # Velocity vector for gun/missile needed. This must be seperate from the Vel_Vec calculated
        # for the ship. 
        gun_velocity_vector = angle_to_vector(self.angle)

        misille_velocity = [self.vel[0] + gun_velocity_vector[0] * 1.7, self.vel[1] + gun_velocity_vector[1] * 1.7]

        # This will calculate the starting draw position of the missile at the front tip of 
        # the ship
        missile_start_pos = self.pos[0] + (self.image_size[0] / 2) * gun_velocity_vector[0], \
        self.pos[1] + (self.image_size[1] / 2) * gun_velocity_vector[1]

        # Create a missile Sprite 
        a_missile = Sprite(missile_start_pos, misille_velocity, self.angle, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius

# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        global EXPLOSION_TIME
        if not self.animated:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
        else:
            explosion_index = (EXPLOSION_TIME % EXPLOSION_DIM) // 1
            explosion_center = [self.image_center[0] + explosion_index * self.image_size[0] , self.image_center[1]]
            canvas.draw_image(self.image, explosion_center, self.image_size, self.pos, self.image_size, self.angle)
            EXPLOSION_TIME += .5

    def update(self):
        # angle update > spin 
        if not self.animated:
            self.angle += self.angle_vel    
                 
        # Test will decide if it is an asteroid (angle_vel > 0) or
        # a_missile (angle_vel == 0). If it is a missile, the velocity will
        # be updated repeatedly (as the update is called within draw()).
        if self.angle_vel == 0:
            velocity_vector = angle_to_vector(self.angle)
            self.vel[0] += velocity_vector[0] * .4
            self.vel[1] += velocity_vector[1] * .4

        # Pos will be updated for all sprites
        self.pos[0] = (self.pos[0] + self.vel[0]) % 800
        self.pos[1] = (self.pos[1] + self.vel[1]) % 600  

        # lifespan
        self.age += 1
        if self.age >= self.lifespan:
            return True  

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius

    def collide(self, other_object):
        if dist(other_object.get_position(), self.get_position()) <= other_object.get_radius() + self.get_radius():
            return True
        else:
            return False

def click(pos):
    global started
    Splash_center = [WIDTH / 2, HEIGHT / 2]
    Splash_size = splash_info.get_size()

    if (Splash_center[0] - Splash_size[0] / 2 < pos[0] < Splash_center[0] + Splash_size[0] / 2 and
        Splash_center[1] - Splash_size[1] / 2 < pos[1] < Splash_center[1] + Splash_size[1] / 2):
        started = True 
        soundtrack.play()

def draw(canvas):
    global time, score, lives, started, rock_group
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship and sprites
    my_ship.draw(canvas)
    #a_missile.draw(canvas)
    
    # update ship and sprites
    my_ship.update()
    #a_missile.update()

    # call process_sprite_groups for sprite sets
    # process_sprite_group will update and draw for each sprite
    process_sprite_group(canvas, rock_group, missile_group, explosion_group)

    # group_collide call and lives update
    if group_collide(rock_group, my_ship):
        lives -= 1

    # group_group_collide call and score update
    if group_group_collide(rock_group, missile_group):
        score += 1


    # draw user interface
    canvas.draw_text("Score: " + str(score), [50, 50], 22, "white")
    canvas.draw_text("Lives: " + str(lives), [680, 50], 22, "white")

    # draw splash screen
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                        splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                        splash_info.get_size())
    # game restart
    if lives <= 0:
        lives = 3
        score = 0
        soundtrack.rewind()
        rock_group = set([])
        started = False

def group_collide(rocks, other_sprite):
    for r in list(rocks):
        if r.collide(other_sprite):
            rocks.remove(r)
            explosion = Sprite(r.get_position(), [0,0], 0, [0,0], explosion_image, explosion_info)
            explosion_group.add(explosion)
            return True

def group_group_collide(rocks, missiles):
    for m in list(missiles):
        if group_collide(rocks, m):
            missiles.remove(m)
            return True
            
    """
    This seems less confusing:

    for r in list(rocks):
        for m in list(missiles):
            if r.collide(m):
                rocks.remove(r)
                missiles.remove(m)
                return True
    """  

def process_sprite_group(canvas, rockgroup, missilegroup, explosiongroup):
    for r in rockgroup:
        r.draw(canvas)
        r.update()

    for m in list(missilegroup):
        m.draw(canvas)
        if m.update():
            missilegroup.remove(m)

    for e in list(explosiongroup):
        e.draw(canvas)
        if e.update():
            explosiongroup.remove(e)

def keyup(key):
    global flames

    if simplegui.KEY_MAP["up"] == key:
        flames = False
        my_ship.thruster(flames)

    elif simplegui.KEY_MAP["left"] == key:
        my_ship.turn_stop()

    elif simplegui.KEY_MAP["right"] == key:
        my_ship.turn_stop()

def keydown(key):
    global flames

    if simplegui.KEY_MAP["up"] == key:
        flames = True
        my_ship.thruster(flames)

    elif simplegui.KEY_MAP["left"] == key:
        my_ship.turn("left")

    elif simplegui.KEY_MAP["right"] == key:
        my_ship.turn("right")

    elif simplegui.KEY_MAP["space"] == key:
        my_ship.shoot()
               
# timer handler that spawns a rock    
def rock_spawner():
    global a_rock, rock_group
    
    # random rock_pos
    rock_pos = [random.randrange(1, WIDTH), random.randrange(1, HEIGHT)]

    # random velocity 
    # if score is greater than 15, velocity upper and lower width limits will increase
    if score <= 15:
        lower = -1
        range_width = 2
        velocity = [(random.random() * range_width + lower),(random.random() * range_width + lower)]
    else:
        lower = -1.5
        range_width = 3
        velocity = [(random.random() * range_width + lower),(random.random() * range_width + lower)]

    # random angle_velocity
    a_lower = -.1
    a_range_width = .2
    random.random() * range_width + lower
    angle_velocity = (random.random() * a_range_width + a_lower)

    # all 3 asteroid images
    asteroid_image_A = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blend.png")
    asteroid_image_B = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")
    asteroid_image_C = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_brown.png")
    asteroid_image = random.choice([asteroid_image_A,asteroid_image_B, asteroid_image_C])

    # Sprite call
    if started:
        if len(rock_group) < 12:
            a_rock = Sprite(rock_pos , velocity, 0, angle_velocity, asteroid_image, asteroid_info)
            if dist(rock_pos, my_ship.get_position()) > my_ship.get_radius() + a_rock.get_radius():
                rock_group.add(a_rock)
            else:
                None
    else:
        rock_group = set([])

# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
rock_group = set([])
missile_group = set([])

# initialize explostion set
explosion_group = set([])
# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
