import os
import re
import datetime
import xbmc
import xbmcgui
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDONNAME = ADDON.getAddonInfo('id')
ADDONPATH = xbmc.translatePath(ADDON.getAddonInfo('path'))
LOC = ADDON.getLocalizedString

ICON_DEFAULT = os.path.join(ADDONPATH, 'resources', 'media', 'pawprint.png')
ICON_ERROR = os.path.join(ADDONPATH, 'resources', 'media', 'pawprint_red.png')

LANGOFFSET = 32130

STRING = 0
BOOL = 1
NUM = 2


def notifyLog(message, level=xbmc.LOGDEBUG):
    xbmc.log('[%s] %s' % (ADDONNAME, message), level)


def notifyUser(message, icon=ICON_DEFAULT, time=3000):
    xbmcgui.Dialog().notification(LOC(32100), message, icon, time)


class XBMCMonitor(xbmc.Monitor):

    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        self.SettingsChanged = False

    def onSettingsChanged(self):
        self.SettingsChanged = True


    @classmethod
    def onNotification(cls, sender, method, data):
        notifyLog('Notification triggered')
        notifyLog('sender: %s' % (sender))
        notifyLog('method: %s' % (method))
        notifyLog('data:   %s' % (data))

class SleepyWatchdog(XBMCMonitor):

    def __init__(self):

        self.currframe = 0
        self.actionCanceled = False

        XBMCMonitor.__init__(self)
        self.getWDSettings()


    def __strToBool(self, par):
        return True if par.upper() == 'TRUE' else False


    def getAddonSetting(self, setting, sType=STRING, multiplicator=1):
        if sType == BOOL:
            return self.__strToBool(ADDON.getSetting(setting))
        elif sType == NUM:
            try:
                return int(re.findall('([0-9]+)', ADDON.getSetting(setting))[0]) * multiplicator
            except (IndexError, TypeError, AttributeError) as e:
                notifyLog('Could not get setting type NUM for %s, return with 0' % (setting), xbmc.LOGERROR)
                notifyLog(str(e), xbmc.LOGERROR)
                return 0
        else:
            return ADDON.getSetting(setting)


    def getWDSettings(self):

        self.mode = self.getAddonSetting('mode')
        self.silent = self.getAddonSetting('silent', BOOL)
        self.notificationType = self.getAddonSetting('notificationType', NUM)   # 0:intermitted, 1:progressbar
        self.notificationTime = self.getAddonSetting('notificationTime', NUM)
        self.sendCEC = self.getAddonSetting('sendCEC', BOOL)
        self.timeframe = bool(self.getAddonSetting('timeframe', NUM))
        self.act_start = int(datetime.timedelta(hours=self.getAddonSetting('start', NUM)).total_seconds())
        self.act_stop = int(datetime.timedelta(hours=self.getAddonSetting('stop', NUM)).total_seconds())
        self.maxIdleTime = self.getAddonSetting('maxIdleTime', NUM, 60)
        self.userIdleTime = self.getAddonSetting('userIdleTime', NUM)
        self.action = self.getAddonSetting('action', NUM) + LANGOFFSET
        self.jumpMainMenu = self.getAddonSetting('mainmenu', BOOL)
        self.keepAlive = self.getAddonSetting('keepalive', BOOL)
        self.addon_id = self.getAddonSetting('addon_id')
        self.profile_id = self.getAddonSetting('profile_id')
        self.testConfig = self.getAddonSetting('testConfig', BOOL)

        if self.timeframe:
            _activity_time = self.act_stop - self.act_start
            if _activity_time < 0: _activity_time += 86400
            notifyLog('active timeframe: %s secs' % (_activity_time))

            if self.action == 32131:
                if _activity_time > self.maxIdleTime: xbmcgui.Dialog().ok(LOC(32100), LOC(32117) % LOC(32131))
            else:
                if _activity_time < self.maxIdleTime: xbmcgui.Dialog().ok(LOC(32100), LOC(32116))

        self.SettingsChanged = False

        notifyLog('settings (re)loaded...')
        notifyLog('current mode:             %s' % (self.mode))
        notifyLog('silent mode:              %s' % (self.silent))
        notifyLog('message type:             %s' % (self.notificationType))
        notifyLog('Duration of notification: %s' % (self.notificationTime))
        notifyLog('send CEC:                 %s' % (self.sendCEC))
        notifyLog('Time frame:               %s' % (self.timeframe))
        notifyLog('Activity start:           %s' % (self.act_start))
        notifyLog('Activity stop:            %s' % (self.act_stop))
        notifyLog('max. idle time:           %s' % (self.maxIdleTime))
        notifyLog('Idle time set by user:    %s' % (self.userIdleTime))
        notifyLog('Action:                   %s' % (self.action))
        notifyLog('Jump to main menu:        %s' % (self.jumpMainMenu))
        notifyLog('Keep alive:               %s' % (self.keepAlive))
        notifyLog('Run addon:                %s' % (self.addon_id))
        notifyLog('Load profile:             %s' % (self.profile_id))
        notifyLog('Test configuration:       %s' % (self.testConfig))

        if self.testConfig:
            self.maxIdleTime = 60 + int(not self.silent) * self.notificationTime
            notifyLog('running in test mode for %s secs' % (self.maxIdleTime))

    # user defined actions

    def stopVideoAudioTV(self):
        if xbmc.Player().isPlaying():
            notifyLog('media is playing, stopping it')
            xbmc.Player().stop()
            if self.jumpMainMenu:
                xbmc.sleep(500)
                notifyLog('jump to main menu')
                xbmc.executebuiltin('ActivateWindow(home)')

    @classmethod
    def quit(cls):
        notifyLog('quit kodi')
        xbmc.executebuiltin('Quit')

    @classmethod
    def systemReboot(cls):
        notifyLog('init system reboot')
        xbmc.restart()

    @classmethod
    def systemShutdown(cls):
        notifyLog('init system shutdown')
        xbmc.shutdown()

    @classmethod
    def systemHibernate(cls):
        notifyLog('init system hibernate')
        xbmc.executebuiltin('Hibernate')

    @classmethod
    def systemSuspend(cls):
        notifyLog('init system suspend')
        xbmc.executebuiltin('Suspend')

    def sendCecCommand(self):
        if not self.sendCEC: return
        notifyLog('send standby command via CEC')
        xbmc.executebuiltin('CECStandby')

    def runAddon(self):
        if xbmc.getCondVisibility('System.HasAddon(%s)' % (self.addon_id.split(',')[0])):
            notifyLog('run addon \'%s\'' % (self.addon_id))
            xbmc.executebuiltin('RunAddon(%s)' % (self.addon_id))
        else:
            notifyLog('could not run nonexistent addon \'%s\'' % (self.addon_id.split(',')[0]), level=xbmc.LOGERROR)

    def switchProfile(self):
        notifyLog('switch profile \'%s\'' % (self.profile_id))
        xbmc.executebuiltin('LoadProfile(%s,prompt)' % (self.profile_id))

    def start(self):

        _currentIdleTime = -1
        _wd_status = False
        _maxIdleTime = self.maxIdleTime

        while not xbmc.Monitor.abortRequested(self):
            self.actionCanceled = False

            _status = False
            if not self.timeframe or self.mode == 'USER':
                _status = True
            else:
                _currframe = (datetime.datetime.now() - datetime.datetime.now().replace(hour=0, minute=0, second=0,
                                                                                        microsecond=0)).seconds
                if self.act_start < self.act_stop:
                    if self.act_start <= _currframe < self.act_stop: _status = True
                else:
                    if self.act_start <= _currframe < 86400 or 0 <= _currframe < self.act_stop: _status = True

            if _wd_status ^ _status:
                notifyLog('Watchdog status changed: %s' % ('active' if _status else 'inactive'))
                _wd_status = _status

            if _wd_status and _currentIdleTime > 60 and not self.testConfig:
                notifyLog('idle time: %s' % (str(datetime.timedelta(seconds=_currentIdleTime))))

            if _currentIdleTime > xbmc.getGlobalIdleTime():
                notifyLog('user activity detected, reset idle time')
                _maxIdleTime = self.maxIdleTime if self.mode == 'SERVICE' else self.userIdleTime
                _currentIdleTime = 0

            # Check if GlobalIdle longer than maxIdle and we're in a time frame

            if _wd_status or self.testConfig:
                if _currentIdleTime > (_maxIdleTime - int(not self.silent) * self.notificationTime):

                    notifyLog('max idle time reached, ready to perform some action')

                    # Check silent mode
                    if not self.silent:
                        count = 0
                        notifyLog('init notification countdown for action no. %s' % (self.action))
                        if self.notificationType == 0:
                            while self.notificationTime - count > 0:
                                if self.action > 32130:
                                    notifyUser(LOC(32115) % (LOC(self.action), self.notificationTime - count), time=5000)
                                if xbmc.Monitor.waitForAbort(self, 10): break
                                count += 10
                                if _currentIdleTime > xbmc.getGlobalIdleTime():
                                    self.actionCanceled = True
                                    break
                        else:
                            progress = xbmcgui.DialogProgress()
                            progress.create(LOC(32100), LOC(32115) % (LOC(self.action), self.notificationTime - count))
                            while self.notificationTime - count >= 0:
                                progress.update(100 - int(count * 100 / self.notificationTime),
                                                LOC(32143) % (LOC(self.action), self.notificationTime - count))
                                if progress.iscanceled():
                                    self.actionCanceled = True
                                    break
                                count += 1
                                xbmc.sleep(1000)

                    if not self.actionCanceled:

                        self.sendCecCommand()
                        {
                        32130: self.stopVideoAudioTV,
                        32131: self.systemReboot,
                        32132: self.systemShutdown,
                        32133: self.systemHibernate,
                        32134: self.systemSuspend,
                        32135: self.runAddon,
                        32136: self.quit,
                        32137: self.switchProfile
                        }.get(self.action)()
                        #
                        # ToDo: implement more user defined actions here
                        #       Action numbers are defined in settings.xml/strings.xml
                        #       also see LANGOFFSET
                        #
                        if self.testConfig:
                            notifyLog('watchdog was running in test mode, keep it alive')
                        else:
                            if self.keepAlive:
                                notifyLog('keep watchdog alive, update idletime for next cycle')
                                _maxIdleTime += self.maxIdleTime
                            else:
                                break
                    else:
                        notifyLog('Countdown canceled by user action')
                        notifyUser(LOC(32118), icon=ICON_DEFAULT)

                    # Reset test status
                    if self.testConfig:
                        ADDON.setSetting('testConfig', 'false')

            _loop = 0
            while not xbmc.Monitor.waitForAbort(self, 10):
                _loop += 10
                _currentIdleTime += 10

                if self.SettingsChanged:
                    notifyLog('settings changed')
                    self.getWDSettings()
                    _maxIdleTime = self.maxIdleTime
                    break

                if self.testConfig or _currentIdleTime > xbmc.getGlobalIdleTime() or _loop >= 60: break

# MAIN #

if __name__ == '__main__':

    mode = 'SERVICE'
    ADDON.setSetting('mode', mode)
    WatchDog = SleepyWatchdog()
    try:
        notifyLog('Sleepy Watchdog kicks in (mode: %s)' % mode)
        WatchDog.start()
    except Exception as e:
        notifyLog(e, level=xbmc.LOGERROR)

    notifyLog('Sleepy Watchdog kicks off from mode: %s' % WatchDog.mode)
    del WatchDog
    ADDON.setSetting('mode', mode)
