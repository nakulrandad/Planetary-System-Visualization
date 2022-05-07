import numpy as np


class Constants:
    G = 6.67*(10**-11)
    AU_DIST = 1.496*(10**11)
    DEG_TO_RAD = np.pi/180
    DAY_TO_SEC = 3600*24
    MASS_SUN = 1.99*(10**30)


class PlanetData:
    MERCURY_DATA = {
        'Mass': 10,
        'Semi Major Axis': 0.387,
        'Orbit Inclination': 7,
        'Orbit Eccentricity': 0.2,
        'Angle-Intr_pl': 10,
        'Angle-maj_ax_pp': 0,
        'Initial Theta': 0
    }
    VENUS_DATA = {
        'Mass': 10,
        'Semi Major Axis': 0.723,
        'Orbit Inclination': 3.39,
        'Orbit Eccentricity': 0.007,
        'Angle-Intr_pl': 0,
        'Angle-maj_ax_pp': 0,
        'Initial Theta': 0
    }
    EARTH_DATA = {
        'Mass': 10,
        'Semi Major Axis': 1,
        'Orbit Inclination': 0,
        'Orbit Eccentricity': 0.017,
        'Angle-Intr_pl': 0,
        'Angle-maj_ax_pp': 0,
        'Initial Theta': 0
    }
    MARS_DATA = {
        'Mass': 10,
        'Semi Major Axis': 1.527,
        'Orbit Inclination': 1.85,
        'Orbit Eccentricity': 0.093,
        'Angle-Intr_pl': 0,
        'Angle-maj_ax_pp': 0,
        'Initial Theta': 0
    }
    JUPITER_DATA = {
        'Mass': 10,
        'Semi Major Axis': 5.2,
        'Orbit Inclination': 1.31,
        'Orbit Eccentricity': 0.048,
        'Angle-Intr_pl': 0,
        'Angle-maj_ax_pp': 0,
        'Initial Theta': 0
    }
    SATURN_DATA = {
        'Mass': 10,
        'Semi Major Axis': 9.54,
        'Orbit Inclination': 2.49,
        'Orbit Eccentricity': 0.056,
        'Angle-Intr_pl': 0,
        'Angle-maj_ax_pp': 0,
        'Initial Theta': 0
    }
    URANUS_DATA = {
        'Mass': 10,
        'Semi Major Axis': 19.19,
        'Orbit Inclination': 0.77,
        'Orbit Eccentricity': 0.046,
        'Angle-Intr_pl': 0,
        'Angle-maj_ax_pp': 0,
        'Initial Theta': 0
    }
    NEPTUNE_DATA = {
        'Mass': 10,
        'Semi Major Axis': 30.06,
        'Orbit Inclination': 1.77,
        'Orbit Eccentricity': 0.01,
        'Angle-Intr_pl': 0,
        'Angle-maj_ax_pp': 0,
        'Initial Theta': 0
    }
