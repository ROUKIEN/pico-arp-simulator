from ursina import Entity, held_keys, time, color, raycast, Text
from PIL import Image
from math import cos, sin, pi, floor

class Robot(Entity):
    def __init__(self, **kwargs):
        super().__init__(model='assets/pico_arp.gltf', scale=.4, y=2, collider='box')
        self.angle = 0
        self.speed = 10
        self.speedRotation = 4
        self.state = "stop"

        self.lineDetectorCenter = Entity(name='center', model='cube', scale=.1, parent=self, z=3.72, y=-.6, color=color.white, visible=False)
        self.lineDetectorLeft = Entity(name='left', model='cube', scale=.1, parent=self, z=2.98, y=-.6, x=-.71, color=color.white, visible=False)
        self.lineDetectorRight = Entity(name='right', model='cube', scale=.1, parent=self, z=2.98, y=-.6, x=.71, color=color.white, visible=False)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        self.angle -= held_keys['a'] * self.speedRotation + int(self.state == "tourne_gauche") * self.speedRotation
        self.angle += held_keys['d'] * self.speedRotation + int(self.state == "tourne_droite") * self.speedRotation

        self.angle = self.angle % 360
        angleRad = self.angle / 180 * pi

        direction = 0
        if held_keys['w'] or self.state == "avance":
            direction = 1
        elif held_keys['s'] or self.state == "recule":
            direction = -1

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
    def __init__(self, robot: Robot, walls, uiText: Text, isDebug: bool):
        super().__init__()
        self.robot = robot
        self.walls = walls
        self.uiText = uiText
        self.isDebug = isDebug

    def update(self):
        # ultrasonic checks
        ultrasonicSensor = raycast(self.robot.world_position, self.robot.forward, ignore=(self.robot,), distance=100, debug=self.isDebug)
        if ultrasonicSensor.hit:
            self.robot.distance_forward = round(ultrasonicSensor.distance, 3)
            self.uiText.text = f"distance avant: {self.robot.distance_forward}"

class LineDetectorHandler(Entity):
    def __init__(self, floor: Entity, robot: Robot, floorTexture: Image, scaleFactor: int, isDebug: bool):
        super().__init__()
        self.robot = robot
        self.floor = floor
        self.floorTexture = floorTexture
        self.scaleFactor = scaleFactor
        self.isDebug = isDebug

    def update(self):
        # line detection
        for lineDetector in self.robot.getLineDetectorSensors():
            castColor = color.white
            if lineDetector.color[3] != 0:
                castColor = lineDetector.color
            lineDetect = raycast(lineDetector.world_position, self.robot.down, ignore=(self.robot,), distance=2, debug=self.isDebug, color=castColor)

            # assign white value. white = 0, black = 65536
            self.assignColor(lineDetector, (1,1,1,1))
            if lineDetect.hit:
                imgX = self.floor.scale_x/2 + lineDetect.world_point.x
                imgY = self.floor.scale_y/2 + lineDetect.world_point.z

                imgX = int(imgX * self.scaleFactor)
                imgY = int(imgY * self.scaleFactor)

                pixel = self.floor.texture.get_pixel(imgX, imgY)
                if pixel:
                    self.assignColor(lineDetector, pixel)
                    lineDetector.color = pixel
                    lineDetector.visible = True
                else:
                    lineDetector.visible = False

    def assignColor(self, lineDetector, pixel):
        max = 65536
        grayscale = floor((.299*pixel[0]+.587*pixel[1]+.114*pixel[2])*65536)
        grayscale = max-grayscale
        match lineDetector.name:
            case "left":
                self.robot.ls_left = grayscale
            case "center":
                self.robot.ls_center = grayscale
            case "right":
                self.robot.ls_right = grayscale

class CollisionHandler(Entity):
    def __init__(self, robot: Robot, walls, camera, isDebug: bool):
        super().__init__()
        self.robot = robot
        self.walls = walls
        self.camera = camera
        self.isDebug = isDebug

        self.cameraOffset =30

        self.prevX = 0
        self.prevZ = 0

    def update(self):
        if self.intersectsWithWall():
            self.robot.x = self.prevX
            self.robot.z = self.prevZ
        else:
            self.prevX = self.robot.x
            self.prevZ = self.robot.z

        if not self.isDebug:
            self.camera.position = (self.robot.position.x - self.cameraOffset, self.robot.position.y + self.cameraOffset, self.robot.position.z - self.cameraOffset)
            self.camera.look_at(self.robot.world_position)

    def intersectsWithWall(self) -> bool:
        for wall in self.walls:
            intersection = wall.intersects(self.robot)
            if intersection.hit:
                return True
        return False