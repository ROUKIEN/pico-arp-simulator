from ursina import *
from ursina.networking import *
from ursina.shaders import lit_with_shadows_shader
from PIL import Image
from arp_simulator import Robot, CollisionHandler, LineDetectorHandler, DistanceSensorHandler

isDebug = False

# create a window
app = Ursina(
    title="Pico ARP simulator",
    editor_ui_enabled=isDebug,
    development_mode=not isDebug,
    borderless=False,
)

followPic = 'assets/circuit_cadlab.png'

bot = Robot()

planePicture = Image.open(followPic)
realPlaneWidth, realPlaneHeight = planePicture.size

scaleFactor = 40
plane = Entity(model='quad', z=.1, texture=followPic, rotation_x=90, y=1, scale=(realPlaneWidth/scaleFactor, realPlaneHeight/scaleFactor), collider='box', shader=lit_with_shadows_shader)

boundary_length = 102
boundaries = [
    Entity(model='cube', color=color.white, scale_x=boundary_length, x=0, z=boundary_length/2, collider='box', shader=lit_with_shadows_shader),
    Entity(model='cube', color=color.white, scale_x=boundary_length, x=0, z=-boundary_length/2, collider='box', shader=lit_with_shadows_shader),
    Entity(model='cube', color=color.white, scale_z=boundary_length, x=boundary_length/2, z=0, collider='box', shader=lit_with_shadows_shader),
    Entity(model='cube', color=color.white, scale_z=boundary_length, x=-boundary_length/2, z=0, collider='box', shader=lit_with_shadows_shader),
]

for boundary in boundaries:
    boundary.y = 2

distanceForward = -1
distanceForwardText = Text(text=f'{distanceForward}', y=-.4, x=-.6, z=-1, scale=1, origin=(0, 0))

# set the blueprint color as a background color (#0563c5)
window.color = color.color(210.63, .9746, .7725)
if not isDebug:
    window.entity_counter.enabled = False
    window.fps_counter.enabled = False
    window.collider_counter.enabled = False
    window.cog_menu.enabled = False

window.exit_button.enabled = False

AmbientLight(color = color.rgba(100, 100, 100, 0.1))

if isDebug:
    EditorCamera()

pivot = Entity()
dl = DirectionalLight(parent=pivot, y=10, z=15, shadows=True)
dl.look_at(bot.world_position)

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
app.run(info=isDebug)
