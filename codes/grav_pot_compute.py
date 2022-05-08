import numpy as np
from planets_data import Constants, PlanetData
from planet_compute import Planet, Planets


def compute_grav_pot(pos, planets, thresh=100):
    pos *= Constants.AU_DIST
    if planets.planets_curr_pos.shape == (0,):
        source_pos_arr = np.array([[0, 0, 0]]).reshape(1, 3)
    else:
        source_pos_arr = np.concatenate(
            [planets.planets_curr_pos, np.array([[0, 0, 0]]).reshape(1, 3)])
    r = np.linalg.norm(pos-source_pos_arr)+0.01
    mass_arr = np.array([i.mass for i in planets.planets] +
                        [Constants.MASS_SUN])
    grav_pot = -Constants.G*mass_arr/r
    grav_pot = (np.abs(grav_pot) >
                thresh)*thresh + (np.abs(grav_pot) < thresh)*grav_pot
    return np.sum(grav_pot)


if __name__ == '__main__':
    pl = Planet('earth', 6*(10**24), init_theta=5)
    pl2 = Planet('merc', 6*(10**23), orb_incl=5, orb_ecc=0.2,
                 intr_pl_ang=45, maj_ang_pp=10, init_theta=5)
    plts = Planets()
    # plts.add_planet(pl)
    # plts.add_planet(pl2)
    print(compute_grav_pot(np.array([0, 1, 0])*Constants.AU_DIST, plts, 100))
