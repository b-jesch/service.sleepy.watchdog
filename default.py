if __name__ == '__main__':

    from service import *

    dialog = xbmcgui.Dialog()
    _offset = 1

    if ADDON.getSetting('mode') == 'USER':
        _idx = dialog.select(LOC(32119), [LOC(32210), LOC(32180), LOC(32181), LOC(32182), LOC(32183), LOC(32184),
                                          LOC(32185), LOC(32186), LOC(32187), LOC(32188), LOC(32189)])
    else:
        _idx = dialog.select(LOC(32119), [LOC(32180), LOC(32181), LOC(32182), LOC(32183), LOC(32184), LOC(32185),
                                          LOC(32186), LOC(32187), LOC(32188), LOC(32189)])
        _offset = 0

    if _idx > -1:
        _userIdleTime = LOC(32180 + _idx + _offset)

        if _offset > 0 and _idx == 0:
            mode = 'SERVICE'
        else:
            mode = 'USER'

        ADDON.setSetting('mode', mode)
        if mode == 'USER':
            ADDON.setSetting('userIdleTime', str(int((re.match('\d+', _userIdleTime).group())) * 60))
            _action = int(ADDON.getSetting('action')) + LANGOFFSET
            notifyLog('Sleepy Watchdog set mode to: %s for %s' % (mode, _userIdleTime))
            notifyUser(LOC(32129) % (LOC(_action), _userIdleTime))
        else:
            ADDON.setSetting('userIdleTime', '0')
            notifyLog('Sleepy Watchdog set mode to: %s' % mode)
            notifyUser(LOC(32211))
    else:
        notifyUser(LOC(32139))
