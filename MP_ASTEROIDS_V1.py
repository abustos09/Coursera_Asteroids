"""
missile_info > lifespan should be 50

""" 



 # program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
started = False
SHOOT = False

A_time = 0
EXPLOSION_DIM = 24


# globals for the asteroid's

# rock position 
rock_width = random.randrange(1, WIDTH)
rock_height = random.randrange(1, HEIGHT)
#rock velocity 
lower = -.3
rock_vel = [random.random() * .6 + lower, random.random() * .6 + lower]

# rock angle vel
rock_angle_vel = random.random() * .16 + -.08


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
missile_info = ImageInfo([5,5], [10, 10], 3, 33)
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
        #canvas.draw_circle(self.pos, self.radius, 1, "White", "White")
        canvas.draw_image(self.image, self.image_center, self.image_size, \
            self.pos, self.image_size, self.angle)
        

    def update(self):
        # angular roatation 
        self.angle += self.angle_vel
        velocity_vector = angle_to_vector(self.angle)

        # class velocity update by means of vector velocity in vector direction
        if self.thrust == True:
            self.vel[0] += velocity_vector[0] * .048
            self.vel[1] += velocity_vector[1] * .048
        else:
            self.vel[0] *= .98
            self.vel[1] *= .98

        # thruster flames on/off 
        if self.thrust == True:
            self.image_center = [135, 45]
            self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
            self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        else:
            self.image_center = [45, 45] 
            self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
            self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        
        # thruster sound
        if self.thrust == True:
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.rewind()

    def get_position(self):
            return self.pos

    def get_radius(self):
            return self.radius

    def missiles(self):
        

        # Velocity vector for gun/missile needed. This must be seperate from the V_V calculated
        # for the ship. 
        gun_velocity_vector = angle_to_vector(self.angle)

        # This will calculate the starting draw position of the missile at the front tip of 
        # the ship
        missile_start_pos = self.pos[0] + (self.image_size[0] / 2) * gun_velocity_vector[0], \
        self.pos[1] + (self.image_size[1] / 2) * gun_velocity_vector[1]

        # Call to Sprite
        a_missile = Sprite(missile_start_pos, self.vel, self.angle, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)
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
        global A_time
        #canvas.draw_circle(self.pos, self.radius, 1, "Red", "Red")
        if not self.animated:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
        else:
            current_explosion_index = (A_time % EXPLOSION_DIM) // 1
            current_explosion_center = [self.image_center[0] + current_explosion_index * self.image_size[0] , self.image_center[1]]
            canvas.draw_image(self.image, current_explosion_center, self.image_size, self.pos, self.image_size, self.angle)
            A_time += .5

    def get_position(self):
            return self.pos

    def get_radius(self):
            return self.radius

    def update(self):
        # spin. 0 spin for missile (through angle_vel = 0). angle will dictate angle missile 
        # will shoot. angle_vel > 0 will add spin to meteor
        if not self.animated:
            self.angle += self.angle_vel  
        
            # Test will decide if it is a meteor(angle_vel > 0) or
            # a missile (angle_vel == 0). If it is a missile, the velocity will
            # be updated (repeatedly as update is called within draw()).
            if self.angle_vel == 0:
                velocity_vector = angle_to_vector(self.angle)
                self.vel[0] += velocity_vector[0] * .4
                self.vel[1] += velocity_vector[1] * .4

            # Pos will be updated for all sprites
            self.pos[0] = (self.pos[0] + self.vel[0]) % 800
            self.pos[1] = (self.pos[1] + self.vel[1]) % 600
        
        self.age += 1
        if self.age >= self.lifespan:
            return True 
        else:
            return False

    def collide(self, other_object):
        #global lives
        if dist(other_object.get_position(), self.pos) <= self.radius + other_object.get_radius():
            return True
        else:
            return False

        """
        if other_object.get_position()[0] + other_object.get_radius() <= self.pos[0] + self.radius and \
        other_object.get_position()[1] + other_object.get_radius() <= self.pos[1] + self.radius:
            return True
        else:
            return False

        """

def draw(canvas):
    global time, lives, score, started
    
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
    #a_rock.draw(canvas)
    process_sprite_group(canvas, rock_group, missile_group, explosion_group)



    """
    if SHOOT == True:
        a_missile.draw(canvas)
        a_missile.update()
    """

    # update ship and sprites
    my_ship.update()
    #a_rock.update()

    #a_rock.update()


    if group_group_collide(rock_group, missile_group):
        score += 1

    #draws scores and lives in frame
    if group_collide(rock_group, my_ship):
        lives -= 1

    if lives <= 0:
        started = False
        lives = 3
        score = 0
        soundtrack.rewind()


    canvas.draw_text("Score: " + str(score), [WIDTH - 80, HEIGHT - 25], 20, "white")
    canvas.draw_text("Lives: " + str(lives), [WIDTH - 80, HEIGHT - 5], 20, "white")



    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())    

