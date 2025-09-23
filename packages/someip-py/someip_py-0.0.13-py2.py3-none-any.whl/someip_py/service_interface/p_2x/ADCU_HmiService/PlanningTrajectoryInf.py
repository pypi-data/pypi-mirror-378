from someip_py.codec import *


class PathPoint(SomeIpPayload):

    PositionXSeN: Int32

    PositionYSeN: Int32

    ParkingLinePointTheta: Int32

    def __init__(self):

        self.PositionXSeN = Int32()

        self.PositionYSeN = Int32()

        self.ParkingLinePointTheta = Int32()


class PlanningTrajectoryKls(SomeIpPayload):
    _has_dynamic_size = True

    PathPointsSeN: SomeIpDynamicSizeArray[PathPoint]

    ParkInTrajDistanceSeN: Uint16

    ParkInTrajReDistanceSeN: Uint16

    StoppointSeN: SomeIpDynamicSizeArray[PathPoint]

    DeccelerationDisplaySeN: Uint8

    def __init__(self):

        self.PathPointsSeN = SomeIpDynamicSizeArray(PathPoint)

        self.ParkInTrajDistanceSeN = Uint16()

        self.ParkInTrajReDistanceSeN = Uint16()

        self.StoppointSeN = SomeIpDynamicSizeArray(PathPoint)

        self.DeccelerationDisplaySeN = Uint8()


class PlanningTrajectory(SomeIpPayload):

    PlanningTrajectory: PlanningTrajectoryKls

    def __init__(self):

        self.PlanningTrajectory = PlanningTrajectoryKls()
