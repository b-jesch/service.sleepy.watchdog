import os
import re
import xbmc, xbmcgui, xbmcaddon

__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('id')
__path__ = __addon__.getAddonInfo('path')
__version__ = __addon__.getAddonInfo('version')
__LS__ = __addon__.getLocalizedString

__iconDefault__ = xbmc.translatePath(os.path.join(__path__, 'resources', 'media', 'pawprint.png'))

def notifyLog(message, level=xbmc.LOGNOTICE):
    xbmc.log('%s: %s' % (__addonname__, message.encode('utf-8')), level)

class SleepyWatchdog(object):

    def __init__(self):
        self.maxIdleTime = None
        self.action = None
        self.showPopup = None
        self.notificationTime = None
        self.PopUp = xbmcgui.DialogProgress()
        self.Player = xbmc.Player()

        self.getWDSettings()

    def getWDSettings(self):
        self.maxIdleTime = int(__addon__.getSetting('maxIdleTime'))
        self.action = __addon__.getSetting('action')
        self.notifyUser = True if __addon__.getSetting('showPopup').upper() == 'TRUE' else False
        self.notificationTime = int(re.match('\d+', __addon__.getSetting('notificationTime')).group())

    # user defined actions

    def stopVideoAudioTV(self):
        if self.Player.isPlaying():
            self.Player.stop()


    def start(self):
        while(not xbmc.abortRequested):

            # Check if GlobalIdle longer than maxIdle
            if xbmc.getGlobalIdleTime() > (self.maxIdleTime - int(self.notifyUser)*self.notificationTime):
                # Check if notification is allowed
                if self.notifyUser:
                    _bar = 0
                    self.PopUp.create(__LS__(32100), 'laufendes Video wird in %s Sekunden gestoppt.' % self.notificationTime)
                    self.Popup.update(_bar)
                # synchronize progressbar
                while _bar < self.notificationTime and not self.PopUp.iscanceled():
                    _bar += 1
                    _percent = int(_bar * 100 / self.notificationTime)
                    self.PopUp.update(_percent, 'laufendes Video wird in %s Sekunden gestoppt.' % (self.notificationTime - _bar))
                    xbmc.sleep(1000)

                # Popup schliessen
                self.PopUp.close()
                if not self.Popup.iscanceled():
                    pass
                    #
                    # ToDo: implement user defined actions here
                    #

            xbmc.sleep(60000)

# MAIN #
try:
    WatchDog = SleepyWatchdog()
    WatchDog.start()
except Exception, e:
    notifyLog('%s' %e, xbmc.LOGERROR)
del WatchDog