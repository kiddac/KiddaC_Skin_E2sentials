#!/usr/bin/python
# -*- coding: utf-8 -*-

# for localized messages
from . import _

from Components.config import config
from enigma import iServiceInformation, eSize, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_CENTER, eServiceReference, eServiceCenter, BT_SCALE, BT_KEEP_ASPECT_RATIO
from datetime import datetime
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend, MultiContentEntryProgress
from Tools.TextBoundary import getTextBoundarySize
from ServiceReference import ServiceReference
from Tools.FuzzyDate import FuzzyTime

from Components.MovieList import MovieListData, moviePlayState
try:
    from Components.MovieList import RECORD_EXTENSIONS
except:
    RECORD_EXTENSIONS = (".ts")

import os


def openatvSetItemsPerPage(self):
    if self.listHeight > 0:
        ext = config.movielist.useextlist.value
        if ext == '1' or ext == '2':
            itemHeight = (self.listHeight // config.movielist.itemsperpage.value) * 2
        else:
            itemHeight = self.listHeight // config.movielist.itemsperpage.value
    else:
        itemHeight = 30  # some default (270/5)
    self.itemHeight = itemHeight
    self.l.setItemHeight(itemHeight)
    self.instance.resize(eSize(self.listWidth, self.listHeight // itemHeight * itemHeight))


def openatvBuildMovieListEntry(self, serviceref, info, begin, data):
    switch = config.usage.show_icons_in_movielist.value
    ext = config.movielist.useextlist.value

    width = self.l.getItemSize().width()
    pathName = serviceref.getPath()
    res = [None]

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

    textPosX = listBeginX + dataIconSize + listMarginX

    if serviceref.flags & eServiceReference.mustDescent:
        # Directory
        iconSize = pathIconSize
        iconPosX = listBeginX - 1
        iconPosY = ih // 2 - iconSize // 2

        trashIconPosY = ih // 2 - trashIconSizeH // 2
        folderIconPosY = ih // 2 - folderIconSizeH // 2
        if iconPosY < iconPosX:
            iconPosY = iconPosX
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
            if txt == ".Trash":
                if ext == "0":
                    dateSize = getTextBoundarySize(self.instance, self.dateFont, self.l.getItemSize(), _("Trashcan")).width()
                    res.append(MultiContentEntryPixmapAlphaBlend(pos=(iconPosX, iconPosY), size=(iconSize, iconSize), png=self.iconTrash, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
                    res.append(MultiContentEntryText(pos=(textPosX, 0), size=(width - textPosX - dateSize - listMarginX - listEndX, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Deleted items")))
                    res.append(MultiContentEntryText(pos=(width - dateSize - listEndX, textPosY), size=(dateSize, self.itemHeight), font=1, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=_("Trashcan")))
                else:
                    if ext == "3":
                        res.append(MultiContentEntryText(pos=(12 // myscalefactor, 0), size=(573 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Deleted items")))
                        res.append(MultiContentEntryPixmapAlphaBlend(pos=(629 // myscalefactor, trashIconPosY), size=(trashIconSizeW, trashIconSizeH), png=self.iconTrash, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
                        res.append(MultiContentEntryText(pos=(705 // myscalefactor, 0), size=(327 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Trashcan")))

                    if ext == "4":
                        res.append(MultiContentEntryText(pos=(12 // myscalefactor, 0), size=(483 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Deleted items")))
                        res.append(MultiContentEntryPixmapAlphaBlend(pos=(510 // myscalefactor, trashIconPosY), size=(trashIconSizeW, trashIconSizeH), png=self.iconTrash, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
                        res.append(MultiContentEntryText(pos=(561 // myscalefactor, 0), size=(150 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Trashcan")))

                    if ext == "5" or ext == "6":
                        res.append(MultiContentEntryPixmapAlphaBlend(pos=(15 // myscalefactor, trashIconPosY), size=(trashIconSizeW, trashIconSizeH), png=self.iconTrash, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
                        res.append(MultiContentEntryText(pos=(68 // myscalefactor, 0), size=(705 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Deleted Recordings")))

                return res

        if ext == "0":
            dateSize = getTextBoundarySize(self.instance, self.dateFont, self.l.getItemSize(), _("Directory")).width()
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(iconPosX, iconPosY), size=(iconSize, iconSize), png=self.iconFolder, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
            res.append(MultiContentEntryText(pos=(textPosX, 0), size=(width - textPosX - dateSize - listMarginX - listEndX, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=txt))
            res.append(MultiContentEntryText(pos=(width - dateSize - listEndX, textPosY), size=(dateSize, self.itemHeight), font=1, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=_("Directory")))
        else:
            if ext == "3":
                res.append(MultiContentEntryText(pos=(12 // myscalefactor, 0), size=(573 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=txt))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(629 // myscalefactor, folderIconPosY), size=(folderIconSizeW, folderIconSizeH), png=self.iconSeries, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
                res.append(MultiContentEntryText(pos=(705 // myscalefactor, 0), size=(327 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Directory")))

            if ext == "4":
                res.append(MultiContentEntryText(pos=(12 // myscalefactor, 0), size=(483 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=txt))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(510 // myscalefactor, folderIconPosY), size=(folderIconSizeW, folderIconSizeH), png=self.iconSeries, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
                res.append(MultiContentEntryText(pos=(561 // myscalefactor, 0), size=(150 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=_("Directory")))

            if ext == "5" or ext == "6":
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(15 // myscalefactor, folderIconPosY), size=(folderIconSizeW, folderIconSizeH), png=self.iconFolder, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
                res.append(MultiContentEntryText(pos=(68 // myscalefactor, 0), size=(705 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=txt))

        return res

    if (data == -1) or (data is None):
        data = MovieListData()
        cur_idx = self.l.getCurrentSelectionIndex()
        x = self.list[cur_idx]  # x = ref,info,begin,...
        data.len = 0  # dont recalc movielist to speedup loading the list
        self.list[cur_idx] = (x[0], x[1], x[2], data)  # update entry in list... so next time we don't need to recalc
        data.txt = info.getName(serviceref)
        data.icon = None
        data.part = None
        data.viewed = None
        if os.path.split(pathName)[1] in self.runningTimers:
            if switch == 'i':
                if (self.playInBackground or self.playInForeground) and serviceref == (self.playInBackground or self.playInForeground):
                    data.icon = self.iconMoviePlayRec
                else:
                    data.icon = self.iconMovieRec
                data.viewed = 'Recording'
            elif switch == 'p' or switch == 's':
                data.part = 100
                if (self.playInBackground or self.playInForeground) and serviceref == (self.playInBackground or self.playInForeground):

                    data.partcol = 0xffc71d
                else:
                    data.partcol = 0xff001d
        elif (self.playInBackground or self.playInForeground) and serviceref == (self.playInBackground or self.playInForeground):
            data.icon = self.iconMoviePlay
            data.viewed = 'Playing'
        else:
            data.part = moviePlayState(pathName + '.cuts', serviceref, data.len)
            if switch == 'i':
                if data.part is not None and data.part > 0:
                    data.icon = self.iconPart[data.part // 25]
                    data.viewed = 'Viewed'
                else:
                    if config.usage.movielist_unseen.value:
                        data.icon = self.iconUnwatched
                        data.viewed = 'Recorded'
            elif switch == 'p' or switch == 's':
                if data.part is not None and data.part > 0:
                    data.partcol = 0xffc71d
                else:
                    if config.usage.movielist_unseen.value:
                        data.part = 100
                        data.partcol = 0x206333

    len = data.len
    if len > 0:
        len = "%d:%02d" % (len // 60, len % 60)
    else:
        len = ""

    iconSize = 0

    if ext == "0":
        if switch == 'i':
            iconSize = dataIconSize
            iconPosX = listBeginX
            iconPosY = ih // 2 - iconSize // 2
            if iconPosY < iconPosX:
                iconPosY = iconPosX
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(iconPosX, iconPosY), size=(iconSize, iconSize), png=data.icon, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
        elif switch == 'p':
            if data.part is not None and data.part > 0:
                iconSize = progressBarSize
                iconPosX = listBeginX
                iconPosY = ih // 2 - iconSize // 8
                if iconPosY < iconPosX:
                    iconPosY = iconPosX
                res.append(MultiContentEntryProgress(pos=(iconPosX, iconPosY), size=(iconSize, iconSize // 4), percent=data.part, borderWidth=2, foreColor=data.partcol, foreColorSelected=None, backColor=None, backColorSelected=None))
            else:
                iconSize = dataIconSize
                iconPosX = listBeginX
                iconPosY = ih // 2 - iconSize // 2
                if iconPosY < iconPosX:
                    iconPosY = iconPosX
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(iconPosX, iconPosY), size=(iconSize, iconSize), png=data.icon, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
        elif switch == 's':
            iconSize = progressIconSize
            iconPosX = listBeginX
            iconPosY = ih // 2 - iconSize // 2
            if iconPosY < iconPosX:
                iconPosY = iconPosX
            if data.part is not None and data.part > 0:
                res.append(MultiContentEntryProgress(pos=(iconPosX, iconPosY), size=(iconSize, iconSize), percent=data.part, borderWidth=2, foreColor=data.partcol, foreColorSelected=None, backColor=None, backColorSelected=None))
            else:
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(iconPosX, iconPosY), size=(iconSize, iconSize), png=data.icon, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))

    begin_string = ""
    if begin > 0:
        begin_string = ', '.join(FuzzyTime(begin, inPast=True))
        d = datetime.fromtimestamp(begin)
        slyk_date_string = d.strftime("%a %d/%m")
        slyk_date_time_string = d.strftime("%a %d %b %H:%M")
        vskin_date_day = d.strftime("%a")
        vskin_date_date = d.strftime("%d/%m")
        vskin_date_time = d.strftime("%H:%M")
    dateSize = serviceSize = getTextBoundarySize(self.instance, self.dateFont, self.l.getItemSize(), begin_string).width()

    if iconSize:
        textPosX = listBeginX + iconSize + listMarginX
    else:
        textPosX = listBeginX

    if ext != '0':
        # getrec = info.getName(serviceref)
        getrec = serviceref.getPath()
        fileName, fileExtension = os.path.splitext(getrec)
        desc = None
        picon = None
        service = None
        try:
            serviceHandler = eServiceCenter.getInstance()
            info = serviceHandler.info(serviceref)
            desc = info.getInfoString(serviceref, iServiceInformation.sDescription)     # get description
            ref = info.getInfoString(serviceref, iServiceInformation.sServiceref)       # get reference
            service = ServiceReference(ref).getServiceName()                            # get service name
            serviceSize = getTextBoundarySize(self.instance, self.dateFont, self.l.getItemSize(), service).width()

        except Exception as e:
            print(('[MovieList] load extended infos get failed: ', e))

        if ext == '1' or ext == '2':
            if fileExtension in RECORD_EXTENSIONS:
                if ext == '1':
                    res.append(MultiContentEntryText(pos=(textPosX, 0), size=(width - textPosX - serviceSize - listMarginX - listEndX, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
                    res.append(MultiContentEntryText(pos=(width - serviceSize - listEndX, textPosY), size=(serviceSize, ih), font=1, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=service))

                if ext == '2':
                    piconSize = ih * 1.667
                    res.append(MultiContentEntryText(pos=(textPosX, 0), size=(width - textPosX - dateSize - listMarginX - listEndX, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
                    res.append(MultiContentEntryPixmapAlphaBlend(pos=(width - piconSize - listEndX, listEndX), size=(piconSize, ih), png=picon, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))

                res.append(MultiContentEntryText(pos=(listBeginX, ih + textPosY), size=(width - listBeginX - dateSize - listMarginX - listEndX, ih), font=1, flags=RT_HALIGN_LEFT, text=desc))
                res.append(MultiContentEntryText(pos=(width - dateSize - listEndX, ih + textPosY), size=(dateSize, ih), font=1, flags=RT_HALIGN_RIGHT, text=begin_string))
            else:
                res.append(MultiContentEntryText(pos=(textPosX, 0), size=(width - textPosX - dateSize - listMarginX - listEndX, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
                res.append(MultiContentEntryText(pos=(width - dateSize - listEndX, ih), size=(dateSize, ih), font=1, flags=RT_HALIGN_RIGHT, text=begin_string))
            return res

        # sky planner
        if ext == '3':
            if fileExtension in RECORD_EXTENSIONS:
                if data.part is not None and data.part > 0:
                    res.append(MultiContentEntryProgress(pos=(909 // myscalefactor, ih // 2 - 3), size=(123 // myscalefactor, 9 // myscalefactor), percent=data.part, borderWidth=1, foreColor=0x207be1, foreColorSelected=0x207be1, backColor=0x0b1e40, backColorSelected=None))
                res.append(MultiContentEntryText(pos=(12 // myscalefactor, 0), size=(573 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(629 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=data.icon, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
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
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(629 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=self.iconDownloaded, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
                res.append(MultiContentEntryText(pos=(1413 // myscalefactor, 0), size=(189 // myscalefactor, ih), font=1, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=slyk_date_string))
            return res

        # slyk q planner
        if ext == '4':
            if fileExtension in RECORD_EXTENSIONS:
                if data.part is not None and data.part > 0:
                    res.append(MultiContentEntryProgress(pos=(726 // myscalefactor, ih // 2 - 3), size=(123 // myscalefactor, 9 // myscalefactor), percent=data.part, borderWidth=1, foreColor=0x207be1, foreColorSelected=0x207be1, backColor=0x0b1e40, backColorSelected=None))
                res.append(MultiContentEntryText(pos=(12 // myscalefactor, 0), size=(483 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(510 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=data.icon, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
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
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(510 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=self.iconDownloaded, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
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
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(1013 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=data.icon, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
                res.append(MultiContentEntryText(pos=(1058 // myscalefactor, 0), size=(165 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.viewed))
            else:
                if data.part is not None and data.part > 0:
                    res.append(MultiContentEntryProgress(pos=(1230 // myscalefactor, ih // 2 - 3), size=(90 // myscalefactor, 9 // myscalefactor), percent=data.part, borderWidth=1, foreColor=0x006fce, foreColorSelected=0xffffff, backColor=0x000000, backColorSelected=None))
                    res.append(MultiContentEntryText(pos=(1058 // myscalefactor, 0), size=(165 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.viewed))
                else:
                    data.viewed = 'Downloaded'
                    res.append(MultiContentEntryText(pos=(1058 // myscalefactor, 0), size=(165 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.viewed))
                res.append(MultiContentEntryText(pos=(15 // myscalefactor, 0), size=(447 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(1013 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=self.iconDownloaded, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
                res.append(MultiContentEntryText(pos=(734 // myscalefactor, 0), size=(270 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=slyk_date_time_string))
            return res

        # vskin planner
        if ext == '6':
            if fileExtension in RECORD_EXTENSIONS:
                if data.part is not None and data.part > 0:
                    res.append(MultiContentEntryProgress(pos=(776 // myscalefactor, ih // 2 - 3), size=(98 // myscalefactor, 9 // myscalefactor), percent=data.part, borderWidth=1, foreColor=0xffffff, foreColorSelected=0xffffff, backColor=0x14020e, backColorSelected=None))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(15 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=data.icon, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
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
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(15 // myscalefactor, seenIconPosY), size=(seenIconSize, seenIconSize), png=self.iconDownloaded, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
                res.append(MultiContentEntryText(pos=(923 // myscalefactor, 0), size=(75 // myscalefactor, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=vskin_date_day))
                res.append(MultiContentEntryText(pos=(983 // myscalefactor, 0), size=(90 // myscalefactor, ih), font=0, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=vskin_date_date))
                res.append(MultiContentEntryText(pos=(1073 // myscalefactor, 0), size=(83 // myscalefactor, ih), font=0, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=vskin_date_time))
            return res

    else:
        res.append(MultiContentEntryText(pos=(textPosX, 0), size=(width - textPosX - dateSize - listMarginX - listEndX, ih), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=data.txt))
        res.append(MultiContentEntryText(pos=(width - dateSize - listEndX, textPosY), size=(dateSize, ih), font=1, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=begin_string))
        return res
