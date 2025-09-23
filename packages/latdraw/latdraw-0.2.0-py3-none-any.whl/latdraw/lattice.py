import logging
from collections.abc import Sequence

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

MAGNET_WIDTH = 0.1

# DEFAULT_COLOUR_MAP = Quadrupole

# If this was actually good: the survey would be generated AUTOMATICALLY from
# the beam angles and tilts! And some offset (with angle) would just belong to
# the beamline! instance. And could maybe even support different visualistion
# backends 🤔.

# Actually to get rotations to work properly, this is more or less necessary,
# because otherwise I have no way of knowing the orientation of a given element
# in XYZ space (survey) without inspecting surrounding elements. So could also
# just be an interface change, without so much work, but i think a
# "beamline.getRotation(element)" etc approach would be the best approach.


class Beamline(Sequence):
    def __init__(self, items):
        self._sequence = list(items)

    def __getitem__(self, key):
        return self._sequence[key]

    def __len__(self):
        return len(self._sequence)

    def survey(self):
        initial_offset = np.array([0, 0, 0]).reshape(3, 1)
        initial_rotation = np.identity(3)

        global_rotations = [initial_rotation]
        global_placements = [initial_offset]

        for element in self:
            local_displacement = element.displacement()
            local_rotation = element.rotation()

            # W_{i-1} in MADX manual
            previous_rotation = global_rotations[-1]
            previous_placement = global_placements[-1]

            # V_i in MADX manual
            global_placement = (
                previous_rotation @ local_displacement + previous_placement
            )
            global_rotation = previous_rotation @ local_rotation

            global_placements.append(global_placement)
            global_rotations.append(global_rotation)

        global_placements = np.hstack(global_placements)
        x, y, z = global_placements[..., 1:]

        active = [x.is_active() for x in self]
        length = [x.length for x in self]

        theta, _, _ = rotation_matrices_to_madx_rotations(global_rotations[1:])
        xlocal, ylocal, zlocal = rotation_matrices_to_local_axis(global_rotations[1:])

        df = pd.DataFrame.from_dict(
            {
                "name": self.name(),
                "keyword": self.keyword(),
                "x": x,
                "y": y,
                "z": z,
                "xlocal": xlocal,
                "ylocal": ylocal,
                "zlocal": zlocal,
                "s": self.s(),
                "theta": theta,
                "length": length,
                "active": active,
                "e1": self._get_attr_or_zero("e1"),
                "e2": self._get_attr_or_zero("e2"),
                "k1": self._get_attr_or_zero("k1"),
                "angle": self._get_attr_or_zero("angle"),
            }
        )

        return df

    def _get_attr_or_zero(self, attr_name):
        result = []
        for x in self:
            try:
                result.append(getattr(x, attr_name))
            except AttributeError:
                result.append(0.0)
        return result

    def keyword(self):
        return [type(element).__name__ for element in self]

    def name(self):
        return [element.name for element in self]

    def s(self):
        return np.cumsum([element.length for element in self])


def rotation_matrices_to_madx_rotations(matrices):
    thetas = []
    unit_z = [0, 0, 1]
    # import ipdb; ipdb.set_trace()
    for matrix in matrices:
        # New direction, starting from pointing along global z:
        # vec = matrix @ unit_z
        new_z = matrix[:, 2]
        # Project the new z onto the x-z plane
        new_z[1] = 0.0

        theta = np.arccos(np.dot(unit_z, new_z) / np.linalg.norm(new_z))
        thetas.append(theta)

    return thetas, [], []


def rotation_matrices_to_local_axis(matrices):
    x = []
    y = []
    z = []
    for matrix in matrices:
        # Third column is new z axis (i.e. comoving s)
        new_x = matrix[:, 0]
        new_y = matrix[:, 1]
        new_z = matrix[:, 2]

        x.append(new_x)
        y.append(new_y)
        z.append(new_z)

    return x, y, z


class StraightElementMixIn:
    def displacement(self):
        return np.array([0, 0, self.length]).reshape(3, 1)

    def rotation(self):
        return np.identity(3)


class Element:
    def __init__(self, name: str, length, **misc):
        """For now position is the END?  survey and S can be dengerate, x and y
        just stay 0...

        """
        self.name = name
        # self.position = np.array(position)
        self.length = length
        self.misc = misc
        # self.tilt = 0

    def __repr__(self):
        typename = type(self).__name__
        rstr = f"<{typename}: name={self.name}, l={self.length}"
        if self.misc:
            rstr += ", " + repr(self.misc)
        rstr += ">"
        return rstr

    def __str__(self):
        return f"{type(self).__name__}: {self.name}"

    def is_active(self):
        return True

    # def tilt_matrix()


