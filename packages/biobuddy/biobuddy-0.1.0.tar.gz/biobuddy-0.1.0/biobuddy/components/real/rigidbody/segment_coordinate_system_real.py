from copy import deepcopy

# from typing import Self

import numpy as np

from .axis_real import AxisReal
from .marker_real import MarkerReal
from ....utils.aliases import Point, Points
from ....utils.linear_algebra import RotoTransMatrix, RotoTransMatrixTimeSeries, get_closest_rt_matrix


class SegmentCoordinateSystemReal:
    def __init__(
        self,
        scs: RotoTransMatrix = RotoTransMatrix(),
        is_scs_local: bool = False,
    ):
        """
        Parameters
        ----------
        scs
            The scs of the SegmentCoordinateSystemReal
        is_scs_local
            If the scs is already in local reference frame
        """
        self.scs = scs
        self.is_in_global = not is_scs_local

    @property
    def scs(self) -> RotoTransMatrix:
        return self._scs

    @scs.setter
    def scs(self, value: RotoTransMatrix):
        self._scs = value

    @property
    def is_in_global(self) -> bool:
        return self._is_in_global

    @is_in_global.setter
    def is_in_global(self, value: bool):
        self._is_in_global = value

    @property
    def is_in_local(self) -> bool:
        return not self._is_in_global

    @is_in_local.setter
    def is_in_local(self, value: bool):
        self._is_in_global = not value

    @staticmethod
    def from_rt_matrix(
        rt_matrix: np.ndarray,
        is_scs_local: bool = False,
    ) -> "SegmentCoordinateSystemReal":
        """
        Construct a SegmentCoordinateSystemReal from angles and translations

        Parameters
        ----------
        rt_matrix: np.ndarray
            The RT matrix
        is_scs_local
            If the scs is already in local reference frame
        """
        scs = RotoTransMatrix()
        scs.from_rt_matrix(rt_matrix)
        return SegmentCoordinateSystemReal(scs=scs, is_scs_local=is_scs_local)

    @staticmethod
    def from_euler_and_translation(
        angles: Points,
        angle_sequence: str,
        translation: Point,
        is_scs_local: bool = False,
    ) -> "SegmentCoordinateSystemReal":
        """
        Construct a SegmentCoordinateSystemReal from angles and translations

        Parameters
        ----------
        angles
            The actual angles
        angle_sequence
            The angle sequence of the angles
        translations
            The XYZ translations
        is_scs_local
            If the scs is already in local reference frame
        """
        scs = RotoTransMatrix()
        scs.from_euler_angles_and_translation(angles=angles, angle_sequence=angle_sequence, translation=translation)
        return SegmentCoordinateSystemReal(scs=scs, is_scs_local=is_scs_local)

    @property
    def inverse(self) -> "Self":
        out = deepcopy(self)
        out.scs = out.scs.inverse
        return out

    def to_biomod(self):

        out_string = ""
        closest_rt = get_closest_rt_matrix(self.scs.rt_matrix)
        out_string += f"\tRTinMatrix	1\n"
        out_string += f"\tRT\n"
        out_string += (
            f"\t\t{closest_rt[0, 0]:0.6f}\t{closest_rt[0, 1]:0.6f}\t{closest_rt[0, 2]:0.6f}\t{closest_rt[0, 3]:0.6f}\n"
        )
        out_string += (
            f"\t\t{closest_rt[1, 0]:0.6f}\t{closest_rt[1, 1]:0.6f}\t{closest_rt[1, 2]:0.6f}\t{closest_rt[1, 3]:0.6f}\n"
        )
        out_string += (
            f"\t\t{closest_rt[2, 0]:0.6f}\t{closest_rt[2, 1]:0.6f}\t{closest_rt[2, 2]:0.6f}\t{closest_rt[2, 3]:0.6f}\n"
        )
        out_string += (
            f"\t\t{closest_rt[3, 0]:0.6f}\t{closest_rt[3, 1]:0.6f}\t{closest_rt[3, 2]:0.6f}\t{closest_rt[3, 3]:0.6f}\n"
        )

        return out_string
