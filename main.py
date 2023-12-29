from ursina import *
#from math import *

# create a window
app = Ursina()

player = Entity(model='assets/gltf/pico_arp.gltf', scale=.4, y=2)
plane = Entity(model='quad', z=.1, texture='assets/ligne_a_suivre.png', rotation_x=90, scale=(40, 40))

# set the blueprint color as a background color
window.color = color.color(200.87, .575, .4706)

AmbientLight()

cameraOffset = 30
speed = 30
speedRotation = 4
robotAngle = 0

def update():
    global robotAngle # dunno why is it needed :shrug:
    robotAngle -= held_keys['d'] * speedRotation
    robotAngle += held_keys['a'] * speedRotation
    robotAngle = robotAngle%360
    angleRad = robotAngle / 180 * pi

    direction = 0
    if held_keys['w']:
        direction = 1
    elif held_keys['s']:
        direction = -1

    player.x += cos(angleRad) * (speed*direction) * time.dt
    player.z += sin(angleRad) * (speed*direction) * time.dt
    player.rotation_y = -robotAngle

    camera.position = (player.position.x - cameraOffset, player.position.y + cameraOffset, player.position.z -cameraOffset)
    camera.look_at(player.position)

def input(key):
    if key == 'space':
        player.y += 1
        invoke(setattr, player, 'y', player.y-1, delay=.25)

# start running the game
app.run()