def group_group_collide(rocks, missiles):
    """min 11 in video collisions for sprites: 
    instead of all this logic, 
    make a call to group_collide
    """

    exploding_rocks = []

    for r in rocks:
        for m in missiles:
            if r.collide(m):
                exploding_rocks.append(r)
                explosion = Sprite(r.pos, [0,0], 0, [0,0], explosion_image, explosion_info, explosion_sound)
                explosion_group.add(explosion)

    for e in exploding_rocks:
        rocks.remove(e)
        return True


def group_collide(b_rocks, b_ship):
    """
    updating the rocks in here, (b_rocks), will actually update the set rock_group

    why?
    Python doesn't copy objects you pass during a function call ever.
    - since you dont assign b_rocks to anything within the funtion, 
    b_rocks acts as a global rocks_group under a copyNAME.

    """
*********
    exploding_rocks = []

    for r in b_rocks:
        if r.collide(b_ship):
            exploding_rocks.append(r)
            explosion = Sprite(r.pos, [0,0], 0, [0,0], explosion_image, explosion_info, explosion_sound)
            explosion_group.add(explosion)
            
    if len(exploding_rocks) > 0:
        for e in exploding_rocks:
            b_rocks.remove(e) 
        return True 
    else:
        return False
**********

 
def process_sprite_group(canvas, rocks, missile, explosions):
    for r in rocks:
        r.draw(canvas)
        r.update()

    expired_missiles = []
    for m in missile:
        if m.update():
            expired_missiles.append(m)

    for e in expired_missiles:
        missile.remove(e)

    for m in missile:
        m.draw(canvas)
        m.update()

    expired_explosions = []
    for e in explosions:
        e.draw(canvas)
        if e.update():
            expired_explosions.append(e)
    for e in expired_explosions:
        explosions.remove(e)
    
    """
    exploding_rocks = []
    for r in rocks:
        if r.collide(my_ship):
            exploding_rocks.append(r)
            explosion = Sprite(r.pos, [0,0], 0, [0,0], explosion_image, explosion_info)
            explosion.draw(canvas)

    for e in exploding_rocks:
        rocks.remove(e)
    """


# timer handler that spawns a rock 
def rock_spawner():
    global asteroid_image, rock_group
    
    # rock position 
    rock_width = random.randrange(1, WIDTH)
    rock_height = random.randrange(1, HEIGHT)
    rock_pos = [rock_width, rock_height]

    #rock velocity 
    lower = -.3
    rock_vel = [random.random() * .6 + lower, random.random() * .6 + lower]

    # rock angle vel
    rock_angle_vel = random.random() * .16 + -.08

    # all 3 asteroid images
    asteroid_image_A = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blend.png")
    asteroid_image_B = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")
    asteroid_image_C = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_brown.png")
    asteroid_image = random.choice([asteroid_image_A,asteroid_image_B, asteroid_image_C])

    # Sprite class call
    
    # Sprite class call
    if started == True:
        if len(rock_group) >= 12:
            return 
        else:
            a_rock = Sprite(rock_pos, rock_vel, 1, rock_angle_vel , asteroid_image, asteroid_info)
            if dist(rock_pos, my_ship.get_position()) >= my_ship.get_radius() + a_rock.get_radius():
                rock_group.add(a_rock)
            else:
                return 
    else:
        rock_group = set()

# Button handler=
def keydown(key):
    global SHOOT

    if key == simplegui.KEY_MAP['up']:
        my_ship.thrust = True

    elif key == simplegui.KEY_MAP['left']:
        my_ship.angle_vel = -.05
        #add calls to a new method inside ship class to decrease angle

    elif key == simplegui.KEY_MAP['right']:
        my_ship.angle_vel = .05
        #add calls to a new method inside ship class to increase angle
    elif key == simplegui.KEY_MAP['space']:
        #SHOOT = True
        my_ship.missiles()


    elif key == simplegui.KEY_MAP['a']:
        print rock_group

def keyup(key):

    if key == simplegui.KEY_MAP['up']:
        my_ship.thrust = False
        
    elif key == simplegui.KEY_MAP['left']:
        my_ship.angle_vel = 0

    elif key == simplegui.KEY_MAP['right']:
        my_ship.angle_vel = 0

def mouseclick(pos):
    global started

    if WIDTH / 2 - splash_info.get_size()[0] / 2 <= pos[0] <= WIDTH / 2 + splash_info.get_size()[0] / 2 and \
    HEIGHT / 2 - splash_info.get_size()[1] / 2 <= pos[1] <= HEIGHT / 2 + splash_info.get_size()[1] / 2:
        started = True
        soundtrack.play()

   


# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)


#a_rock = Sprite([WIDTH / 3, HEIGHT / 3], [1, 1], 0, .07, asteroid_image, asteroid_info)
rock_group = set()
#a_rock = Sprite([rock_width, rock_height], rock_vel, 1, rock_angle_vel , asteroid_image, asteroid_info)
#rock_group.add(a_rock)

#a_missile = Sprite()
missile_group = set()
#a_missile = Sprite([2 * WIDTH / 3, 2 * HEIGHT / 3], [0, 0], 0, 0, missile_image, missile_info, missile_sound)

explosion_group = set()

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(mouseclick)


timer = simplegui.create_timer(1500.0, rock_spawner)

# get things rolling
timer.start()
frame.start()