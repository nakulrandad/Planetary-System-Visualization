#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ============================================================================
"""
Description: Visualization of planetary data via GUI.

Author: Nakul Randad (https://github.com/nakulrandad)
"""
# ============================================================================
import numpy as np
from matplotlib import pyplot as plt

from traits.api import Any, Array, HasTraits, Range, Float, observe, Instance, Button
from traitsui.api import View, Item, Group, UndoButton, RevertButton

from mayavi.core.api import PipelineBase
from mayavi.core.ui.api import MayaviScene, SceneEditor, MlabSceneModel


def curve(n_mer, n_long, n_s):
    dphi = np.pi/1000.
    phi = np.arange(0.0, 2*np.pi + 0.5*dphi, dphi)
    mu = phi*n_mer
    x = np.cos(mu) * n_s * (1 + np.cos(n_long * mu/n_mer)*0.5)
    y = np.sin(mu) * n_s * (1 + np.sin(n_long * mu/n_mer)*0.5)
    z = 0.5 * n_s * np.sin(n_long*mu/n_mer)
    t = mu
    return x, y, z, t


class PlanetarySystemModel(HasTraits):
    n_meridional = Range(1, 30, 1)
    n_longitudinal = Range(0, 30, 12)
    n_size = Range(1, 5, 3)

    scene = Instance(MlabSceneModel, ())
    plot = Instance(PipelineBase)

    toggle_bg = Button('Dark Mode')

    def __init__(self):
        super().__init__()
        x, y, z, t = curve(self.n_meridional, self.n_longitudinal, self.n_size)
        self.plot = self.scene.mlab.plot3d(
            x, y, z, t, tube_radius=0.08, colormap='Spectral')
        self.is_dark = False
        self.scene.scene.background = (1, 1, 1)

    @observe('n_meridional,n_longitudinal,n_size,scene.activated')
    def update_plot(self, event=None):
        x, y, z, t = curve(self.n_meridional, self.n_longitudinal, self.n_size)
        self.plot.mlab_source.trait_set(
            x=x, y=y, z=z, scalars=t)

    def _toggle_bg_fired(self):
        print("I am toggled!")
        bgcolor = (0, 0, 0) if self.is_dark else (1, 1, 1)
        self.is_dark = not self.is_dark
        self.scene.scene.background = bgcolor

    # The layout of the dialog created
    view = View(
        Group(
            Item(
                'scene', editor=SceneEditor(
                    scene_class=MayaviScene),
                height=250, width=300, show_label=False),
            Group(
                '_', 'n_meridional', 'n_longitudinal', 'n_size', 'toggle_bg',
                show_border=True, label='Curve Parameters'),
            orientation='vertical'),
        resizable=True, buttons=[UndoButton, RevertButton],
        title='Project: Planetary Visualization')


planet_system_model = PlanetarySystemModel()
planet_system_model.configure_traits()
