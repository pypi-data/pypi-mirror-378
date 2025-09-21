from someip_py.codec import *


class VehiclePoint(SomeIpPayload):

    PositionXSeN: Int32

    PositionYSeN: Int32

    def __init__(self):

        self.PositionXSeN = Int32()

        self.PositionYSeN = Int32()


class CustomParkingKls(SomeIpPayload):
    _has_dynamic_size = True

    ParkingTypeSeN: Uint8

    APAImagePointSeN: SomeIpDynamicSizeArray[VehiclePoint]

    CustomParkFlag: Uint8

    ApaCustomParkVehDirStsSeN: Uint8

    def __init__(self):

        self.ParkingTypeSeN = Uint8()

        self.APAImagePointSeN = SomeIpDynamicSizeArray(VehiclePoint)

        self.CustomParkFlag = Uint8()

        self.ApaCustomParkVehDirStsSeN = Uint8()


class CustomParking(SomeIpPayload):

    CustomParking: CustomParkingKls

    def __init__(self):

        self.CustomParking = CustomParkingKls()


class IdtRet(SomeIpPayload):

    IdtRet: Uint8

    def __init__(self):

        self.IdtRet = Uint8()
