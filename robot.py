import socket
import struct

# Internal code is written in english while exposed APIs are writter in french.
# This is purely intentional as this library is expected to be
# used by teenagers during some workshops.

class ClientSimulateur():
    # a wrapper to interact with ursina's networking library.
    # send/receive must be in sync with https://github.com/pokepetter/ursina/blob/master/ursina/networking.py
    def __init__(self, host: str, port: int):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            self.socket = s
        except:
            raise RuntimeError("Impossible de se connecter au simulateur. Veuillez vérifier qu'il soit bien en cours d'exécution.")

    def __del__(self):
        print("Closing socket:", self.socket)
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def sendmsg(self, msg: str):
        b = bytearray()
        b += struct.pack(">H", len(msg))
        b += bytes(msg, encoding='utf-8')
        self.socket.sendall(b)

    def receive(self):
        state = "l"
        expectedByteCount = 2
        bytes_received = bytearray()
        while True:
            data = self.socket.recv(expectedByteCount)

            if data is None:
                break
            if len(data) == 0:
                break

            bytes_received += data
            expectedByteCount -= len(data)

            if expectedByteCount == 0:
                if state == "l":
                    l = struct.unpack(">H", bytes_received)[0]
                    state = "c"
                    expectedByteCount = l
                    bytes_received.clear()
                elif state == "c":
                    d = bytes(bytes_received.copy())
                    state = "l"
                    expectedByteCount = 2
                    bytes_received.clear()
                    return d

class CapteurDeLigne():
    def __init__(self):
        pass

    def couleurs(self) -> list:
        pass

class VraiCapteurDeLigne(CapteurDeLigne):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot

    def couleurs(self) -> list:
        return (
            self.robot.getRawLFValue("l"),
            self.robot.getRawLFValue("c"),
            self.robot.getRawLFValue("r"),
        )

class CapteurDistance():
    def __init__(self):
        pass

    def distance() -> float:
        pass

class VraiCapteurDistance(CapteurDistance):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot

    def distance() -> float:
        return self.robot.getDistance("f")

class Moteur():
    def __init__(self):
        pass

    def avance(self):
        pass

    def stop(self):
        pass

    def recule(self):
        pass

class VraiMoteur(Moteur):
    def __init__(self, robot, position):
        super().__init__()
        self.position = position
        self.robot = robot
        self.vitesse = 20

    def avance(self):
        self.robot.motorOn(self.position, "f", self.vitesse, True)

    def stop(self):
        self.robot.motorOff(self.position)

    def recule(self):
        self.robot.motorOn(self.position, "r", self.vitesse, True)

class Robot():
    def __init__(self):
        pass

    def avance(self):
        pass

    def recule(self):
        pass

    def tourne_droite(self):
        pass

    def tourne_gauche(self):
        pass

    def stop(self):
        pass

    def distance_avant(self) -> float:
        pass

    def couleurs_sol(self) -> list:
        pass

class SimulationRobot(Robot):
    def __init__(self, clientSimulation):
        super().__init__()
        self.clientSimulation = clientSimulation

    def avance(self):
        self.clientSimulation.sendmsg("avance")

    def recule(self):
        self.clientSimulation.sendmsg("recule")

    def tourne_droite(self):
        self.clientSimulation.sendmsg("tourne_droite")

    def tourne_gauche(self):
        self.clientSimulation.sendmsg("tourne_gauche")

    def stop(self):
        self.clientSimulation.sendmsg("stop")

    def distance_avant(self) -> float:
        self.clientSimulation.sendmsg("distance")
        return float(self.clientSimulation.receive())

    def couleurs_sol(self) -> list:
        self.clientSimulation.sendmsg("suivi_ligne")
        received = self.clientSimulation.receive().decode("utf-8")
        return list(map(int, str(received).split(";")))

class VraiRobot(Robot):
    def __init__(self, capteurDeLigne: CapteurDeLigne, capteurDistanceAvant: CapteurDistance, moteurDroit: Moteur, moteurGauche: Moteur):
        super().__init__()
        self.capteurDeLigne = capteurDeLigne
        self.capteurDistanceAvant = capteurDistanceAvant
        self.moteurDroit = moteurDroit
        self.moteurGauche = moteurGauche

    def avance(self):
        self.moteurDroit.avance()
        self.moteurGauche.avance()

    def recule(self):
        self.moteurDroit.recule()
        self.moteurGauche.recule()

    def tourne_droite(self):
        self.moteurDroit.recule()
        self.moteurGauche.avance()

    def tourne_gauche(self):
        self.moteurDroit.avance()
        self.moteurGauche.recule()

    def stop(self):
        self.moteurDroit.stop()
        self.moteurGauche.stop()

    def distance_avant(self) -> float:
        return self.capteurDistanceAvant.distance()

    def couleurs_sol(self) -> list:
        return self.capteurDeLigne.couleurs()

def creerRobot(typeRobot: str) -> Robot:
    if typeRobot == "simulateur":
        client = ClientSimulateur("localhost", 12345)
        return SimulationRobot(client)
    else:
        import PicoAutonomousRobotics
        robot = PicoAutonomousRobotics.KitronikPicoRobotBuggy()
        cl = VraiCapteurDeLigne(robot)
        cd = VraiCapteurDistance(robot)
        mg = VraiMoteur(robot, "l")
        md = VraiMoteur(robot, "r")

        return VraiRobot(cl, cd, md, mg)
