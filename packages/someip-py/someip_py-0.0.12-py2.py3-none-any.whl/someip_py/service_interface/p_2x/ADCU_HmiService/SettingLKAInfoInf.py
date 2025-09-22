from someip_py.codec import *


class SettingLKAInfoKls(SomeIpPayload):

    LDWSettingSeN: Uint8

    LDPSwitchSeN: Uint8

    ELKASwitch: Uint8

    LDWSwitch: Uint8

    LSSSettingSeN: Uint8

    LDPTypeSeN: Uint8

    def __init__(self):

        self.LDWSettingSeN = Uint8()

        self.LDPSwitchSeN = Uint8()

        self.ELKASwitch = Uint8()

        self.LDWSwitch = Uint8()

        self.LSSSettingSeN = Uint8()

        self.LDPTypeSeN = Uint8()


class SettingLKAInfo(SomeIpPayload):

    SettingLKAInfo: SettingLKAInfoKls

    def __init__(self):

        self.SettingLKAInfo = SettingLKAInfoKls()
