#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ============================================================================
"""
Description: Visualization of planetary data via GUI.

Author: Nakul Randad (https://github.com/nakulrandad)
"""
# ============================================================================
import time
import numpy as np
from matplotlib import pyplot as plt

from traits.api import Any, Array, HasTraits, Range, Float, observe, Instance, Button, HasStrictTraits, Str, Int, List
from traitsui.api import View, Item, Group, UndoButton, RevertButton, TableEditor, ObjectColumn, ExpressionColumn

from mayavi import mlab
from mayavi.core.api import PipelineBase
from mayavi.core.ui.api import MayaviScene, SceneEditor, MlabSceneModel

from planets_data import PlanetData, Constants
from planet_compute import Planets, Planet
from grav_pot_compute import compute_grav_pot


pl_map = {
    'mercury': PlanetData.MERCURY_DATA,
    'venus': PlanetData.VENUS_DATA,
    'earth': PlanetData.EARTH_DATA,
    'mars': PlanetData.MARS_DATA,
    'jupiter': PlanetData.JUPITER_DATA,
    'saturn': PlanetData.SATURN_DATA,
    'uranus': PlanetData.URANUS_DATA,
    'neptune': PlanetData.NEPTUNE_DATA
}

plts = Planets(dt=10*Constants.DAY_TO_SEC)
for name in pl_map:
    pl_data = pl_map[name]
    plts.add_planet(
        Planet(
            name, pl_data['Mass'],
            sem_maj_ax=pl_data['Semi Major Axis'],
            orb_incl=pl_data['Orbit Inclination'],
            orb_ecc=pl_data['Orbit Eccentricity'],
            intr_pl_ang=pl_data['Angle-Intr_pl'],
            maj_ang_pp=pl_data['Angle-maj_ax_pp'],
            init_theta=pl_data['Initial Theta']))

orbit_data = {name: [] for name in pl_map}
for i in range(25000):
    curr_data = plts.update_and_fetch_pos()
    for name in pl_map:
        orbit_data[name].append(curr_data[name])


class Planet_ui(HasTraits):
    name = Str()
    semi_major_axis = Float()
    orbit_inc = Float()
    orbit_ecc = Float()

    traits_view = View(
        'name',
        'semi_major_axis',
        'orbit_inc',
        'orbit_ecc',
        title='Create new planet',
        width=0.18,
        buttons=['OK', 'Cancel'],
    )


table_editor = TableEditor(
    columns=[ObjectColumn(
        name='name', width=0.20),
        ObjectColumn(
        name='semi_major_axis', width=0.10,
        horizontal_alignment='center',
        label='Semi Major Axis (AU)'),
        ObjectColumn(
        name='orbit_inc', width=0.10,
        horizontal_alignment='center',
        label='Orbit Inclination'),
        ObjectColumn(
        name='orbit_ecc', width=0.10,
        horizontal_alignment='center',
        label='Orbit Eccentricity'), ],
    deletable=True, sort_model=False, auto_size=False,
    orientation='vertical',
    edit_view=View(
        Group(
            'name', 'semi_major_axis', 'orbit_inc',
            'orbit_ecc', show_border=True),
        resizable=True,),
    show_toolbar=True, row_factory=Planet_ui,)


# Create some Planets:
planets_list = [
    Planet_ui(
        name=name.capitalize(),
        semi_major_axis=pl_map[name]['Semi Major Axis'],
        orbit_inc=pl_map[name]['Orbit Inclination'],
        orbit_ecc=pl_map[name]['Orbit Eccentricity'])
    for name in pl_map]


class PlanetarySystemModel(HasTraits):
    potential_threshold = Range(1, 1000, 100)
    speed = Range(1, 50, 10)

    scene = Instance(MlabSceneModel, ())
    plot = Instance(PipelineBase)

    play = Button('Play')
    toggle_bg = Button('Dark Mode')
    toggle_potential = Button('Potential')
    reset = Button()

    planets = List(Planet_ui)

    def __init__(self, planets):
        super().__init__()
        self.planet_plt = []
        self.sun_plot = self.scene.mlab.points3d(
            0, 0, 0, color=(1, 1, 0), resolution=100, scale_factor=0.4)
        curr_data = plts.update_and_fetch_pos()
        for name in pl_map:
            curr_pose = curr_data[name]
            self.planet_plt.append(self.scene.mlab.points3d(
                curr_pose[0],
                curr_pose[1],
                curr_pose[2],
                color=pl_map[name]['Color'],
                resolution=100,
                scale_factor=np.log10(pl_map[name]['Semi Major Axis']+1)*0.7)
            )

            orbit = np.array(orbit_data[name]).T
            self.scene.mlab.plot3d(
                orbit[0],
                orbit[1],
                orbit[2],
                tube_radius=0.01, color=(1, 1, 1))
        self.is_dark = True
        self.is_playing = False
        self.scene.scene.background = (0, 0, 0)
        self.planets = planets
        # self.plot_potential()

    @ observe('potential_threshold,speed,scene.activated')
    def update_plot(self, event=None):
        for i, name in enumerate(pl_map):
            curr_pose = plts.update_and_fetch_pos()
            self.planet_plt[i].mlab_source.trait_set(
                x=curr_pose[name][0],
                y=curr_pose[name][1],
                z=curr_pose[name][2])

    # @ observe('potential_threshold,scene.activated')
    def plot_potential(self, event=None):
        x, y = np.mgrid[-20:20:200j, -20:20:200j]
        self.grav_potential = np.zeros_like(x)
        for xi in range(len(x)):
            for yi in range(len(y)):
                self.grav_potential[xi, yi] = compute_grav_pot(
                    np.array([x[xi, yi], y[xi, yi], 0]), plts, thresh=self.potential_threshold)
        self.grav_potential /= np.max(self.grav_potential)
        self.pot_plot = self.scene.mlab.surf(
            x, y, self.grav_potential, colormap='Spectral')

    def _toggle_bg_fired(self):
        bgcolor = (0, 0, 0) if self.is_dark else (1, 1, 1)
        self.scene.scene.background = bgcolor
        self.is_dark = not self.is_dark

    def _toggle_potential_fired(self):
        self.plot_potential()

    def _play_fired(self):
        self.is_playing = not self.is_playing
        _ = [plts.update_and_fetch_pos() for i in range(self.speed)]
        curr_data = plts.update_and_fetch_pos()
        for i, name in enumerate(pl_map):
            curr_pose = curr_data[name]
            self.planet_plt[i].mlab_source.trait_set(
                x=curr_pose[0],
                y=curr_pose[1],
                z=curr_pose[2])

    def _reset_fired(self):
        self.planets = planets_list
        print("Reset fired")

    view = View(
        Group(
            Group(
                Item(
                    'scene', editor=SceneEditor(
                        scene_class=MayaviScene),
                    height=250, width=300, show_label=False),
                Group(
                    '_', 'potential_threshold', 'speed',
                    Group(
                        'toggle_bg', 'toggle_potential', 'play',
                        orientation='horizontal'),
                    show_border=True, label='Plotting Features'),
                orientation='vertical'),
            Group(
                Item('planets', show_label=False, editor=table_editor),
                'reset', show_border=True, label='Planet Data',),
            orientation='horizontal'),
        resizable=True, kind='live', title='Project: Planetary Visualization')


planet_system_model = PlanetarySystemModel(planets=planets_list)

if __name__ == '__main__':
    t0 = time.time()
    planet_system_model.configure_traits()
    print(f"Time taken to initialize is {time.time()-t0} secs")
