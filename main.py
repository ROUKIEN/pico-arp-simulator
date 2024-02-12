from ursina import *
from ursina.networking import *
from ursina.shaders import lit_with_shadows_shader
from PIL import Image
import os
from arp_simulator import Robot, CollisionHandler, LineDetectorHandler, DistanceSensorHandler

isDebug = False

# create a window
app = Ursina(
    title="Pico ARP simulator",
    editor_ui_enabled=isDebug,
    development_mode=not isDebug,
    borderless=False,
)

followPic = os.path.dirname(__file__)+'/assets/circuit_cadlab.png'

bots = {}

planePicture = Image.open(followPic)
followPic = "circuit_cadlab"

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

# set the blueprint color as a background color (#0563c5)
window.color = color.color(210.63, .9746, .7725)
if not isDebug:
    window.entity_counter.enabled = False
    window.fps_counter.enabled = False
    window.collider_counter.enabled = False
    window.cog_menu.enabled = False

window.exit_button.enabled = False

AmbientLight(color = color.rgba(100, 100, 100, 0.1))

cameraOffset = 50
# EditorCamera()
camera.position = (-cameraOffset, cameraOffset, -cameraOffset)
camera.look_at((0, 0, 0))

pivot = Entity()
dl = DirectionalLight(parent=pivot, y=10, z=15, shadows=True)
dl.look_at((0, 0, 0))

collisionHandler = CollisionHandler({}, boundaries)
ldh = LineDetectorHandler(plane, {}, planePicture, scaleFactor, isDebug)
dsh = DistanceSensorHandler({}, boundaries, isDebug)

peer = Peer()

def on_connect(connection, time_connected):
    print("Connected to", connection.address)

def on_disconnect(connection, time_disconnected):
    print("Disconnected from", connection.address)
    for cbotUuid in bots[connection.address]:
        robot = bots[connection.address][cbotUuid]

        collisionHandler.remove(robot)
        dsh.remove(robot)
        ldh.remove(robot)

        destroy(robot)

    bots.pop(connection.address)

def on_data(connection, data, time_received):
    result = data.decode("utf-8")

    action = result.split(':')
    cmd = action[0]
    if len(action) == 2:
        cmd_uuid = uuid.UUID(action[1])

    if cmd == "new_robot":
        new_bot = Robot()
        new_bot.x = int(action[1]) * 2
        new_bot.z = int(action[2]) * 2
        new_bot.angle = int(action[3])
        new_bot.uuid = uuid.uuid4()
        if connection.address not in bots:
            bots[connection.address] = {}
        bots[connection.address][new_bot.uuid] = new_bot

        collisionHandler.addRobot(bots[connection.address][new_bot.uuid])
        dsh.addRobot(bots[connection.address][new_bot.uuid])
        ldh.addRobot(bots[connection.address][new_bot.uuid])
        # send the uuid to the client so that they can send instructions to that specific robot
        connection.send(bytes(str(new_bot.uuid), encoding="utf-8"))
        return

    if cmd_uuid and cmd_uuid not in bots[connection.address]:
        raise RuntimeError("bot not found")

    bot = bots[connection.address][cmd_uuid]

    if cmd == "avance":
        bot.state = "avance"
    elif cmd == "recule":
        bot.state = "recule"
    elif cmd == "stop":
        bot.state = "stop"
    elif cmd == "tourne_droite":
        bot.state = "tourne_droite"
    elif cmd == "tourne_gauche":
        bot.state = "tourne_gauche"
    elif cmd == "distance":
        connection.send(bytes(str(bot.distance_forward), encoding="utf-8"))
    elif cmd == "suivi_ligne":
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
