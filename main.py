from ursina import *
from PIL import Image

# create a window
app = Ursina()

followPic = 'assets/ligne_a_suivre.png'
player = Entity(model='assets/pico_arp.gltf', scale=.4, y=2, collider='box')

planePicture = Image.open(followPic)
realPlaneWidth, realPlaneHeight = planePicture.size

scaleFactor = 50

planeWidth = realPlaneWidth/scaleFactor
planeHeight = realPlaneHeight/scaleFactor

plane = Entity(model='quad', z=.1, texture=followPic, rotation_x=90, y=1, scale=(planeWidth, planeHeight), collider='box')

lineDetectorCenter = Entity(model='cube', scale=.1, parent=player, z=3.72, y=-.6, color=color.white, visible=False)
lineDetectorLeft = Entity(model='cube', scale=.1, parent=player, z=2.98, y=-.6, x=-.71, color=color.white, visible=False)
lineDetectorRight = Entity(model='cube', scale=.1, parent=player, z=2.98, y=-.6, x=.71, color=color.white, visible=False)

lineDetectSensors = [
    lineDetectorCenter,
    lineDetectorLeft,
    lineDetectorRight
]

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
floorCenterCoords = Text(text='', y=-.45, x=-.673, z=-1, scale=1, origin=(0, 0))
floorLeftCoords = Text(text='', y=-.45, x=-.75, z=-1, scale=1, origin=(0, 0))
floorRightCoords = Text(text='', y=-.45, x=-.80, z=-1, scale=1, origin=(0, 0))

# set the blueprint color as a background color (#0563c5)
window.color = color.color(210.63, .9746, .7725)

AmbientLight()

cameraOffset = 30
speed = 10
speedRotation = 4
robotAngle = 0

isDebug = True

if isDebug:
    EditorCamera()

def intersectsWithWall(walls, robot: Entity) -> bool:
    for wall in walls:
        intersection = wall.intersects(robot)
        if intersection.hit:
            return True
    return False

def update():
    global robotAngle # dunno why is it needed :shrug:
    robotAngle -= held_keys['a'] * speedRotation
    robotAngle += held_keys['d'] * speedRotation
    robotAngle = robotAngle % 360
    angleRad = robotAngle / 180 * pi

    direction = 0
    if held_keys['w']:
        direction = 1
    elif held_keys['s']:
        direction = -1

    prevX = player.x
    prevZ = player.z

    player.z += cos(angleRad) * (speed*direction) * time.dt
    player.x += sin(angleRad) * (speed*direction) * time.dt
    player.rotation_y = robotAngle

    if intersectsWithWall(boundaries, player):
        player.x = prevX
        player.z = prevZ

    if not isDebug:
        camera.position = (player.position.x - cameraOffset, player.position.y + cameraOffset, player.position.z -cameraOffset)
        camera.look_at(player.world_position)

    # ultrasonic checks
    ultrasonicSensor = raycast(player.world_position, player.forward, ignore=(player,), distance=100, debug=isDebug)
    if ultrasonicSensor.hit:
        distanceForward = round(ultrasonicSensor.distance, 3)
        distanceForwardText.text = f"distance avant: {distanceForward}"

    # line detection
    for lineDetector in lineDetectSensors:
        castColor = color.white
        if lineDetector.color[3] != 0:
            castColor = lineDetector.color
        lineDetect = raycast(lineDetector.world_position, player.down, ignore=(player,), distance=2, debug=isDebug, color=castColor)
        if lineDetect.hit:
            imgX = plane.scale_x/2 + lineDetect.world_point.x
            imgY = plane.scale_y/2 + lineDetect.world_point.z

            imgX = int(imgX * scaleFactor)
            imgY = int(imgY * scaleFactor)

            pixel = plane.texture.get_pixel(imgX, imgY)
            if pixel:
                lineDetector.color = pixel
                lineDetector.visible = True
            else:
                lineDetector.visible = False

# start running the game
app.run()
