import os
import sys
import subprocess
import traceback
import re
import time
import xbmc, xbmcgui, xbmcaddon

__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('id')
__path__ = __addon__.getAddonInfo('path')
__version__ = __addon__.getAddonInfo('version')
__LS__ = __addon__.getLocalizedString

__iconDefault__ = xbmc.translatePath(os.path.join(__path__, 'resources', 'media', 'pawprint.png'))

LANGOFFSET = 32130

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
        self.PopUp = xbmcgui.DialogProgress()
        self.Player = xbmc.Player()
        self.execBuiltin = xbmc.executebuiltin

        XBMCMonitor.__init__(self)
        self.getWDSettings()


    def traceError(self, err, exc_tb):
        while exc_tb:
            tb = traceback.format_tb(exc_tb)
            self.notifyLog('%s' % err, xbmc.LOGERROR)
            self.notifyLog('in module: %s' % (sys.argv[0].strip() or '<not defined>'), xbmc.LOGERROR)
            self.notifyLog('at line:   %s' % traceback.tb_lineno(exc_tb), xbmc.LOGERROR)
            self.notifyLog('in file:   %s' % tb[0].split(",")[0].strip()[6:-1],xbmc.LOGERROR)
            exc_tb = exc_tb.tb_next

    def notifyLog(self, message, level=xbmc.LOGNOTICE):
        xbmc.log('[%s] %s' % (__addonname__, message.encode('utf-8')), level)

    def getWDSettings(self):
        self.maxIdleTime = int(re.match('\d+', __addon__.getSetting('maxIdleTime')).group())*60
        self.action = int(__addon__.getSetting('action')) + LANGOFFSET
        self.notifyUser = True if __addon__.getSetting('showPopup').upper() == 'TRUE' else False
        self.notificationTime = int(re.match('\d+', __addon__.getSetting('notificationTime')).group())
        self.testConfig = True if __addon__.getSetting('testConfig').upper() == 'TRUE' else False
        self.sendCEC = True if __addon__.getSetting('sendCEC').upper() == 'TRUE' else False
        self.jumpMainMenu = True if __addon__.getSetting('mainmenu').upper() == 'TRUE' else False
        self.keepAlive = True if __addon__.getSetting('keepalive').upper() == 'TRUE' else False
        self.addon_id = __addon__.getSetting('addon_id')
        self.SettingsChanged = False

        if self.testConfig:
            self.maxIdleTime = 60 + int(self.notifyUser)*self.notificationTime
            self.testIsRunning = True
        else:
            self.testIsRunning = False

    # user defined actions

    def stopVideoAudioTV(self):
        if self.Player.isPlaying():
            self.notifyLog('media is playing, stopping it')
            self.Player.stop()
            if self.jumpMainMenu:
                xbmc.sleep(500)
                self.notifyLog('jump to main menu')
                self.execBuiltin('ActivateWindow(home)')

    def quit(self):
        self.notifyLog('quit kodi')
        self.execBuiltin('Quit')

    def systemReboot(self):
        self.notifyLog('init system reboot')
        xbmc.restart()

    def systemShutdown(self):
        self.notifyLog('init system shutdown')
        xbmc.shutdown()

    def systemHibernate(self):
        self.notifyLog('init system hibernate')
        self.execBuiltin('Hibernate')

    def systemSuspend(self):
        self.notifyLog('init system suspend')
        self.execBuiltin('Suspend')

    def sendCecCommand(self):
        if not self.sendCEC: return
        self.notifyLog('send standby command via CEC')
        cec = subprocess.Popen('echo \"standby 0\" | cec-client -s', stdout=subprocess.PIPE, shell=True).communicate()
        for retstr in cec: self.notifyLog(str(retstr).strip())

    def runAddon(self):
        if xbmc.getCondVisibility('System.HasAddon(%s)' % (self.addon_id)):
            self.notifyLog('run addon \'%s\'' % (self.addon_id))
            self.execBuiltin('RunAddon(%s)' % (self.addon_id))
        else:
            self.notifyLog('could not run nonexistent addon \'%s\'' % (self.addon_id), level=xbmc.LOGERROR)

    def start(self):

        _currentIdleTime = 0
        _maxIdleTime = self.maxIdleTime
        _msgCnt = 0
        self.notifyLog('Sleepy Watchdog kicks in')
        try:
            while not xbmc.abortRequested or xbmc.Monitor.waitForAbort():
                self.actionCanceled = False
                if _currentIdleTime > xbmc.getGlobalIdleTime() + 60 or self.SettingsChanged:
                    self.notifyLog('user activity detected or settings changed, reset idle time')
                    self.getWDSettings()
                    _maxIdleTime = self.maxIdleTime
                if _currentIdleTime > xbmc.getGlobalIdleTime():
                    _msgCnt = 0

                if _msgCnt % 10 == 0 and _currentIdleTime > 60 and not self.testIsRunning: self.notifyLog('idle time %s' % (time.strftime('%H:%M:%S', time.gmtime(_currentIdleTime))))
                _currentIdleTime = xbmc.getGlobalIdleTime()
                _msgCnt += 1

                # Check if GlobalIdle longer than maxIdle
                if _currentIdleTime > (_maxIdleTime - int(self.notifyUser)*self.notificationTime):

                    self.notifyLog('max idle time reached, ready to perform some action')

                    # Reset test status
                    __addon__.setSetting('testConfig', 'false')

                    # Check if notification is allowed
                    if self.notifyUser:
                        _bar = 0
                        self.notifyLog('init notification countdown for action no. %s' % (self.action))
                        self.PopUp.create(__LS__(32100), __LS__(32115) % (__LS__(self.action), self.notificationTime))
                        self.PopUp.update(_bar)
                        # synchronize progressbar
                        while _bar < self.notificationTime:
                            _bar += 1
                            _percent = int(_bar * 100 / self.notificationTime)
                            self.PopUp.update(_percent, __LS__(32100), __LS__(32115) % (__LS__(self.action), self.notificationTime - _bar))
                            if self.PopUp.iscanceled():
                                self.actionCanceled = True
                                break
                            xbmc.sleep(1000)

                        self.PopUp.close()
                        xbmc.sleep(500)
                        #
                    if not self.actionCanceled:

                        self.actionPerformed = True

                        self.sendCecCommand()
                        {
                        32130: self.stopVideoAudioTV,
                        32131: self.systemReboot,
                        32132: self.systemShutdown,
                        32133: self.systemHibernate,
                        32134: self.systemSuspend,
                        32135: self.runAddon,
                        32136: self.quit
                        }.get(self.action)()
                        #
                        # ToDo: implement more user defined actions here
                        #       Action numbers are defined in settings.xml/strings.xml
                        #       also see LANGOFFSET
                        #
                        if self.testIsRunning:
                            self.notifyLog('watchdog was running in test mode and remains alive')
                        else:
                            if self.keepAlive:
                                self.notifyLog('keeping watchdog alive, update idletime for next cycle')
                                _maxIdleTime += self.maxIdleTime
                            else:
                                break
                    #

                _loop = 1
                while not xbmc.abortRequested or xbmc.Monitor.waitForAbort():
                    xbmc.sleep(1000)
                    _loop += 1
                    _currentIdleTime += 1

                    if self.SettingsChanged:
                        self.notifyLog('settings changed, update configuration')
                        self.getWDSettings()
                        break

                    if self.testIsRunning or _currentIdleTime > xbmc.getGlobalIdleTime() or _loop > 60: break

            self.notifyLog('Sleepy Watchdog kicks off')
        except Exception, e:
            self.traceError(e, sys.exc_traceback)

# MAIN #
WatchDog = SleepyWatchdog()
WatchDog.start()
del WatchDog

