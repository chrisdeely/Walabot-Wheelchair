"""
Forked from https://github.com/Walabot-Projects/Walabot-SensorTargets
"""
from time import sleep
import sys
import os
import logging
import WalabotAPI
import json
from socketIO_client import SocketIO, LoggingNamespace

socketIO = SocketIO('localhost', 3000, LoggingNamespace)
socketIO.wait(seconds=1)

WARNING_DIST = 100
ALERT_DIST = 60

logger = logging.getLogger('WW')

class WalabotWheelchair():
    """ Main app class.
    """

    def __init__(self):
        """ Init the Walabot API.
        """
        self.wlbt = Walabot()

    def initAppLoop(self):
        """ Connect to the Walabot device, set it's arena parameters according
            to the config, calibrate if needed and start calls
            the loop function.
        """
        if self.wlbt.isConnected():  # connection achieved
            logger.debug("Status: " + self.wlbt.getStatusString())
            try:
                self.wlbt.setParameters(*getParameters())
            except WalabotAPI.WalabotError as err:
                logger.error(str(err))
                return
            self.numOfTargetsToDisplay = 1
            self.wlbt.calibrate()
            logger.debug("Status: " + self.wlbt.getStatusString())
            self.shouldLoop = True
            self.loop()
        else:
            logger.debug("No Walabot device detected - quiting")

    def loop(self):
        """ Triggers the Walabot, get the Sensor targets
        """
        while self.shouldLoop:
            try:
                targets = self.wlbt.getTargets()
                logger.debug((int(self.wlbt.getFps())))
            except WalabotAPI.WalabotError as err:
                logger.error(str(err))
                self.stopLoop()
                return
            targets = targets[:self.numOfTargetsToDisplay]
            if len(targets) > 0 and targets[0].zPosCm < WARNING_DIST:
                logger.debug(targets[0])
                socketIO.emit('targetData', json.dumps(targets[0].__dict__))
            else:
                logger.debug("No active targets")
                socketIO.emit('noTarget')

    def stopLoop(self):
        """ Kills the loop function and reset the relevant app components.
        """
        self.shouldLoop = False
        self.wlbt.stopAndDisconnect()
        socketIO.disconnect()

def getParameters():
    """ Return the values of all the parameters
    TODO: replace with config
    """
    warn = WARNING_DIST
    alert = ALERT_DIST
    rMin = 1.0
    rMax = 150.0
    rRes = 5.0
    tMax = 45.0
    tRes = 10.0
    pMax = 45.0
    pRes = 10.0
    thld = 15.0
    mtiParam = 0
    rParams = (rMin, rMax, rRes)
    tParams = (-tMax, tMax, tRes)
    pParams = (-pMax, pMax, pRes)
    thldParam = thld
    return rParams, tParams, pParams, thldParam, mtiParam

class Walabot:
    """ Control the Walabot using the Walabot API.
    """

    def __init__(self):
        """ Init the Walabot API.
        """
        self.wlbt = WalabotAPI
        self.wlbt.Init()
        self.wlbt.SetSettingsFolder()

    def isConnected(self):
        """ Try to connect the Walabot device. Return True/False accordingly.
        """
        try:
            self.wlbt.ConnectAny()
        except self.wlbt.WalabotError as err:
            if err.code == 19:  # "WALABOT_INSTRUMENT_NOT_FOUND"
                return False
            else:
                raise err
        return True

    def getParameters(self):
        """ Get the arena parameters from the Walabot API.
        """
        r = self.wlbt.GetArenaR()
        theta = self.wlbt.GetArenaTheta()
        phi = self.wlbt.GetArenaPhi()
        threshold = self.wlbt.GetThreshold()
        mti = self.wlbt.GetDynamicImageFilter()
        return r, theta, phi, threshold, mti

    def setParameters(self, r, theta, phi, threshold, mti):
        """ Set the arena Parameters according given ones.
        """
        self.wlbt.SetProfile(self.wlbt.PROF_SENSOR_NARROW)
        self.wlbt.SetArenaR(*r)
        self.wlbt.SetArenaTheta(*theta)
        self.wlbt.SetArenaPhi(*phi)
        self.wlbt.SetThreshold(threshold)
        self.wlbt.SetDynamicImageFilter(mti)
        self.wlbt.Start()

    def calibrate(self):
        """ Calibrate the Walabot.
        """
        self.wlbt.StartCalibration()
        while self.wlbt.GetStatus()[0] == self.wlbt.STATUS_CALIBRATING:
            self.wlbt.Trigger()

    def getStatusString(self):
        """ Return the Walabot status as a string.
        """
        status = self.wlbt.GetStatus()[0]
        if status == 0:
            return "STATUS_DISCONNECTED"
        elif status == 1:
            return "STATUS_CONNECTED"
        elif status == 2:
            return "STATUS_IDLE"
        elif status == 3:
            return "STATUS_SCANNING"
        elif status == 4:
            return "STATUS_CALIBRATING"

    def getTargets(self):
        """ Trigger the Walabot, retrive the targets according to the desired
            tracker given.
        """
        self.wlbt.Trigger()
        return self.wlbt.GetSensorTargets()

    def getFps(self):
        """ Return the Walabot FPS (internally, from the API).
        """
        return self.wlbt.GetAdvancedParameter("FrameRate")

    def stopAndDisconnect(self):
        """ Stop and disconnect from the Walabot.
        """
        self.wlbt.Stop()
        self.wlbt.Disconnect()

def initLogger():
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('ww.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info("Application start")

if __name__ == "__main__":
    initLogger()
    main = WalabotWheelchair()
    try:
        main.initAppLoop()
    except KeyboardInterrupt:
        print 'Interrupted'
        try:
            main.stopLoop()
            sys.exit(0)
        except SystemExit:
            os._exit(0)
