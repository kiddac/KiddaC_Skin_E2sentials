#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import _

from Components.config import config, ConfigSelection, ConfigSubsection, ConfigYesNo, ConfigClock, configfile, ConfigSelectionNumber
from enigma import getDesktop, addFont, eTimer
from Plugins.Plugin import PluginDescriptor
from Screens.MovieSelection import MovieSelection
from Components.MovieList import MovieList
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import SCOPE_ACTIVE_SKIN, resolveFilename
import twisted.python.runtime
import time
import os
import sys
import json

from .Task import JobManager, Task, Job


try:
    from boxbranding import getImageDistro, getImageVersion
    boxbrandingfile = True
except:
    boxbrandingfile = False

try:
    from multiprocessing.pool import ThreadPool
    hasMultiprocessing = True
except:
    hasMultiprocessing = False

try:
    from concurrent.futures import ThreadPoolExecutor
    if twisted.python.runtime.platform.supportsThreads():
        hasConcurrent = True
    else:
        hasConcurrent = False
except:
    hasConcurrent = False

pythonVer = sys.version_info.major

scraper_script = "/usr/script/toppicks_scraper.sh"
picker_script = "/usr/script/toppicks_picker.sh"

# Change permissions to 755
os.chmod(scraper_script, 0o755)
os.chmod(picker_script, 0o755)

with open("/usr/lib/enigma2/python/Plugins/Extensions/KiddaC_Skin_E2sentials/version.txt", "r") as f:
    version = f.readline()

isDreambox = False
if os.path.exists("/usr/bin/apt-get"):
    isDreambox = True

screenwidth = getDesktop(0).size()

if screenwidth.width() > 1280:
    skin_directory = "/usr/lib/enigma2/python/Plugins/Extensions/KiddaC_Skin_E2sentials/skin/fhd/"
else:
    skin_directory = "/usr/lib/enigma2/python/Plugins/Extensions/KiddaC_Skin_E2sentials/skin/hd/"


hdr = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate'
}

dir_plugins = "/usr/lib/enigma2/python/Plugins/Extensions/KiddaC_Skin_E2sentials/"

font_folder = os.path.join(dir_plugins, "fonts/")

config.plugins.E2sentials = ConfigSubsection()

cfg = config.plugins.E2sentials
cfg.useextlist = ConfigSelection(default='0', choices={'0': _('No'), '3': _('Sky Planner'), '4': _('Slyk Q Planner'), '5': _('Slyk Onyx Planner'), '6': _('VSkin Planner')})
cfg.enablemovieplannermod = ConfigYesNo(default=False)
cfg.enabletoppicksmod = ConfigYesNo(default=False)
cfg.enablescreennamesmod = ConfigYesNo(default=False)
cfg.toppickschoice = ConfigSelection(default="sky", choices={"sky": _("Sky UK"), "osn": _("OSN Arabic")})
cfg.toppicksscraper = ConfigClock(default=((9 * 60) + 9) * 60)  # 10:09
cfg.toppickspicker = ConfigSelectionNumber(5, 300, 5, default=15, wraparound=True)
cfg.toppickschannellogos = ConfigYesNo(default=True)
cfg.toppicksprogrammelogos = ConfigYesNo(default=True)
cfg.toppickschannels = ConfigSelection(choices=[("1", _("Press OK"))], default="1")

cfg.toppicks_osn_movies = ConfigYesNo(default=True)
cfg.toppicks_osn_general = ConfigYesNo(default=True)
cfg.toppicks_osn_lifestyle = ConfigYesNo(default=True)
cfg.toppicks_osn_arabic = ConfigYesNo(default=True)
cfg.toppicks_osn_kids = ConfigYesNo(default=True)
cfg.toppicks_osn_sky_lifestyle = ConfigYesNo(default=True)
cfg.toppicks_osn_sky_kids = ConfigYesNo(default=True)

cfg.toppicks_sky_documentaries = ConfigYesNo(default=True)
cfg.toppicks_sky_crime = ConfigYesNo(default=True)
cfg.toppicks_sky_nature = ConfigYesNo(default=True)
cfg.toppicks_sky_kids = ConfigYesNo(default=True)
cfg.toppicks_sky_cinema = ConfigYesNo(default=True)
cfg.toppicks_sky_sports = ConfigYesNo(default=True)
cfg.toppicks_sky_entertainment = ConfigYesNo(default=True)

if cfg.enablemovieplannermod.value:
    config.movielistmod = ConfigSubsection()
    config.movielistmod.useextlist = ConfigSelection(default='0', choices={'0': _('No'), '3': _('Sky Planner'), '4': _('Slyk Q Planner'), '5': _('Slyk Onyx Planner'), '6': _('VSkin Planner')})
    config.movielist.useextlist = ConfigSelection(default='0', choices={'0': _('No'), '3': _('Sky Planner'), '4': _('Slyk Q Planner'), '5': _('Slyk Onyx Planner'), '6': _('VSkin Planner')})
    config.movielist.useextlist.save()
    configfile.save()
