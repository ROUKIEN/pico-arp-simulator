from ursina import *

# create a window
app = Ursina()

player = Entity(model='assets/pico_arp.gltf', scale=.4, y=2, collider='box')
plane = Entity(model='quad', z=.1, texture='assets/ligne_a_suivre.png', rotation_x=90, scale=(40, 40))

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

cameraOffset = 30
speed = 30
speedRotation = 4
robotAngle = 0

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
    robotAngle = robotAngle%360
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

    camera.position = (player.position.x - cameraOffset, player.position.y + cameraOffset, player.position.z -cameraOffset)
    camera.look_at(player.world_position)

    #print(player.forward)
    raycastPosition = (
        player.world_position.x,
        player.world_position.y,
        player.world_position.z,
    )
    hit_info = raycast(raycastPosition, player.forward, ignore=(player,), distance=100, debug=True)
    if hit_info.hit:
        distanceForward = round(hit_info.distance, 3)
        distanceForwardText.text = str(f"distance avant: {distanceForward}")

def input(key):
    if key == 'space':
        player.y += 1
        invoke(setattr, player, 'y', player.y-1, delay=.25)

# start running the game
app.run()
