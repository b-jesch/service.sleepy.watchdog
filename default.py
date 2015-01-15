import os
import sys
import traceback
import re
import xbmc, xbmcgui, xbmcaddon

__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('id')
__path__ = __addon__.getAddonInfo('path')
__version__ = __addon__.getAddonInfo('version')
__LS__ = __addon__.getLocalizedString

__iconDefault__ = xbmc.translatePath(os.path.join(__path__, 'resources', 'media', 'pawprint.png'))


def traceError(err, exc_tb):
    while exc_tb:
        tb = traceback.format_tb(exc_tb)
        notifyLog('%s' % err, xbmc.LOGERROR)
        notifyLog('in module: %s' % (sys.argv[0].strip() or '<not defined>'), xbmc.LOGERROR)
        notifyLog('at line:   %s' % traceback.tb_lineno(exc_tb), xbmc.LOGERROR)
        notifyLog('in file:   %s' % tb[0].split(",")[0].strip()[6:-1],xbmc.LOGERROR)
        exc_tb = exc_tb.tb_next

def notifyLog(message, level=xbmc.LOGNOTICE):
    xbmc.log('%s: %s' % (__addonname__, message.encode('utf-8')), level)

class XBMCMonitor(xbmc.Monitor):

    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        self.SettingsChanged = False

    def onSettingsChanged(self):
        self.SettingsChanged = True

    def onScreensaverActivated(self):
        self.ScreensaverActive = True

    def onScreensaverDeactivated(self):
        self.ScreensaverActive = False

class SleepyWatchdog(XBMCMonitor):

    def __init__(self):
        self.maxIdleTime = None
        self.action = None
        self.actionPerformed = False
        self.actionCanceled = False
        self.showPopup = None
        self.notificationTime = None
        self.PopUp = xbmcgui.DialogProgressBG()
        self.Player = xbmc.Player()
        self.execBuiltin = xbmc.executebuiltin

        XBMCMonitor.__init__(self)
        self.getWDSettings()

    def getWDSettings(self):
        self.maxIdleTime = int(re.match('\d+', __addon__.getSetting('maxIdleTime')).group())*60
        #
        # ONLY TESTING PURPOSES !
        # self.maxIdleTime = 1
        #
        self.action = int(__addon__.getSetting('action'))
        self.notifyUser = True if __addon__.getSetting('showPopup').upper() == 'TRUE' else False
        self.notificationTime = int(re.match('\d+', __addon__.getSetting('notificationTime')).group())
        self.testConfig = True if __addon__.getSetting('testConfig').upper() == 'TRUE' else False

        if self.testConfig: self.maxIdleTime = 60 + int(self.notifyUser)*self.notificationTime

    # user defined actions

    def stopVideoAudioTV(self):
        notifyLog('stop playing media')
        if self.Player.isPlaying():
            self.Player.stop()

    def systemReboot(self):
        notifyLog('init system reboot')
        xbmc.restart()

    def systemShutdown(self):
        notifyLog('init system shutdown')
        xbmc.shutdown()

    def systemHibernate(self):
        notifyLog('init system hibernate')
        self.execBuiltin('Hibernate')

    def systemSuspend(self):
        notifyLog('init system suspend')
        self.execBuiltin('Suspend')

    def start(self):

        _currentIdleTime = 0
        while not xbmc.abortRequested:
            self.actionCanceled = False
            if _currentIdleTime > xbmc.getGlobalIdleTime():
                notifyLog('user activity detected, reset idle time')
            _currentIdleTime = xbmc.getGlobalIdleTime()
            notifyLog('calculated idle time: %s secs' % _currentIdleTime)

            # Check if GlobalIdle longer than maxIdle
            if _currentIdleTime > (self.maxIdleTime - int(self.notifyUser)*self.notificationTime):

                notifyLog('max idle time reached, ready to perform some action')

                # Reset test status (This works not properly!)
                __addon__.setSetting('testConfig', 'false')

                # Check if notification is allowed
                if self.notifyUser:
                    _bar = 0
                    notifyLog('init notification shutdown')
                    self.PopUp.create(__LS__(32100), __LS__(32115) % (__LS__(32130 + self.action), self.notificationTime))
                    self.PopUp.update(_bar)
                    # synchronize progressbar
                    while _bar < self.notificationTime:
                        _bar += 1
                        _percent = int(_bar * 100 / self.notificationTime)
                        self.PopUp.update(_percent, __LS__(32100), __LS__(32115) % (__LS__(32130 + self.action), self.notificationTime - _bar))
                        if _currentIdleTime > xbmc.getGlobalIdleTime():
                            self.actionCanceled = True
                            # self.PopUp.close()
                            notifyLog('user activity detected, pending action canceled')
                            break
                        xbmc.sleep(1000)

                    # if self.PopUp.isFinished():
                    self.PopUp.close()

                    if not self.actionCanceled:

                        self.actionPerformed = True
                        {
                        0: self.stopVideoAudioTV,
                        1: self.systemReboot,
                        2: self.systemShutdown,
                        3: self.systemHibernate,
                        4: self.systemSuspend
                        }.get(self.action)()
                        #
                        # ToDo: implement more user defined actions here
                        #
                        break
                    #
            xbmc.sleep(10000)
            if self.SettingsChanged:
                notifyLog('settings changed, update configuration')
                self.getWDSettings()
                self.SettingsChanged = False
            #
        notifyLog('action performed, execution finished')

# MAIN #
WatchDog = SleepyWatchdog()
try:
    notifyLog('Sleepy Watchdog kicks in')
    WatchDog.start()
except Exception, e:
    traceError(e, sys.exc_traceback)
del WatchDog