from ursina import *
from ursina.networking import *
from PIL import Image
from arp_simulator import Robot, CollisionHandler, LineDetectorHandler, DistanceSensorHandler

# create a window
app = Ursina()

followPic = 'assets/circuit.png'

bot = Robot()

planePicture = Image.open(followPic)
realPlaneWidth, realPlaneHeight = planePicture.size

scaleFactor = 50
plane = Entity(model='quad', z=.1, texture=followPic, rotation_x=90, y=1, scale=(realPlaneWidth/scaleFactor, realPlaneHeight/scaleFactor), collider='box')

boundary_length = 70
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

isDebug = False

if isDebug:
    EditorCamera()

collisionHandler = CollisionHandler(bot, boundaries, camera, isDebug)
ldh = LineDetectorHandler(plane, bot, planePicture, scaleFactor, isDebug)
dsh = DistanceSensorHandler(bot, boundaries, distanceForwardText, isDebug)

peer = Peer()

def on_connect(connection, time_connected):
    print("Connected to", connection.address)

def on_disconnect(connection, time_disconnected):
    print("Disconnected from", connection.address)

def on_data(connection, data, time_received):
    result = data.decode("utf-8")

    if result == "avance":
        bot.state = "avance"
    elif result == "recule":
        bot.state = "recule"
    elif result == "stop":
        bot.state = "stop"
    elif result == "tourne_droite":
        bot.state = "tourne_droite"
    elif result == "tourne_gauche":
        bot.state = "tourne_gauche"
    elif result == "distance":
        connection.send(bytes(str(bot.distance_forward), encoding="utf-8"))
    elif result == "suivi_ligne":
        colors = f"{bot.ls_center};{bot.ls_left};{bot.ls_right}"
        connection.send(bytes(str(colors), encoding="utf-8"))
    else:
        pass

peer.on_connect = on_connect
peer.on_disconnect = on_disconnect
peer.on_data = on_data

peer.start("0.0.0.0", 12345, is_host=True)

def update():
    peer.update()

# start running the game
app.run()
