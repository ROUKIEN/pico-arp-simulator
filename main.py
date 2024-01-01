from ursina import *
from PIL import Image
from arp_simulator import Robot, CollisionHandler, LineDetectorHandler, DistanceSensorHandler

# create a window
app = Ursina()

followPic = 'assets/ligne_a_suivre.png'

bot = Robot()

planePicture = Image.open(followPic)
realPlaneWidth, realPlaneHeight = planePicture.size

scaleFactor = 50
plane = Entity(model='quad', z=.1, texture=followPic, rotation_x=90, y=1, scale=(realPlaneWidth/scaleFactor, realPlaneHeight/scaleFactor), collider='box')

boundary_length = 60
boundaries = [
    Entity(model='cube', color=color.white, scale_x=boundary_length, x=0, z=boundary_length/2, collider='box'),
    Entity(model='cube', color=color.white, scale_x=boundary_length, x=0, z=-boundary_length/2, collider='box'),
    Entity(model='cube', color=color.white, scale_z=boundary_length, x=boundary_length/2, z=0, collider='box'),
    Entity(model='cube', color=color.white, scale_z=boundary_length, x=-boundary_length/2, z=0, collider='box'),
]

for boundary in boundaries:
    boundary.y = 2

distanceForward = -1
distanceForwardText = Text(text=f'{distanceForward}', y=-.4, x=-.6, z=-1, scale=1, origin=(0, 0))

# set the blueprint color as a background color (#0563c5)
window.color = color.color(210.63, .9746, .7725)

AmbientLight()

isDebug = True

if isDebug:
    EditorCamera()

collisionHandler = CollisionHandler(bot, boundaries, camera, isDebug)
ldh = LineDetectorHandler(plane, bot, planePicture, scaleFactor, isDebug)
dsh = DistanceSensorHandler(bot, boundaries, distanceForwardText, isDebug)

# start running the game
app.run()
