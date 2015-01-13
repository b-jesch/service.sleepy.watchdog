# das vollständige Skript

import xbmc, xbmcgui, xbmcaddon

addon = xbmcaddon.Addon("service.playback.sleeptimer")
counter = 180   # 3 Minuten (180 sec)
bar = 0         # Progressanzeige (Null Prozent)

while(not xbmc.abortRequested):
    # Testen ob Idletimer länger als Idlezeit idlet, 180 sec abziehen
    if xbmc.getGlobalIdleTime() > (int(addon.getSetting('idle_time_min'))*60 - counter):


        # Popup starten
        PopUp = xbmcgui.DialogProgress()
        PopUp.create('Inaktivitätstimer', 'laufendes Video wird in %s Sekunden gestoppt.' % counter)
        PopUp.update(bar)
        # Progressbar synchronisieren, 180 sec runterzählen
        while bar < counter and not PopUp.iscanceled():
            bar += 1
            percent = int(bar * 100 / counter)
            PopUp.update(percent, 'laufendes Video wird in %s Sekunden gestoppt.' % (counter - bar))
            xbmc.sleep(1000)

        # Popup schliessen
        PopUp.close()
        if not PopUp.iscanceled():
            # definierte Aktionen ausführen
            # Player stoppen
            if xbmc.Player().isPlaying():
                xbmc.Player().stop()
                
    xbmc.sleep(60000)