else:
    config.movielist.useextlist = ConfigSelection(default="0", choices={"0": _("No"), "1": _("ServiceName"), "2": _("ServicePicon")})
    config.movielist.useextlist.save()
    configfile.save()

enigmainfo_path = '/usr/lib/enigma.info'

if os.path.exists(enigmainfo_path):
    info = {}

    # Open the file and read it line by line
    with open(enigmainfo_path, 'r') as file:
        for line in file:
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                value = value.strip("'\"")
                info[key] = value

    distro = info.get('distro')
    imageversion = info.get('imageversion')
elif boxbrandingfile:
    distro = getImageDistro()
    imageversion = getImageVersion()
else:
    distro = ""
    imageversion = ""


def main(session, **kwargs):
    from . import settings
    session.open(settings.E2sentials_Settings)
    return


def MovieList1__init__(self, root=None, sort_type=None, descr_state=None):
    # openatv 6.4 - 7.4
    try:
        myMovieList__init__(self, root, sort_type, descr_state)
    except Exception as e:
        print(e)

    self.screenwidth = getDesktop(0).size().width()

    self.iconSeries = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/series.png"))
    if self.iconSeries is None:
        self.iconSeries = LoadPixmap(skin_directory + "icons/series.png")

    self.iconDownloaded = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/downloaded.png"))
    if self.iconDownloaded is None:
        self.iconDownloaded = LoadPixmap(skin_directory + "icons/downloaded.png")


def MovieList2__init__(self, root=None, sort_type=None, descr_state=None, allowCollections=False):
    # openvix
    try:
        myMovieList__init__(self, root, sort_type, descr_state, allowCollections)
    except Exception as e:
        print(e)

    self.screenwidth = getDesktop(0).size().width()

    self.iconSeries = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/series.png"))
    if self.iconSeries is None:
        self.iconSeries = LoadPixmap(skin_directory + "icons/series.png")

    self.iconDownloaded = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/downloaded.png"))
    if self.iconDownloaded is None:
        self.iconDownloaded = LoadPixmap(skin_directory + "icons/downloaded.png")


def loadMoviePlannerMod(reason, session=None, **kwargs):
    if session is not None:

        global myMovieList__init__
        global myMovieSelection__init__

        myMovieList__init__ = MovieList.__init__

    if distro.lower() == "openvix":
        from .openvixmovieselection import configure2

        if float(imageversion) >= 5.4:
            from .openvix6 import openvix6BuildMovieListEntry
        elif float(imageversion) <= 5.3:
            from .openvix53 import openvix53BuildMovieListEntry

        MovieList.__init__ = MovieList2__init__

        if float(imageversion) >= 5.4:
            MovieList.buildMovieListEntry = openvix6BuildMovieListEntry
        elif float(imageversion) <= 5.3:
            MovieList.buildMovieListEntry = openvix53BuildMovieListEntry

        MovieSelection.configure = configure2

    elif distro.lower() == "openbh":
        from .openvixmovieselection import configure2
        from .openvix6 import openvix6BuildMovieListEntry
        MovieList.__init__ = MovieList2__init__
        MovieList.buildMovieListEntry = openvix6BuildMovieListEntry
        MovieSelection.configure = configure2

    elif distro.lower() == "openatv":
        from .openatv import openatvBuildMovieListEntry, openatvSetItemsPerPage

        MovieList.__init__ = MovieList1__init__

        try:
            MovieList.setItemsPerPage = openatvSetItemsPerPage
            MovieList.buildMovieListEntry = openatvBuildMovieListEntry
        except Exception as e:
            print(e)


autoStartTimerScraper = None
autoStartTimerPicker = None


