#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ============================================================================
"""
Description: Consists of planet class and planet data.
"""
# ============================================================================

import numpy as np
from planets_data import Constants, PlanetData

def get_rotation_matrix(theta, axis='z'):
    if axis == 'x':
        return np.array([[1, 0, 0], [0, np.cos(theta), -np.sin(theta)], [0, np.sin(theta), np.cos(theta)]])
    if axis == 'y':
        return np.array([[np.cos(theta), 0, np.sin(theta)], [0, 1, 0], [-np.sin(theta), 0, np.cos(theta)]])
    if axis == 'z':
        return np.array([[np.cos(theta), -np.sin(theta), 0], [np.sin(theta), np.cos(theta), 0], [0, 0, 1]])

class Planet:
    def __init__(self, name, mass, sem_maj_ax=1, orb_incl=0, orb_ecc=0, intr_pl_ang=0, maj_ang_pp=0, init_theta=0):
        self.name = name
        self.mass = mass
        
        self.add_orbital_data(sem_maj_ax=sem_maj_ax, orb_incl=orb_incl, orb_ecc=orb_ecc, intr_pl_ang=intr_pl_ang, maj_ang_pp=maj_ang_pp, init_theta=init_theta)

    def add_orbital_data(self, sem_maj_ax=None, orb_incl=None, orb_ecc=None, intr_pl_ang=None, maj_ang_pp=None, init_theta=None):
        if sem_maj_ax!=None:
            self.sem_maj_ax = sem_maj_ax*Constants.AU_DIST
        if orb_incl!=None:
            self.orbit_inclination = orb_incl*Constants.DEG_TO_RAD
        if orb_ecc!=None:
            self.orbit_ecc = orb_ecc
        if intr_pl_ang!=None:
            self.plane_intersection_angle_with_maj_ax = intr_pl_ang*Constants.DEG_TO_RAD
        if maj_ang_pp!=None:
            self.major_axis_angle_in_planet_plane = maj_ang_pp*Constants.DEG_TO_RAD
        if init_theta!=None:
            self.init_theta=init_theta*Constants.DEG_TO_RAD

        self.compute_perh_aph()
        self.planet_plane_vector = self.compute_planet_plane_vector()

    def compute_perh_aph(self):
        self.perh = self.sem_maj_ax*(1-self.orbit_ecc)
        self.aph = self.sem_maj_ax*(1+self.orbit_ecc)

    def compute_planet_plane_vector(self):
        ppv = np.array([0,-np.sin(self.orbit_inclination), np.cos(self.orbit_inclination)])
        rot_mat_ang = self.plane_intersection_angle_with_maj_ax
        rot_mat = np.array([[np.cos(rot_mat_ang), -np.sin(rot_mat_ang), 0], [np.sin(rot_mat_ang), np.cos(rot_mat_ang), 0], [0, 0, 1]])
        ppv = np.matmul(rot_mat, ppv)
        return ppv


class Planets:
    def __init__(self, dt=10*Constants.DAY_TO_SEC, cent_mass=Constants.MASS_SUN):
        self.planets = []
        self.dt = dt
        self.center_mass = cent_mass
        self.planets_theta = np.array([])
        self.planets_sem_maj = np.array([])
        self.planets_ecc = np.array([])
        self.planets_perhs = np.array([])
        self.planets_aphs = np.array([])
        self.planets_curr_pos = np.array([])

    def calc_curr_pos_vector(self, planet_index):
        idx = planet_index
        rot_z_1 = get_rotation_matrix(self.planets_theta[idx] + self.planets[idx].major_axis_angle_in_planet_plane)
        rot_x_1 = get_rotation_matrix(self.planets[idx].orbit_inclination, axis='x')
        rot_z_2 = get_rotation_matrix(self.planets[idx].plane_intersection_angle_with_maj_ax)
        pos_vector = np.matmul(rot_z_2, np.matmul(rot_x_1, np.matmul(rot_z_1, np.array([1,0,0]))))
        pos_vector = pos_vector*self.planets_sem_maj[idx]*(1-self.planets_ecc[idx]*np.cos(self.planets_theta[idx]))
        return pos_vector.reshape([-1,3])

    def add_planet(self, planet=None):
        if planet!=None:
            if self.planets == []:
                self.planets.append(planet)
                self.planets_theta = np.array([planet.init_theta])
                self.planets_sem_maj = np.array([planet.sem_maj_ax])
                self.planets_ecc = np.array([planet.orbit_ecc])
                self.planets_perhs = np.array([planet.perh])
                self.planets_aphs = np.array([planet.aph])
                self.planets_curr_pos = self.calc_curr_pos_vector(-1)

            if planet not in self.planets:
                self.planets.append(planet)
                self.planets_theta = np.concatenate([self.planets_theta, np.array([planet.init_theta])])
                self.planets_sem_maj = np.concatenate([self.planets_sem_maj, np.array([planet.sem_maj_ax])])
                self.planets_ecc = np.concatenate([self.planets_ecc, np.array([planet.orbit_ecc])])
                self.planets_perhs = np.concatenate([self.planets_perhs, np.array([planet.perh])])
                self.planets_aphs = np.concatenate([self.planets_aphs, np.array([planet.aph])])
                self.planets_curr_pos = np.concatenate([self.planets_curr_pos, self.calc_curr_pos_vector(-1)])

            self.P = (2*np.pi/((Constants.G*self.center_mass)**0.5))*(self.planets_sem_maj**1.5)
            ar_vel = (np.pi*self.dt/2)*((1-self.planets_ecc**2)**0.5)*(1/self.P)
            self.dth_min = ar_vel*(1/(1-self.planets_ecc)**2)
            self.dth_max = ar_vel*(1/(1+self.planets_ecc)**2)

    def update_curr_pos(self, planet_index):
        self.planets_curr_pos[planet_index] = self.calc_curr_pos_vector(planet_index)

    def update_theta(self):
        self.dtheta = (self.dth_min + ((self.dth_max-self.dth_min)/np.pi)*np.abs(np.pi-self.planets_theta))
        print('dtheta', self.dtheta)
        self.planets_theta = self.planets_theta + self.dtheta

    def update(self):
        self.update_theta()
        for i in range(len(self.planets)):
            self.update_curr_pos(i)

    def update_and_fetch_pos(self, units='AU', update=True):
        if self.update:
            self.update()
        if units=='AU':
            conv_factor = 1/Constants.AU_DIST
        curr_pos = self.planets_curr_pos*conv_factor
        return {self.planets[i].name : curr_pos[i] for i in range(len(self.planets))}
        


if __name__=='__main__':
    pl = Planet('earth', 6*(10**24), init_theta=5)
    pl2 = Planet('merc', 6*(10**23), orb_incl=5, orb_ecc=0.2, intr_pl_ang=45, maj_ang_pp=10, init_theta=5)
    plts = Planets()
    plts.add_planet(pl)
    print(plts.planets_curr_pos)
    plts.add_planet(pl2)
    print(plts.planets_curr_pos)
    print(plts.dth_max, plts.dth_min, plts.P)
    plts.update()
    print(plts.planets_curr_pos)

