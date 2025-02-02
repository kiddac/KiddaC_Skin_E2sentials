# for localized messages

from .plugin import cfg

from enigma import eTimer, getDesktop
from Components.Label import Label
from Screens.Screen import Screen

myscreenname = None
screenwidth = getDesktop(0).size()
original_show = Screen.show


class ScreenNamesAutoMain:
    def __init__(self):
        self.mydialog = None

    def startScreenNames(self, session):
        if self.mydialog is None:
            self.mydialog = session.instantiateDialog(ScreenNamesAutoScreen)
            self.makeShow()

    def makeShow(self):
        if cfg.enablescreennamesmod.value:
            if Screen.show != myshow:
                Screen.show = myshow
            if self.mydialog:
                self.mydialog.show()
        else:
            if self.mydialog:
                self.mydialog.hide()


def myshow(self):
    if ScreenNamesAuto.mydialog:
        ScreenNamesAuto.mydialog.hide()

    original_show(self)
    print("[Screen] Showing screen '%s'." % self.skinName)  # To ease identification of screens.

    if (self.skinName != "RdsInfoDisplay"
        and self.skinName != "ScreenNamesAutoScreen"
        and "UnhandledKey" not in str(self.skinName)
        and "InfoBar" not in str(self.skinName)
        and "Summary" not in str(self.skinName)
            and "_summary" not in str(self.skinName)):
        global myscreenname
        myscreenname = str(self.skinName)
        ScreenNamesAuto.mydialog = None
        ScreenNamesAuto.startScreenNames(self.session)


ScreenNamesAuto = ScreenNamesAutoMain()


class ScreenNamesAutoScreen(Screen):
    if screenwidth.width() > 1280:
        skin = """<screen name="ScreenNamesAutoScreen" position="0,0" size="1920,50" title="ScreenNames Status" backgroundColor="#0b3663" flags="wfNoBorder" zPosition="100">
        <widget name="message_label" position="0,0" size="1920,50" font="Regular;24" backgroundColor="#0b3663" valign="center" halign="center" transparent="1" zPosition="101"/>
        </screen>"""
    else:
        skin = """<screen name="ScreenNamesAutoScreen" position="0,0" size="1280,50" title="ScreenNames Status" backgroundColor="#0b3663" flags="wfNoBorder" zPosition="100">
        <widget name="message_label" position="0,0" size="1280,32" font="Regular;16" backgroundColor="#0b3663" valign="center" halign="center" transparent="1" zPosition="101" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin = ScreenNamesAutoScreen.skin
        self['message_label'] = Label()

        self.ScreenNamesTimer = eTimer()
        try:
            self.ScreenNamesTimer_conn = self.ScreenNamesTimer.timeout.connect(self.__makeWhatYouNeed)
        except:
            self.ScreenNamesTimer.callback.append(self.__makeWhatYouNeed)

        self.state = None
        self.onLayoutFinish.append(self.__chckState)

    def __chckState(self):
        if self.instance:
            self.state = cfg.enablescreennamesmod.value
            if cfg.enablescreennamesmod.value and ScreenNamesAuto.mydialog is not None:
                ScreenNamesAuto.mydialog.show()
            self.ScreenNamesTimer.start(100, True)

    def __makeWhatYouNeed(self):
        if cfg.enablescreennamesmod.value:
            if self.instance:
                self['message_label'].setText(myscreenname)
