from ursina import Entity, held_keys, time, color, raycast, Text
from PIL import Image
from math import cos, sin, pi, floor

class Robot(Entity):
    def __init__(self, **kwargs):
        super().__init__(model='assets/pico_arp_chassis.gltf', scale=.4, y=2, collider='box')
        self.angle = 0
        self.speed = 10
        self.speedRotation = 4
        self.state = "stop"
        self.distance_forward = 1000
        self.ls_left = 0
        self.ls_center = 0
        self.ls_right = 0

        self.rightWheel = Entity(name='rightWheel', parent=self, model="assets/pico_arp_wheel.gltf", x=3.4, z=1.3, y=2*.4)
        self.leftWheel = Entity(name='leftWheel', parent=self, model="assets/pico_arp_wheel.gltf", x=-3.4, z=1.3, y=2*.4, rotation_y=180)

        self.lineDetectorCenter = Entity(name='center', model='cube', scale=.1, parent=self, z=3.72, y=-.6, color=color.white, visible=False)
        self.lineDetectorLeft = Entity(name='left', model='cube', scale=.1, parent=self, z=2.98, y=-.6, x=-.71, color=color.white, visible=False)
        self.lineDetectorRight = Entity(name='right', model='cube', scale=.1, parent=self, z=2.98, y=-.6, x=.71, color=color.white, visible=False)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        isTurningLeft = self.state == "tourne_gauche"
        isTurningRight = self.state == "tourne_droite"

        self.angle -= int(self.state == "tourne_gauche") * self.speedRotation
        self.angle += int(self.state == "tourne_droite") * self.speedRotation

        self.angle = self.angle % 360
        angleRad = self.angle / 180 * pi

        direction = 0

        if self.state == "avance":
            direction = 1
        elif self.state == "recule":
            direction = -1

        wheelDiameter = 6.48
        wheelMultiplier = 3000
        divider = 5

        wheelCircumference = wheelDiameter * pi
        rot = self.speed * (wheelMultiplier/divider) / wheelCircumference

        if isTurningLeft:
            rot = self.speedRotation * wheelMultiplier / wheelCircumference
            self.leftWheel.rotation_x += rot * 1 * time.dt
            self.rightWheel.rotation_x -= -rot * 1 * time.dt
        elif isTurningRight:
            rot = self.speedRotation * wheelMultiplier / wheelCircumference
            self.leftWheel.rotation_x += rot * -1 * time.dt
            self.rightWheel.rotation_x -= rot * 1 * time.dt
        else:
            self.leftWheel.rotation_x += rot * -direction * time.dt
            self.rightWheel.rotation_x -= rot * -direction * time.dt

        self.z += cos(angleRad) * (self.speed*direction) * time.dt
        self.x += sin(angleRad) * (self.speed*direction) * time.dt
        self.rotation_y = self.angle

    def getLineDetectorSensors(self):
        return [
            self.lineDetectorCenter,
            self.lineDetectorLeft,
            self.lineDetectorRight,
        ]

class DistanceSensorHandler(Entity):
    def __init__(self, robots: list[str, Robot], walls, isDebug: bool):
        super().__init__()
        self.robots = robots
        self.walls = walls
        self.isDebug = isDebug

    def addRobot(self, robot: Robot):
        self.robots[robot.uuid] = robot

    def remove(self, robot: Robot):
        self.robots.pop(robot.uuid, True)

    def update(self):
        # ultrasonic checks
        for uuid, robot in self.robots.items():
            ultrasonicSensor = raycast(robot.world_position, robot.forward, ignore=self.robots.values(), distance=100, debug=self.isDebug)
            if ultrasonicSensor.hit:
                robot.distance_forward = round(ultrasonicSensor.distance, 3)

class LineDetectorHandler(Entity):
    def __init__(self, floor: Entity, robots: list[str, Robot], floorTexture: Image, scaleFactor: int, isDebug: bool):
        super().__init__()
        self.robots = robots
        self.floor = floor
        self.floorTexture = floorTexture
        self.scaleFactor = scaleFactor
        self.isDebug = isDebug

    def addRobot(self, robot: Robot):
        self.robots[robot.uuid] = robot

    def remove(self, robot: Robot):
        self.robots.pop(robot.uuid, True)

    def update(self):
        for uuid, robot in self.robots.items():
            # line detection
            for lineDetector in robot.getLineDetectorSensors():
                castColor = color.white
                if lineDetector.color[3] != 0:
                    castColor = lineDetector.color
                lineDetect = raycast(lineDetector.world_position, robot.down, ignore=(robot,), distance=2, debug=self.isDebug, color=castColor)

                # assign white value. white = 0, black = 65536
                self.assignColor(lineDetector, (1,1,1,1), robot)
                if lineDetect.hit:
                    imgX = self.floor.scale_x/2 + lineDetect.world_point.x
                    imgY = self.floor.scale_y/2 + lineDetect.world_point.z

                    imgX = int(imgX * self.scaleFactor)
                    imgY = int(imgY * self.scaleFactor)

                    pixel = self.floor.texture.get_pixel(imgX, imgY)
                    if pixel:
                        self.assignColor(lineDetector, pixel, robot)
                        lineDetector.color = pixel
                        lineDetector.visible = True
                    else:
                        lineDetector.visible = False

    def assignColor(self, lineDetector, pixel, robot: Robot):
        max = 65536
        grayscale = floor((.299*pixel[0]+.587*pixel[1]+.114*pixel[2])*65536)
        grayscale = max-grayscale
        match lineDetector.name:
            case "left":
                robot.ls_left = grayscale
            case "center":
                robot.ls_center = grayscale
            case "right":
                robot.ls_right = grayscale

class CollisionHandler(Entity):
    def __init__(self, robots: dict[str, Robot], walls):
        super().__init__()
        self.robots = robots
        self.prevPos = {}
        self.walls = walls

    def addRobot(self, robot: Robot):
        self.robots[robot.uuid] = robot
        self.prevPos[robot.uuid] = (0, 0)

    def remove(self, robot: Robot):
        self.robots.pop(robot.uuid)
        self.prevPos.pop(robot.uuid)

    def update(self):
        for uuid, robot in self.robots.items():
            if self.intersectsWithWall(robot):
                x, z = self.prevPos[uuid]
                robot.x = x
                robot.z = z
            else:
                self.prevPos[uuid] = (robot.x, robot.z)

    def intersectsWithWall(self, robot) -> bool:
        for wall in self.walls:
            intersection = wall.intersects(robot)
            if intersection.hit:
                return True
        return False