class AutoStartTimerScraper:
    def __init__(self, session):
        self.session = session
        self.timer = eTimer()

        try:
            self.timer_conn = self.timer.timeout.connect(self.onTimer)
        except:
            self.timer.callback.append(self.onTimer)
        self.update()

    def getWakeTime(self):
        clock = cfg.toppicksscraper.value  # Scheduled time from configuration
        nowt = time.time()
        now = time.localtime(nowt)
        return int(time.mktime((now.tm_year, now.tm_mon, now.tm_mday, clock[0], clock[1], 0, now.tm_wday, now.tm_yday, now.tm_isdst)))

    def update(self, atLeast=0):
        self.timer.stop()
        wake = self.getWakeTime()
        nowtime = time.time()
        if wake > 0:
            if wake < nowtime + atLeast:
                # Schedule for the next day.
                wake += 24 * 3600
            next = wake - int(nowtime)
            if next > 3600:
                next = 3600
            if next <= 0:
                next = 60
            self.timer.startLongTimer(next)
        else:
            wake = -1
        return wake

    def onTimer(self):
        self.timer.stop()
        now = int(time.time())
        wake = self.getWakeTime()
        atLeast = 0
        if abs(wake - now) < 60:
            self.runScraper()
            atLeast = 60
        self.update(atLeast)

    def runScraper(self):
        if cfg.enabletoppicksmod.value:
            print("\n *********** Running Top Picks Scraper ************ \n")
            self.runScraperTask()

    def runScraperTask(self):
        for job in job_manager.getPendingJobs():
            job.abort()

        try:
            cfg_values = {
                'toppickschoice': cfg.toppickschoice.value,
                'toppickschannellogos': cfg.toppickschannellogos.value,
                'toppicksprogrammelogos': cfg.toppicksprogrammelogos.value,
                'toppicks_osn_movies': cfg.toppicks_osn_movies.value,
                'toppicks_osn_general': cfg.toppicks_osn_general.value,
                'toppicks_osn_lifestyle': cfg.toppicks_osn_lifestyle.value,
                'toppicks_osn_arabic': cfg.toppicks_osn_arabic.value,
                'toppicks_osn_kids': cfg.toppicks_osn_kids.value,
                'toppicks_osn_sky_lifestyle': cfg.toppicks_osn_sky_lifestyle.value,
                'toppicks_osn_sky_kids': cfg.toppicks_osn_sky_kids.value,
                'toppicks_sky_documentaries': cfg.toppicks_sky_documentaries.value,
                'toppicks_sky_crime': cfg.toppicks_sky_crime.value,
                'toppicks_sky_nature': cfg.toppicks_sky_nature.value,
                'toppicks_sky_kids': cfg.toppicks_sky_kids.value,
                'toppicks_sky_cinema': cfg.toppicks_sky_cinema.value,
                'toppicks_sky_sports': cfg.toppicks_sky_sports.value,
                'toppicks_sky_entertainment': cfg.toppicks_sky_entertainment.value,
            }

            config_path = "/etc/enigma2/e2sentials/toppicks_config.json"
            with open(config_path, 'w') as f:
                json.dump(cfg_values, f)

            job = Job("Top Picks Scraper Job")
            picker_task = Task(job, "Run Top Picks Scraper")
            picker_task.setCmdline("/usr/script/toppicks_scraper.sh")
            job.addTask(picker_task)

            job_manager.AddJob(job, onFail=None)

        except Exception as e:
            print("[runPickerTask] Error:", e)


