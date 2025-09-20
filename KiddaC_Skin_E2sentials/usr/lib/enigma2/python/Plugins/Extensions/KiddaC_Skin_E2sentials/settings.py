#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json

from . import _
from .plugin import cfg, skin_directory, distro, version
from .xStaticText import StaticText

from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Pixmap import Pixmap
from Components.config import (
    ConfigSelection,
    ConfigText,
    ConfigYesNo,
    configfile,
    getConfigListEntry,
)
from Screens import Standby
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

from .Task import JobManager, Task, Job

job_manager = JobManager()


class E2sentials_Settings(ConfigListScreen, Screen):
    ALLOW_SUSPEND = True

    def __init__(self, session):
        Screen.__init__(self, session)

        self.session = session

        skin_path = os.path.join(skin_directory)
        skin = os.path.join(skin_path, "settings.xml")
        if os.path.exists("/var/lib/dpkg/status"):
            skin = os.path.join(skin_path, "DreamOS/settings.xml")

        with open(skin, "r") as f:
            self.skin = f.read()

        self.setup_title = _("Settings")

        self.onChangedEntry = []

        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)

        self["key_red"] = StaticText(_("Back"))
        self["key_green"] = StaticText(_("Save"))
        self["key_yellow"] = StaticText()
        self["key_blue"] = StaticText()
        self["version"] = StaticText()

        self.file_path = '/etc/enigma2/e2sentials/all_channels_data.json'

        self["VKeyIcon"] = Pixmap()
        self["VKeyIcon"].hide()
        self["HelpWindow"] = Pixmap()
        self["HelpWindow"].hide()

        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
            "cancel": self.cancel,
            "red": self.cancel,
            "green": self.save,
            "yellow": self.scraper,
            "blue": self.picker,
        }, -2)

        self["version"].setText(version)

        self.initConfig()
        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def cancel(self, answer=None):

        if answer is None:
            if self["config"].isChanged():
                self.session.openWithCallback(self.cancel, MessageBox, _("Really close without saving settings?"))
            else:
                self.close()
        elif answer:
            for x in self["config"].list:
                x[1].cancel()

            self.close()
        return

    def save(self):
        if cfg.enabletoppicksmod:

            # Check if OSN is selected and validate its categories
            osn_selected = cfg.toppickschoice.value == "osn"
            osn_categories_selected = any([
                cfg.toppicks_osn_movies.value,
                cfg.toppicks_osn_general.value,
                cfg.toppicks_osn_lifestyle.value,
                cfg.toppicks_osn_arabic.value,
                cfg.toppicks_osn_kids.value,
                cfg.toppicks_osn_sky_lifestyle.value,
                cfg.toppicks_osn_sky_kids.value
            ]) if osn_selected else False

            # Check if Sky is selected and validate its categories
            sky_selected = cfg.toppickschoice.value == "sky"
            sky_categories_selected = any([
                cfg.toppicks_sky_documentaries.value,
                cfg.toppicks_sky_crime.value,
                cfg.toppicks_sky_nature.value,
                cfg.toppicks_sky_kids.value,
                cfg.toppicks_sky_cinema.value,
                cfg.toppicks_sky_sports.value,
                cfg.toppicks_sky_entertainment.value
            ]) if sky_selected else False

            # Show an error message if no categories are selected for the chosen provider
            if osn_selected and not osn_categories_selected:
                self.session.open(
                    MessageBox,
                    _("No OSN categories selected. Please enter a some categories to show images for."),
                    MessageBox.TYPE_ERROR,
                    timeout=10
                )
                return

            if sky_selected and not sky_categories_selected:
                self.session.open(
                    MessageBox,
                    _("No Sky categories selected. Please enter a some categories to show images for."),
                    MessageBox.TYPE_ERROR,
                    timeout=10
                )
                return

        # Save the configuration if changes were made
        if self["config"].isChanged():
            for x in self["config"].list:
                x[1].save()
            cfg.save()
            configfile.save()

        self.finished()

    def scraper(self):
        if self["key_yellow"].getText() == _("Download Images"):
            self.runScraperTask()

    def picker(self):
        if self["key_blue"].getText() == _("Refresh Images"):
            self.runPickerTask()

    def finished(self):
        if self.org_enablemovieplannermod != cfg.enablemovieplannermod.value or self.org_enabletoppicksmod != cfg.enabletoppicksmod.value or self.org_enablescreennamesmod != cfg.enablescreennamesmod.value:
            self.changedFinished()
        else:
            self.scraper()

        self.close()

    def changedFinished(self):
        self.session.openWithCallback(self.ExecuteRestart, MessageBox, _("You need to restart the GUI") + "\n" + _("Do you want to restart now?"), MessageBox.TYPE_YESNO)
        self.close()

    def ExecuteRestart(self, result=None):
        if result:
            Standby.quitMainloop(3)
        else:
            if cfg.enabletoppicksmod:
                self.runScraperTask()
            self.close()

    def initConfig(self):
        self.cfg_enablescreennamesmod = getConfigListEntry(_("Enable Screen Names Debug"), cfg.enablescreennamesmod)
        self.cfg_enablemovieplannermod = getConfigListEntry(_("Enable Movie Planner Mod"), cfg.enablemovieplannermod)
        self.cfg_enabletoppicksmod = getConfigListEntry(_("Enable Top Picks Mod"), cfg.enabletoppicksmod)
        self.cfg_toppickschoice = getConfigListEntry(_("Top Picks image set"), cfg.toppickschoice)

        self.cfg_toppicksscraper = getConfigListEntry(_("Top Picks download images time"), cfg.toppicksscraper)
        self.cfg_toppickspicker = getConfigListEntry(_("Top Picks refresh images every (X) mins..."), cfg.toppickspicker)
        self.cfg_toppickschannellogo = getConfigListEntry(_("Top Picks show channel logo overlays"), cfg.toppickschannellogos)
        self.cfg_toppicksprogrammelogos = getConfigListEntry(_("Top Picks show backdrop programme logo overlay"), cfg.toppicksprogrammelogos)

        self.cfg_toppicks_osn_movies = getConfigListEntry(_("Show Movie channels"), cfg.toppicks_osn_movies)
        self.cfg_toppicks_osn_general = getConfigListEntry(_("Show General channels"), cfg.toppicks_osn_general)
        self.cfg_toppicks_osn_lifestyle = getConfigListEntry(_("Show Lifestyle channels"), cfg.toppicks_osn_lifestyle)
        self.cfg_toppicks_osn_arabic = getConfigListEntry(_("Show Arabic channels"), cfg.toppicks_osn_arabic)
        self.cfg_toppicks_osn_kids = getConfigListEntry(_("Show Kids channels"), cfg.toppicks_osn_kids)
        self.cfg_toppicks_osn_sky_lifestyle = getConfigListEntry(_("Show Sky Lifestyle"), cfg.toppicks_osn_sky_lifestyle)
        self.cfg_toppicks_osn_sky_kids = getConfigListEntry(_("Show Sky Kids"), cfg.toppicks_osn_sky_kids)

        self.cfg_toppicks_sky_documentaries = getConfigListEntry(_("Show Documentary channels"), cfg.toppicks_sky_documentaries)
        self.cfg_toppicks_sky_crime = getConfigListEntry(_("Show Crime channels"), cfg.toppicks_sky_crime)
        self.cfg_toppicks_sky_nature = getConfigListEntry(_("Show Nature channels"), cfg.toppicks_sky_nature)
        self.cfg_toppicks_sky_kids = getConfigListEntry(_("Show Kids channels"), cfg.toppicks_sky_kids)
        self.cfg_toppicks_sky_cinema = getConfigListEntry(_("Show Cinema channels"), cfg.toppicks_sky_cinema)
        self.cfg_toppicks_sky_sports = getConfigListEntry(_("Show Sports channels"), cfg.toppicks_sky_sports)
        self.cfg_toppicks_sky_entertainment = getConfigListEntry(_("Show Entertainment channels"), cfg.toppicks_sky_entertainment)

        self.org_enablemovieplannermod = cfg.enablemovieplannermod.value
        self.org_enabletoppicksmod = cfg.enabletoppicksmod.value
        self.org_enablescreennamesmod = cfg.enablescreennamesmod.value

        self.createSetup()

    def createSetup(self):
        if cfg.enabletoppicksmod.value:
            self["key_yellow"].setText(_("Download Images"))
        else:
            self["key_yellow"].setText("")

        if cfg.enabletoppicksmod.value and os.path.exists(self.file_path) and os.path.isfile(self.file_path) and os.path.getsize(self.file_path) > 0:
            self["key_blue"].setText(_("Refresh Images"))
        else:
            self["key_blue"].setText("")

        config_entries = [
            self.cfg_enablescreennamesmod,
            self.cfg_enablemovieplannermod if distro.lower() == "openvix" or distro.lower() == "openbh" or distro.lower() == "openatv" else None,
            self.cfg_enabletoppicksmod,

            self.cfg_toppickschoice if cfg.enabletoppicksmod.value else None,
            self.cfg_toppicksscraper if cfg.enabletoppicksmod.value else None,
            self.cfg_toppickspicker if cfg.enabletoppicksmod.value else None,
            self.cfg_toppickschannellogo if cfg.enabletoppicksmod.value else None,
            self.cfg_toppicksprogrammelogos if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "osn") else None,

            self.cfg_toppicks_osn_movies if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "osn") else None,
            self.cfg_toppicks_osn_general if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "osn") else None,
            self.cfg_toppicks_osn_lifestyle if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "osn") else None,
            self.cfg_toppicks_osn_arabic if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "osn") else None,
            self.cfg_toppicks_osn_kids if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "osn") else None,
            self.cfg_toppicks_osn_sky_lifestyle if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "osn") else None,
            self.cfg_toppicks_osn_sky_kids if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "osn") else None,

            self.cfg_toppicks_sky_documentaries if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "sky") else None,
            self.cfg_toppicks_sky_crime if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "sky") else None,
            self.cfg_toppicks_sky_nature if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "sky") else None,
            self.cfg_toppicks_sky_kids if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "sky") else None,
            self.cfg_toppicks_sky_cinema if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "sky") else None,
            self.cfg_toppicks_sky_sports if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "sky") else None,
            self.cfg_toppicks_sky_entertainment if (cfg.enabletoppicksmod.value and cfg.toppickschoice.value == "sky") else None,
        ]

        self.list = [entry for entry in config_entries if entry is not None]

        self["config"].list = self.list
        self["config"].l.setList(self.list)
        self.handleInputHelpers()

    def handleInputHelpers(self):
        from enigma import ePoint
        currConfig = self["config"].getCurrent()

        if currConfig is not None:
            if isinstance(currConfig[1], ConfigText):
                if "VKeyIcon" in self:
                    try:
                        self["VirtualKB"].setEnabled(True)
                    except:
                        pass

                    try:
                        self["virtualKeyBoardActions"].setEnabled(True)
                    except:
                        pass
                    self["VKeyIcon"].show()

                if "HelpWindow" in self and currConfig[1].help_window and currConfig[1].help_window.instance is not None:
                    helpwindowpos = self["HelpWindow"].getPosition()
                    currConfig[1].help_window.instance.move(ePoint(helpwindowpos[0], helpwindowpos[1]))

            else:
                if "VKeyIcon" in self:
                    try:
                        self["VirtualKB"].setEnabled(False)
                    except:
                        pass

                    try:
                        self["virtualKeyBoardActions"].setEnabled(False)
                    except:
                        pass
                    self["VKeyIcon"].hide()

    def changedEntry(self):
        self.item = self["config"].getCurrent()
        for x in self.onChangedEntry:
            x()

        try:
            if isinstance(self["config"].getCurrent()[1], ConfigYesNo) or isinstance(self["config"].getCurrent()[1], ConfigSelection):
                self.createSetup()
        except:
            pass

    def getCurrentEntry(self):
        return self["config"].getCurrent() and self["config"].getCurrent()[0] or ""

    def getCurrentValue(self):
        return self["config"].getCurrent() and str(self["config"].getCurrent()[1].getText()) or ""

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
            self["key_blue"].setText("")

        except Exception as e:
            print("[runPickerTask] Error:", e)

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
            self["key_yellow"].setText("")

        except Exception as e:
            print("[runPickerTask] Error:", e)
