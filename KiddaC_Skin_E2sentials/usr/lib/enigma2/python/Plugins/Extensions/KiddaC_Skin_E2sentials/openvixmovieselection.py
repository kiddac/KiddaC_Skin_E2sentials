#!/usr/bin/python
# -*- coding: utf-8 -*-

# for localized messages
from . import _

from Components.ActionMap import ActionMap
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigSelection, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.MovieList import MovieList
from Screens.MovieSelection import l_moviesort


class MovieBrowserConfiguration2(ConfigListScreen, Screen):
    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        self.session = session
        self.skinName = "Setup"
        self.setup_title = _("Movie List Setup")
        Screen.setTitle(self, _(self.setup_title))

        self['footnote'] = Label("")

        self["description"] = Label("")

        self.onChangedEntry = []
        cfg = ConfigSubsection()
        cfg.moviesort = ConfigSelection(default=str(config.movielist.moviesort.value), choices=l_moviesort)
        cfg.description = ConfigYesNo(default=(config.movielist.description.value != MovieList.HIDE_DESCRIPTION))
        self.cfg = cfg

        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self.createSetup()

        self["actions"] = ActionMap(["SetupActions", 'ColorActions'], {
            "red": self.cancel,
            "green": self.save,
            "save": self.save,
            "cancel": self.cancel,
            "ok": self.save,
            "menu": self.cancel,
        }, -2)
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("OK"))

        if self.selectionChanged not in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)
        self.selectionChanged()

    def createSetup(self):
        self.list.append(getConfigListEntry(_("Use movie planner layout mod"), config.movielistmod.useextlist, _("Use alternative movie planner layouts. Primarily for for KiddaC's skins, but compatible with some other skins.")))
        self.list.append(getConfigListEntry(_("Use trash can in movie list"), config.usage.movielist_trashcan, _("When enabled, deleted recordings are moved to the trash can, instead of being deleted immediately.")))
        self.list.append(getConfigListEntry(_("Remove items from trash can after (days)"), config.usage.movielist_trashcan_days, _("Configure the number of days after which items are automatically removed from the trash can.\nA setting of 0 disables this.")))
        self.list.append(getConfigListEntry(_("Clean network trash cans"), config.usage.movielist_trashcan_network_clean, _("When enabled, network trash cans are probed for cleaning.")))
        self.list.append(getConfigListEntry(_("Disk space to reserve for recordings (in GB)"), config.usage.movielist_trashcan_reserve, _("Configure the minimum amount of disk space to be available for recordings. When the amount of space drops below this value, deleted items will be removed from the trash can.")))

        try:
            self.list.append(getConfigListEntry(_("Background delete option"), config.misc.erase_flags, _("Configure on which devices the background delete option should be used.")))
        except:
            pass

        try:
            self.list.append(getConfigListEntry(_("Background delete speed"), config.misc.erase_speed, _("Configure the speed of the background deletion process. Lower speed will consume less hard disk drive performance.")))
        except:
            pass

        self.list.append(getConfigListEntry(_("Font size"), config.movielist.fontsize, _("This allows you change the font size relative to skin size, so 1 increases by 1 point size, and -1 decreases by 1 point size")))
        self.list.append(getConfigListEntry(_("Number of rows"), config.movielist.itemsperpage, _("Number of rows to display")))
        self.list.append(getConfigListEntry(_("Use slim screen"), config.movielist.useslim, _("Use the alternative screen")))

        try:
            self.list.append(getConfigListEntry(_("Use adaptive date display"), config.movielist.use_fuzzy_dates, _("Adaptive date display allows recent dates to be displayed as 'Today' or 'Yesterday'.  It hides the year for recordings made this year.  It hides the day of the week for recordings made in previous years.")))
        except:
            pass

        try:
            self.list.append(getConfigListEntry(_("Sort"), self.cfg.moviesort, _("Set the default sorting method.")))
        except:
            pass

        try:
            self.list.append(getConfigListEntry(_("Sort Trash by deletion time"), config.usage.trashsort_deltime, _("Use the deletion time to sort Trash directories.\nMost recently deleted at the top.")))
        except:
            pass

        try:
            self.list.append(getConfigListEntry(_("Show extended description"), self.cfg.description, _("Show or hide the extended description, (skin dependant).")))
        except:
            pass

        try:
            self.list.append(getConfigListEntry(_("Use individual settings for each directory"), config.movielist.settings_per_directory, _("When set, each directory will show the previous state used. When off, the default values will be shown.")))
        except:
            pass

        if not config.movielist.settings_per_directory.value:
            try:
                self.list.append(getConfigListEntry(_("Permanent sort key changes"), config.movielist.perm_sort_changes, _("When set, sort changes via the sort key will be permanent.") + "\n" + _("When unset, sort changes will be temporary - just for this view of a directory.")))
            except:
                pass

        try:
            self.list.append(getConfigListEntry(_("Stop service on return to movie list"), config.movielist.stop_service, _("Stop previous broadcasted service on return to movie list.")))
        except:
            pass

        self.list.append(getConfigListEntry(_("Show status icons in movie list"), config.usage.show_icons_in_movielist, _("Shows the watched status of the movie.")))

        if config.usage.show_icons_in_movielist.value != 'o':
            try:
                self.list.append(getConfigListEntry(_("Show icon for new/unseen items"), config.usage.movielist_unseen, _("Shows the icons when new/unseen, otherwise it will not show an icon.")))
            except:
                pass

        self.list.append(getConfigListEntry(_("Service Title mode"), config.usage.movielist_servicename_mode, _("Show picons in the movie list.")))

        if "picon" in config.usage.movielist_servicename_mode.value:
            self.list.append(getConfigListEntry(_("Picon Width"), config.usage.movielist_piconwidth, _(".")))

        try:
            self.list.append(getConfigListEntry(_("Show movie lengths in movie list"), config.usage.load_length_of_movies_in_moviellist, _("When enabled, the length of each recording will be shown in the movielist (this might cause some additional loading time).")))
        except:
            pass

        try:
            self.list.append(getConfigListEntry(_("Play audio in background"), config.movielist.play_audio_internal, _("Keeps the movie list open whilst playing audio files.")))
        except:
            pass

        try:
            self.list.append(getConfigListEntry(_("Root directory"), config.movielist.root, _("Sets the root directory of movie list, to remove the '..' from being shown in that folder.")))
        except:
            pass

        try:
            self.list.append(getConfigListEntry(_("Hide known extensions"), config.movielist.hide_extensions, _("Allows you to hide the extensions of known file types.")))
        except:
            pass

        try:
            self.list.append(getConfigListEntry(_("Show live tv when movie stopped"), config.movielist.show_live_tv_in_movielist, _("When set the PIG will return to live after a movie has stopped playing.")))
        except:
            pass

        if config.usage.sort_settings.value:
            self.list.sort()
        self["config"].list = self.list
        self["config"].l.setList(self.list)

    def selectionChanged(self):
        self["description"].setText(self.getCurrentDescription())

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.createSetup()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.createSetup()

    def save(self):
        self.saveAll()
        cfg = self.cfg
        config.movielist.moviesort.setValue(int(cfg.moviesort.value))
        if cfg.description.value:
            config.movielist.description.value = MovieList.SHOW_DESCRIPTION
        else:
            config.movielist.description.value = MovieList.HIDE_DESCRIPTION
        if not config.movielist.settings_per_directory.value:
            config.movielist.moviesort.save()
            config.movielist.description.save()
            config.movielist.useslim.save()
            config.usage.on_movie_eof.save()
        self.close(True)

    def cancel(self):
        if self["config"].isChanged():
            self.session.openWithCallback(self.cancelCallback, MessageBox, _("Really close without saving settings?"))
        else:
            self.cancelCallback(True)

    def cancelCallback(self, answer):
        if answer:
            for x in self["config"].list:
                x[1].cancel()
            self.close(False)


def configure2(self):
    self.session.openWithCallback(self.configureDone, MovieBrowserConfiguration2)