class AutoStartTimerPicker:
    def __init__(self, session):
        self.session = session
        self.timer = eTimer()

        try:
            self.timer_conn = self.timer.timeout.connect(self.onTimer)
        except:
            self.timer.callback.append(self.onTimer)
        self.update()

    def update(self):
        self.timer.stop()
        if cfg.enabletoppicksmod.value:
            interval = cfg.toppickspicker.value * 60  # Picker interval in seconds
            self.timer.startLongTimer(interval)

    def onTimer(self):
        self.timer.stop()
        if os.path.exists("/etc/enigma2/e2sentials/all_channels_data.json"):
            if cfg.enabletoppicksmod.value:
                # Run the picker task
                # print("\n *********** Running Top Picks Picker ************ \n")
                self.runPickerTask()
        else:
            # If the JSON file does not exist, run the scraper task instead
            if cfg.enabletoppicksmod.value:
                print("\n *********** Running Top Picks Scraper ************ \n")
                self.runScraperTask()
        self.update()

    def runScraperTask(self):

        for job in job_manager.getPendingJobs():
            job.abort()

        try:
            cfg_values = {
                'toppickschoice': cfg.toppickschoice.value,
                'toppickschannellogos': cfg.toppickschannellogos.value,
                'toppicksprogrammelogos': cfg.toppicksprogrammelogos.value,
                'toppicks_osn_movies': cfg.toppicks_osn_movies.value,
                'toppicks_osn_general': cfg.toppicks_osn_general.value,
                'toppicks_osn_lifestyle': cfg.toppicks_osn_lifestyle.value,
                'toppicks_osn_arabic': cfg.toppicks_osn_arabic.value,
                'toppicks_osn_kids': cfg.toppicks_osn_kids.value,
                'toppicks_osn_sky_lifestyle': cfg.toppicks_osn_sky_lifestyle.value,
                'toppicks_osn_sky_kids': cfg.toppicks_osn_sky_kids.value,
                'toppicks_sky_documentaries': cfg.toppicks_sky_documentaries.value,
                'toppicks_sky_crime': cfg.toppicks_sky_crime.value,
                'toppicks_sky_nature': cfg.toppicks_sky_nature.value,
                'toppicks_sky_kids': cfg.toppicks_sky_kids.value,
                'toppicks_sky_cinema': cfg.toppicks_sky_cinema.value,
                'toppicks_sky_sports': cfg.toppicks_sky_sports.value,
                'toppicks_sky_entertainment': cfg.toppicks_sky_entertainment.value,
            }

            config_path = "/etc/enigma2/e2sentials/toppicks_config.json"
            with open(config_path, 'w') as f:
                json.dump(cfg_values, f)

            job = Job("Top Picks Scraper Job")
            picker_task = Task(job, "Run Top Picks Scraper")
            picker_task.setCmdline("/usr/script/toppicks_scraper.sh")
            job.addTask(picker_task)

            job_manager.AddJob(job, onFail=None)

        except Exception as e:
            print("[runPickerTask] Error:", e)

    def runPickerTask(self):

        for job in job_manager.getPendingJobs():
            job.abort()

        try:
            cfg_values = {
                'toppickschoice': cfg.toppickschoice.value,
                'toppickschannellogos': cfg.toppickschannellogos.value,
                'toppicksprogrammelogos': cfg.toppicksprogrammelogos.value,
                'toppicks_osn_movies': cfg.toppicks_osn_movies.value,
                'toppicks_osn_general': cfg.toppicks_osn_general.value,
                'toppicks_osn_lifestyle': cfg.toppicks_osn_lifestyle.value,
                'toppicks_osn_arabic': cfg.toppicks_osn_arabic.value,
                'toppicks_osn_kids': cfg.toppicks_osn_kids.value,
                'toppicks_osn_sky_lifestyle': cfg.toppicks_osn_sky_lifestyle.value,
                'toppicks_osn_sky_kids': cfg.toppicks_osn_sky_kids.value,
                'toppicks_sky_documentaries': cfg.toppicks_sky_documentaries.value,
                'toppicks_sky_crime': cfg.toppicks_sky_crime.value,
                'toppicks_sky_nature': cfg.toppicks_sky_nature.value,
                'toppicks_sky_kids': cfg.toppicks_sky_kids.value,
                'toppicks_sky_cinema': cfg.toppicks_sky_cinema.value,
                'toppicks_sky_sports': cfg.toppicks_sky_sports.value,
                'toppicks_sky_entertainment': cfg.toppicks_sky_entertainment.value,
            }

            config_path = "/etc/enigma2/e2sentials/toppicks_config.json"
            with open(config_path, 'w') as f:
                json.dump(cfg_values, f)

            job = Job("Top Picks Picker Job")
            picker_task = Task(job, "Run Top Picks Picker")
            picker_task.setCmdline("/usr/script/toppicks_picker.sh")
            job.addTask(picker_task)

            job_manager.AddJob(job, onFail=None)

        except Exception as e:
            print("[runPickerTask] Error:", e)


job_manager = JobManager()

delayTimer = eTimer()


def autostart(reason, session=None, **kwargs):
    if cfg.enablemovieplannermod.value:
        loadMoviePlannerMod(reason, session, **kwargs)

    global autoStartTimerScraper, autoStartTimerPicker

    def startTimers():
        """Callback function to initialize the timers after delay."""
        global autoStartTimerScraper, autoStartTimerPicker
        if reason == 0:
            if session is not None:
                if autoStartTimerScraper is None:
                    autoStartTimerScraper = AutoStartTimerScraper(session)
                if autoStartTimerPicker is None:
                    autoStartTimerPicker = AutoStartTimerPicker(session)

    if reason == 0 and session is not None:
        delayTimer.callback.append(startTimers)
        delayTimer.startLongTimer(60)  # Delay of 60 seconds
    return


def autostartscreennames(reason, **kwargs):
    if reason == 0:
        if cfg.enablescreennamesmod.value:
            from . import screennames
            screennames.ScreenNamesAuto.startScreenNames(kwargs["session"])


def Plugins(**kwargs):
    addFont(os.path.join(font_folder, "m-plus-rounded-1c-regular.ttf"), "e2sentialsregular", 100, 0)

    iconFile = "icons/plugin-icon_sd.png"
    if screenwidth.width() > 1280:
        iconFile = "icons/plugin-icon.png"

    description = _("Skin additions - Top Picks, Movie Planner Mods, Screen Names")
    pluginname = _("KiddaC Skin E2sentials")

    result = [
        PluginDescriptor(name=pluginname, description=description, where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart),
        PluginDescriptor(name=pluginname, description=description, where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=autostartscreennames),
        PluginDescriptor(name=pluginname, description=description, where=PluginDescriptor.WHERE_PLUGINMENU, icon=iconFile, fnc=main)
    ]
    return result
