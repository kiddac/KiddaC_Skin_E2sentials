#!/usr/bin/python
# -*- coding: utf-8 -*-

# for localized messages
from . import _

from enigma import iServiceInformation, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_CENTER, BT_SCALE, BT_KEEP_ASPECT_RATIO, BT_HALIGN_CENTER, BT_ALIGN_CENTER, BT_VALIGN_CENTER, eServiceReference, eServiceCenter, loadPNG

try:
    from gettext import ngettext
except:
    print("*** gettext error ***")

from Components.config import config
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend, MultiContentEntryProgress
from Components.Renderer.Picon import getPiconName
from datetime import datetime
from time import localtime, strftime
from Tools.FuzzyDate import FuzzyTime
from ServiceReference import ServiceReference


from Components.MovieList import MovieListData, moviePlayState

try:
    from Components.MovieList import RECORD_EXTENSIONS
except:
    RECORD_EXTENSIONS = (".ts")

import os


def openvix53BuildMovieListEntry(self, serviceref, info, begin, data):
    # #################### mod ###################### #
    ext = config.movielistmod.useextlist.value
    ih = self.itemHeight
    myscalefactor = 1
    if self.screenwidth >= 1920:
        listBeginX = 3
        listEndX = 3
        listMarginX = 12
        pathIconSize = 30
        dataIconSize = 30
        progressIconSize = 30
        progressBarSize = 72
        textPosY = 2

        trashIconSizeH = 36
        trashIconSizeW = 33
        folderIconSizeH = 42
        folderIconSizeW = 36
        seenIconSize = 30
        seenIconPosY = ih // 2 - seenIconSize // 2

    else:
        listBeginX = 2
        listEndX = 2
        listMarginX = 8
        pathIconSize = 20
        dataIconSize = 20
        progressIconSize = 20
        progressBarSize = 48
        textPosY = 1

        trashIconSizeH = 24
        trashIconSizeW = 22
        folderIconSizeH = 28
        folderIconSizeW = 24
        seenIconSize = 20
        seenIconPosY = ih // 2 - seenIconSize // 2
        myscalefactor = 1.5
    # ############################################# #

    showPicons = "picon" in config.usage.movielist_servicename_mode.value
    switch = config.usage.show_icons_in_movielist.value
    piconWidth = config.usage.movielist_piconwidth.value if showPicons else 0
    durationWidth = self.durationWidth if config.usage.load_length_of_movies_in_moviellist.value else 0

    width = self.l.getItemSize().width()

    dateWidth = self.dateWidth
    if not config.movielist.use_fuzzy_dates.value:
        dateWidth += 30

    iconSize = self.iconsWidth
    if switch == 'p':
        iconSize = self.pbarLargeWidth
    ih = self.itemHeight
    col0iconSize = piconWidth if showPicons else iconSize

    space = self.spaceIconeText
    r = self.spaceRight
    pathName = serviceref.getPath()
    res = [None]

    if serviceref.flags & eServiceReference.mustDescent:

        # #################### mod ###################### #
        trashIconPosY = ih // 2 - trashIconSizeH // 2
        folderIconPosY = ih // 2 - folderIconSizeH // 2
        # ############################################### #
        # Directory
        # Name is full path name
        if info is None:
            # Special case: "parent"
            txt = ".."
        else:
            p = os.path.split(pathName)
            if not p[1]:
                # if path ends in '/', p is blank.
                p = os.path.split(p[0])
            txt = p[1]
        # trashcan
        if txt == ".Trash":
            if ext == "0":
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(0, 0), size=(col0iconSize, self.itemHeight), png=self.iconTrash, flags=BT_ALIGN_CENTER))
                res.append(MultiContentEntryText(pos=(col0iconSize + space, 0), size=(width - 145, self.itemHeight), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Deleted items")))
                res.append(MultiContentEntryText(pos=(width - 145 - r, 0), size=(145, self.itemHeight), font=1, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=_("Trash can")))

            # #################### mod ###################### #
            else:
                if ext == "3":
                    res.append(MultiContentEntryText(pos=(12 // myscalefactor, 0), size=(573 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Deleted items")))
                    res.append(MultiContentEntryPixmapAlphaBlend(pos=(629 // myscalefactor, trashIconPosY), size=(trashIconSizeW, trashIconSizeH), png=self.iconTrash))
                    res.append(MultiContentEntryText(pos=(705 // myscalefactor, 0), size=(327 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Trashcan")))

                if ext == "4":
                    res.append(MultiContentEntryText(pos=(12 // myscalefactor, 0), size=(483 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Deleted items")))
                    res.append(MultiContentEntryPixmapAlphaBlend(pos=(510 // myscalefactor, trashIconPosY), size=(trashIconSizeW, trashIconSizeH), png=self.iconTrash))
                    res.append(MultiContentEntryText(pos=(561 // myscalefactor, 0), size=(150 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Trashcan")))

                if ext == "5" or ext == "6":
                    res.append(MultiContentEntryPixmapAlphaBlend(pos=(15 // myscalefactor, trashIconPosY), size=(trashIconSizeW, trashIconSizeH), png=self.iconTrash))
                    res.append(MultiContentEntryText(pos=(68 // myscalefactor, 0), size=(705 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Deleted Recordings")))
            # ############################################### #

            return res

        # directory
        if ext == "0":
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(0, 0), size=(col0iconSize, self.itemHeight), png=self.iconFolder, flags=BT_ALIGN_CENTER))

            if self.getCurrent() in self.markList:
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(0, 0), size=(col0iconSize, self.itemHeight), png=self.iconMarked))

            res.append(MultiContentEntryText(pos=(col0iconSize + space, 0), size=(width - 145, self.itemHeight), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=txt))
            res.append(MultiContentEntryText(pos=(width - 145 - r, 0), size=(145, self.itemHeight), font=1, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=_("Directory")))

        # #################### mod ###################### #
        else:
            if ext == "3":
                res.append(MultiContentEntryText(pos=(12 // myscalefactor, 0), size=(573 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=txt))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(629 // myscalefactor, folderIconPosY), size=(folderIconSizeW, folderIconSizeH), png=self.iconSeries))
                res.append(MultiContentEntryText(pos=(705 // myscalefactor, 0), size=(327 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Directory")))

            if ext == "4":
                res.append(MultiContentEntryText(pos=(12 // myscalefactor, 0), size=(483 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=txt))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(510 // myscalefactor, folderIconPosY), size=(folderIconSizeW, folderIconSizeH), png=self.iconSeries))
                res.append(MultiContentEntryText(pos=(561 // myscalefactor, 0), size=(150 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Directory")))

            if ext == "5" or ext == "6":
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(15 // myscalefactor, folderIconPosY), size=(folderIconSizeW, folderIconSizeH), png=self.iconFolder))
                res.append(MultiContentEntryText(pos=(68 // myscalefactor, 0), size=(705 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=txt))
        # ############################################### #

        return res

    if data == -1 or data is None:
        data = MovieListData()
        cur_idx = self.l.getCurrentSelectionIndex()
        x = self.list[cur_idx]  # x = ref,info,begin,...
        if config.usage.load_length_of_movies_in_moviellist.value:
            data.len = x[1].getLength(x[0])  # recalc the movie length...
        else:
            data.len = 0  # dont recalc movielist to speedup loading the list
        self.list[cur_idx] = (x[0], x[1], x[2], data)  # update entry in list... so next time we don't need to recalc
        data.txt = info.getName(serviceref)
        data.icon = None
        data.part = None
        # #################### mod ###################### #
        data.viewed = None
        # ############################################### #
        if os.path.split(pathName)[1] in self.runningTimers:
            if switch == 'i':
                if (self.playInBackground or self.playInForeground) and serviceref == (self.playInBackground or self.playInForeground):
                    data.icon = self.iconMoviePlayRec
                else:
                    data.icon = self.iconMovieRec
                    # #################### mod ###################### #
                    data.viewed = 'Recording'
                    # ############################################### #
            elif switch in ('p', 's'):
                data.part = 100
                if (self.playInBackground or self.playInForeground) and serviceref == (self.playInBackground or self.playInForeground):
                    data.partcol = self.pbarColourSeen
                else:
                    data.partcol = self.pbarColourRec
        elif (self.playInBackground or self.playInForeground) and serviceref == (self.playInBackground or self.playInForeground):
            data.icon = self.iconMoviePlay
            # #################### mod ###################### #
            data.viewed = 'Playing'
            # ############################################### #
        else:
            data.part = moviePlayState(pathName + '.cuts', serviceref, data.len)
            if switch == 'i':
                if data.part is not None and data.part > 0:
                    data.icon = self.iconPart[data.part // 25]

                    # #################### mod ###################### #
                    data.viewed = 'Viewed'
                    # ############################################### #
                else:
                    if config.usage.movielist_unseen.value:
                        data.icon = self.iconUnwatched
                        # #################### mod ###################### #
                        data.viewed = 'Recorded'
                        # ############################################### #
            elif switch in ('p', 's'):
                if data.part is not None and data.part > 0:
                    data.partcol = self.pbarColourSeen
                else:
                    if config.usage.movielist_unseen.value:
                        data.part = 100
                        data.partcol = self.pbarColour

    colX = 0
    if switch == 'p':
        iconSize = self.pbarLargeWidth
    ih = self.itemHeight

    def addProgress():
        # icon/progress
        if ext == "0":
            if data:
                if switch == 'i' and hasattr(data, 'icon') and data.icon is not None:
                    res.append(MultiContentEntryPixmapAlphaBlend(pos=(colX, self.partIconeShift), size=(iconSize, data.icon.size(). height()), png=data.icon))
                elif switch in ('p', 's'):
                    if hasattr(data, 'part') and data.part > 0:
                        res.append(MultiContentEntryProgress(pos=(colX, self.pbarShift), size=(iconSize, self.pbarHeight), percent=data.part, borderWidth=2, foreColor=data.partcol, foreColorSelected=None, backColor=None, backColorSelected=None))
                    elif hasattr(data, 'icon') and data.icon is not None:
                        res.append(MultiContentEntryPixmapAlphaBlend(pos=(colX, self.pbarShift), size=(iconSize, self.pbarHeight), png=data.icon))
        return iconSize

    # serviceref = info.getInfoString(serviceref, iServiceInformation.sServiceref)
    displayPicon = None

    if ext == "0":
        if piconWidth > 0:
            # Picon
            picon = getPiconName(serviceref)
            if picon != "":
                displayPicon = loadPNG(picon)
            if displayPicon is not None:
                res.append(MultiContentEntryPixmapAlphaBlend(
                    pos=(colX, 0), size=(piconWidth, ih),
                    png=displayPicon,
                    backcolor=None, backcolor_sel=None, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO | BT_HALIGN_CENTER | BT_VALIGN_CENTER))
            colX += piconWidth + space
        else:
            colX += addProgress() + space

        # Recording name
        res.append(MultiContentEntryText(pos=(colX, 0), size=(width - iconSize - space - durationWidth - dateWidth - r - colX, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
        colX = width - iconSize - space - durationWidth - dateWidth - r

        if piconWidth > 0:
            colX += addProgress()

        # Duration - optionally active
        if durationWidth > 0:
            if data:
                len = data.len
                if len > 0:
                    len = ngettext("%d Min", "%d Mins", (len / 60)) % (len / 60)
                    res.append(MultiContentEntryText(pos=(colX, 0), size=(durationWidth, ih), font=1, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=len))

    # Date
    begin_string = ""
    if begin > 0:
        if config.movielist.use_fuzzy_dates.value:
            begin_string = ', '.join(FuzzyTime(begin, inPast=True))
        else:
            begin_string = strftime("%s, %s" % (config.usage.date.daylong.value, config.usage.time.short.value), localtime(begin))

        # #################### mod ###################### #
        d = datetime.fromtimestamp(begin)
        slyk_date_string = d.strftime("%a %d/%m")
        slyk_date_time_string = d.strftime("%a %d %b %H:%M")
        vskin_date_day = d.strftime("%a")
        vskin_date_date = d.strftime("%d/%m")
        vskin_date_time = d.strftime("%H:%M")
        # ############################################### #
    if ext == "0":
        res.append(MultiContentEntryText(pos=(width - dateWidth - r, 0), size=(dateWidth, ih), font=1, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=begin_string))
    else:
        # #################### mod ###################### #
        # getrec = info.getName(serviceref)
        getrec = serviceref.getPath()
        fileName, fileExtension = os.path.splitext(getrec)

        service = None
        try:
            serviceHandler = eServiceCenter.getInstance()
            info = serviceHandler.info(serviceref)
            ref = info.getInfoString(serviceref, iServiceInformation.sServiceref)       # get reference
            service = ServiceReference(ref).getServiceName()                            # get service name
        except Exception as e:
            print(('[MovieList] load extended infos get failed: ', e))

        # sky planner
        if ext == '3':
            if fileExtension in RECORD_EXTENSIONS:
                if data.part is not None and data.part > 0:
                    res.append(MultiContentEntryProgress(pos=(909 // myscalefactor, ih // 2 - 3), size=(123 // myscalefactor, 9 // myscalefactor), percent=data.part, borderWidth=1, foreColor=0x207be1, foreColorSelected=0x207be1, backColor=0x0b1e40, backColorSelected=None))
                res.append(MultiContentEntryText(pos=(12 // myscalefactor, 0), size=(573 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(629 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=data.icon))
                res.append(MultiContentEntryText(pos=(705 // myscalefactor, 0), size=(203 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.viewed))
                res.append(MultiContentEntryText(pos=(1068 // myscalefactor, 0), size=(309 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=service))
                res.append(MultiContentEntryText(pos=(1413 // myscalefactor, 0), size=(189 // myscalefactor, ih), font=1, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=slyk_date_string))
            else:
                if data.part is not None and data.part > 0:
                    res.append(MultiContentEntryProgress(pos=(909 // myscalefactor, ih // 2 - 3), size=(123 // myscalefactor, 9 // myscalefactor), percent=data.part, borderWidth=1, foreColor=0x207be1, foreColorSelected=0x207be1, backColor=0x0b1e40, backColorSelected=None))
                    res.append(MultiContentEntryText(pos=(705 // myscalefactor, 0), size=(203 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.viewed))
                else:
                    data.viewed = 'Downloaded'
                    res.append(MultiContentEntryText(pos=(705 // myscalefactor, 0), size=(327 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.viewed))
                res.append(MultiContentEntryText(pos=(12 // myscalefactor, 0), size=(573 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(629 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=self.iconDownloaded))
                res.append(MultiContentEntryText(pos=(1413 // myscalefactor, 0), size=(189 // myscalefactor, ih), font=1, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=slyk_date_string))
            return res

        # slyk q planner
        if ext == '4':
            if fileExtension in RECORD_EXTENSIONS:
                if data.part is not None and data.part > 0:
                    res.append(MultiContentEntryProgress(pos=(726 // myscalefactor, ih // 2 - 3), size=(123 // myscalefactor, 9 // myscalefactor), percent=data.part, borderWidth=1, foreColor=0x207be1, foreColorSelected=0x207be1, backColor=0x0b1e40, backColorSelected=None))
                res.append(MultiContentEntryText(pos=(12 // myscalefactor, 0), size=(483 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(510 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=data.icon))
                res.append(MultiContentEntryText(pos=(561 // myscalefactor, 0), size=(150 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.viewed))
                res.append(MultiContentEntryText(pos=(864 // myscalefactor, 0), size=(240 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=service))
                res.append(MultiContentEntryText(pos=(1119 // myscalefactor, 0), size=(135 // myscalefactor, ih), font=0, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=slyk_date_string))
            else:
                if data.part is not None and data.part > 0:
                    res.append(MultiContentEntryProgress(pos=(726 // myscalefactor, ih // 2 - 3), size=(123 // myscalefactor, 9 // myscalefactor), percent=data.part, borderWidth=1, foreColor=0x207be1, foreColorSelected=0x207be1, backColor=0x0b1e40, backColorSelected=None))
                    res.append(MultiContentEntryText(pos=(561 // myscalefactor, 0), size=(150 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.viewed))
                else:
                    data.viewed = 'Downloaded'
                    res.append(MultiContentEntryText(pos=(561 // myscalefactor, 0), size=(150 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.viewed))
                res.append(MultiContentEntryText(pos=(12 // myscalefactor, 0), size=(483 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(510 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=self.iconDownloaded))
                res.append(MultiContentEntryText(pos=(1119 // myscalefactor, 0), size=(135 // myscalefactor, ih), font=0, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=slyk_date_string))
            return res

        # slyk onyx planner
        if ext == '5':
            if fileExtension in RECORD_EXTENSIONS:
                if data.part is not None and data.part > 0:
                    res.append(MultiContentEntryProgress(pos=(1230 // myscalefactor, ih // 2 - 3), size=(90 // myscalefactor, 9 // myscalefactor), percent=data.part, borderWidth=1, foreColor=0x006fce, foreColorSelected=0xffffff, backColor=0x000000, backColorSelected=None))
                res.append(MultiContentEntryText(pos=(15 // myscalefactor, 0), size=(447 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
                res.append(MultiContentEntryText(pos=(477 // myscalefactor, 0), size=(242 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=service))
                res.append(MultiContentEntryText(pos=(734 // myscalefactor, 0), size=(270 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=slyk_date_time_string))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(1013 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=data.icon))
                res.append(MultiContentEntryText(pos=(1058 // myscalefactor, 0), size=(165 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.viewed))
            else:
                if data.part is not None and data.part > 0:
                    res.append(MultiContentEntryProgress(pos=(1230 // myscalefactor, ih // 2 - 3), size=(90 // myscalefactor, 9 // myscalefactor), percent=data.part, borderWidth=1, foreColor=0x006fce, foreColorSelected=0xffffff, backColor=0x000000, backColorSelected=None))
                    res.append(MultiContentEntryText(pos=(1058 // myscalefactor, 0), size=(165 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.viewed))
                else:
                    data.viewed = 'Downloaded'
                    res.append(MultiContentEntryText(pos=(1058 // myscalefactor, 0), size=(165 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.viewed))
                res.append(MultiContentEntryText(pos=(15 // myscalefactor, 0), size=(447 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(1013 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=self.iconDownloaded))
                res.append(MultiContentEntryText(pos=(734 // myscalefactor, 0), size=(270 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=slyk_date_time_string))
            return res

        # vskin planner
        if ext == '6':
            if fileExtension in RECORD_EXTENSIONS:
                if data.part is not None and data.part > 0:
                    res.append(MultiContentEntryProgress(pos=(776 // myscalefactor, ih // 2 - 3), size=(98 // myscalefactor, 9 // myscalefactor), percent=data.part, borderWidth=1, foreColor=0xffffff, foreColorSelected=0xffffff, backColor=0x14020e, backColorSelected=None))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(15 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=data.icon))
                res.append(MultiContentEntryText(pos=(68 // myscalefactor, 0), size=(405 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
                res.append(MultiContentEntryText(pos=(486 // myscalefactor, 0), size=(257 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=service))
                res.append(MultiContentEntryText(pos=(923 // myscalefactor, 0), size=(75 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=vskin_date_day))
                res.append(MultiContentEntryText(pos=(983 // myscalefactor, 0), size=(90 // myscalefactor, ih), font=0, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=vskin_date_date))
                res.append(MultiContentEntryText(pos=(1073 // myscalefactor, 0), size=(83 // myscalefactor, ih), font=0, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=vskin_date_time))
            else:
                if data.part is not None and data.part > 0:
                    res.append(MultiContentEntryProgress(pos=(776 // myscalefactor, ih // 2 - 3), size=(98 // myscalefactor, 9 // myscalefactor), percent=data.part, borderWidth=1, foreColor=0xffffff, foreColorSelected=0xffffff, backColor=0x14020e, backColorSelected=None))
                else:
                    data.viewed = 'Downloaded'
                res.append(MultiContentEntryText(pos=(68 // myscalefactor // myscalefactor, 0), size=(405 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(15 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=self.iconDownloaded))
                res.append(MultiContentEntryText(pos=(923 // myscalefactor, 0), size=(75 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=vskin_date_day))
                res.append(MultiContentEntryText(pos=(983 // myscalefactor, 0), size=(90 // myscalefactor, ih), font=0, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=vskin_date_date))
                res.append(MultiContentEntryText(pos=(1073 // myscalefactor, 0), size=(83 // myscalefactor, ih), font=0, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=vskin_date_time))
            return res

    # ############################################### #
    return res
