import time
from robot import creerRobot, Robot

should_continue = True

def wallsDetection(robot: Robot):
    robot.avance()
    while should_continue:
        if robot.distance() < 10:
            robot.stop()
            print("stop")
            time.sleep(1)
            robot.tourne_droite()
            print("tourner a droite")
            time.sleep(.4)
            robot.stop()
            print("stop")
            time.sleep(1)
        else:
            robot.avance()
            print("avancer")

def remote(robot: Robot):
    while should_continue:
        action = input("Instruction?\n")
        if action == "avance":
            robot.avance()
        elif action == "stop":
            robot.stop()
        elif action == "tourne_droite":
            robot.tourne_droite()
        elif action == "tourne_gauche":
            robot.tourne_gauche()
        elif action == "recule":
            robot.recule()

def followLine(robot: Robot):
    robot.avance()
    lostLine = False
    onLine = False
    while should_continue:
        [colorCenter, colorRight, colorLeft] = robot.couleurs_sol()
        colorCenter = (colorCenter < 3000)
        colorRight = (colorRight < 3000)
        colorLeft = (colorLeft < 3000)
        match (colorLeft, colorCenter, colorRight):
            case (False, False, False):
                robot.avance()
                onLine = False
            case (False, False, True):
                lostLine = False
                robot.tourne_droite()
            case (False, True, False):
                lostLine = False
                robot.avance()
            case (False, True, True):
                lostLine = False
                robot.tourne_droite()
            case (True, False, False):
                lostLine = False
                robot.tourne_gauche()
            case (True, False, True):
                lostLine = False
                robot.tourne_droite()
            case (True, True, False):
                lostLine = False
                robot.tourne_gauche()
            case (True, True, True):
                lostLine = False
                robot.avance()

mode = input("quel mode?\n")
simulateur = creerRobot("simulateur")
match mode:
    case "walls":
        wallsDetection(simulateur)
    case "line":
        followLine(simulateur)
    case "remote":
        remote(simulateur)