class ThinElement(Element, StraightElementMixIn):
    def __init__(self, name: str, **misc):
        super().__init__(name, 0.0, **misc)

    def is_active(self):
        return True

    def __repr__(self):
        typename = type(self).__name__
        return f"<{typename}: name={self.name}>"


class Marker(ThinElement):
    pass


class Monitor(ThinElement):
    pass


class Drift(Element, StraightElementMixIn):
    pass


class SimpleDipole(Element):
    def __init__(self, name: str, length, angle, **misc):
        super().__init__(name, length, **misc)
        self.angle = angle

    def is_active(self):
        return self.angle != 0

    def displacement(self):
        if self.angle == 0:
            res = np.array([0, 0, self.length])
        else:
            res = np.array(
                [self.rho * (np.cos(self.angle) - 1), 0, self.rho * np.sin(self.angle)]
            )

        return res.reshape(3, 1)

    def rotation(self):
        return np.array(
            [
                [np.cos(self.angle), 0, -np.sin(self.angle)],
                [0, 1, 0],
                [np.sin(self.angle), 0, np.cos(self.angle)],
            ]
        )

    def __repr__(self):
        typename = type(self).__name__
        return f"<{typename}: name={self.name}, l={self.length}, angle={self.angle}>"


class RBend(SimpleDipole):
    @property
    def rho(self):
        "Using the MAD8/X definition here..."
        return self.length / (2 * np.sin(self.angle / 2))

    def is_square(self):
        return (self.e1 == 0) and (self.e2 == 0)


class SBend(SimpleDipole):
    @property
    def rho(self):
        "Using the MAD8/X definition here..."
        return self.length / self.angle

    def is_square(self):
        return (self.e1 == self.angle / 2) and (self.e2 == self.angle / 2)


class HKicker(SimpleDipole, StraightElementMixIn):
    pass


class VKicker(SimpleDipole, StraightElementMixIn):
    pass


class Kicker(SimpleDipole, StraightElementMixIn):
    pass


class Quadrupole(Element, StraightElementMixIn):
    def __init__(self, name: str, length, k1, **misc):
        super().__init__(name, length, **misc)
        self.k1 = k1

    def is_active(self):
        return self.k1 != 0

    def __str__(self):
        l = self.length
        k1 = self.k1
        k1l = l * k1
        return f"<Quad: {self.name}, {l=}, {k1=}, {k1l=}>"

    def polarity(self):
        return np.sign(self.k1)


class Sextupole(Element, StraightElementMixIn):
    def __init__(self, name: str, length, k2, **misc):
        super().__init__(name, length, **misc)
        self.k2 = k2

    def is_active(self):
        return self.k2 != 0


class Octupole(Element, StraightElementMixIn):
    def __init__(self, name: str, length: float, k3: float, **misc):
        super().__init__(name, length, **misc)
        self.k3 = k3

    def is_active(self):
        return self.k3 != 0


class RFCavity(Element, StraightElementMixIn):
    def __init__(self, name: str, length: float, voltage: float, phase: float, **misc):
        super().__init__(name, length, **misc)
        self.voltage = voltage
        self.phase = phase

    def is_active(self):
        return self.voltage != 0


class Solenoid(Element, StraightElementMixIn):
    def __init__(self, name: str, length, ks, **misc):
        super().__init__(name, length, **misc)
        self.ks = ks

    def is_active(self):
        return self.ks != 0


class Collimator(Element, StraightElementMixIn):
    pass


class Cavity(Element):
    pass


class GenericMap(Element, StraightElementMixIn):
    pass


class TransverseDeflectingCavity(Element, StraightElementMixIn):
    def __init__(self, name: str, length, voltage, **misc):
        super().__init__(name, length, **misc)
        self.voltage = voltage

    def is_active(self):
        return self.voltage != 0


class Undulator(Element, StraightElementMixIn):
    def __init__(self, name: str, length, kx=0.0, ky=0.0, **misc):
        super().__init__(name, length, **misc)
        self.kx = kx
        self.ky = ky

    def is_active(self):
        return self.kx != 0 or self.ky != 0
