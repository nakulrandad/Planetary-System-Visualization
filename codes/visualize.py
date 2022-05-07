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

from traits.api import Any, Array, HasTraits, Range, Float, observe, Instance, Button, HasStrictTraits, Str, Int, List
from traitsui.api import View, Item, Group, UndoButton, RevertButton, TableEditor, ObjectColumn, ExpressionColumn

from mayavi.core.api import PipelineBase
from mayavi.core.ui.api import MayaviScene, SceneEditor, MlabSceneModel

from planets_data import PlanetData

# from traits.api import HasTraits, HasStrictTraits, Str, Int, Regex, List

# from traitsui.api import (
#     View,
#     Group,
#     Item,
#     TableEditor,
#     ObjectColumn,
#     ExpressionColumn,
#     EvalTableFilter,
# )
# from traitsui.table_filter import (
#     EvalFilterTemplate,
#     MenuFilterTemplate,
#     RuleFilterTemplate,
# )

PLANET_NAMES = [planet for planet in PlanetData.__dict__
                if not planet.startswith('_')]


def curve(n_mer, n_long, n_s):
    dphi = np.pi/1000.
    phi = np.arange(0.0, 2*np.pi + 0.5*dphi, dphi)
    mu = phi*n_mer
    x = np.cos(mu) * n_s * (1 + np.cos(n_long * mu/n_mer)*0.5)
    y = np.sin(mu) * n_s * (1 + np.sin(n_long * mu/n_mer)*0.5)
    z = 0.5 * n_s * np.sin(n_long*mu/n_mer)
    t = mu
    return x, y, z, t

# A helper class for the 'Department' class below:


class Employee(HasTraits):
    first_name = Str()
    last_name = Str()
    age = Int()

    traits_view = View(
        'first_name',
        'last_name',
        'age',
        title='Create new employee',
        width=0.18,
        buttons=['OK', 'Cancel'],
    )


# For readability, the TableEditor of the demo is defined here, rather than in
# the View:
table_editor = TableEditor(
    columns=[
        ObjectColumn(name='first_name', width=0.20),
        ObjectColumn(name='last_name', width=0.20),
        ExpressionColumn(
            label='Full Name',
            width=0.30,
            expression="'%s %s' % (object.first_name, " "object.last_name )",
        ),
        ObjectColumn(name='age', width=0.10, horizontal_alignment='center'),
    ],
    deletable=True,
    sort_model=True,
    auto_size=False,
    orientation='vertical',
    edit_view=View(
        Group('first_name', 'last_name', 'age', show_border=True),
        resizable=True,
    ),
    show_toolbar=True,
    row_factory=Employee,
)


# Create some employees:
employees_list = [
    Employee(first_name='Jason', last_name='Smith', age=32),
    Employee(first_name='Mike', last_name='Tollan', age=34),
    Employee(
        first_name='Dave', last_name='Richards', age=42
    ),
    Employee(first_name='Lyn', last_name='Spitz', age=40),
    Employee(first_name='Greg', last_name='Andrews', age=45),
]


class PlanetarySystemModel(HasTraits):
    n_meridional = Range(1, 30, 1)
    n_longitudinal = Range(0, 30, 12)
    n_size = Range(1, 5, 3)

    scene = Instance(MlabSceneModel, ())
    plot = Instance(PipelineBase)

    toggle_bg = Button('Dark Mode')
    reset = Button()

    employees = List(Employee)

    def __init__(self, employees):
        super().__init__()
        x, y, z, t = curve(self.n_meridional, self.n_longitudinal, self.n_size)
        self.plot = self.scene.mlab.plot3d(
            x, y, z, t, tube_radius=0.08, colormap='Spectral')
        self.is_dark = False
        self.scene.scene.background = (1, 1, 1)
        self.employees = employees

    @observe('n_meridional,n_longitudinal,n_size,scene.activated')
    def update_plot(self, event=None):
        x, y, z, t = curve(self.n_meridional, self.n_longitudinal, self.n_size)
        self.plot.mlab_source.trait_set(
            x=x, y=y, z=z, scalars=t)

    def _toggle_bg_fired(self):
        bgcolor = (0, 0, 0) if self.is_dark else (1, 1, 1)
        self.scene.scene.background = bgcolor
        self.is_dark = not self.is_dark

    def _reset_fired(self):
        self.employees = employees_list
        print("reset fired")

    view = View(
        Group(
            Group(
                Item(
                    'scene',
                    editor=SceneEditor(scene_class=MayaviScene),
                    height=250, width=300, show_label=False),
                Group(
                    '_', 'n_meridional', 'n_longitudinal', 'n_size',
                    'toggle_bg', show_border=True,
                    label='Plotting Features'),
                orientation='vertical'),
            Group(
                Item(
                    'employees', show_label=False,
                    editor=table_editor), 'reset',
                show_border=True, label='Planet Data',),
            orientation='horizontal'),
        resizable=True,
        kind='live', title='Project: Planetary Visualization')


planet_system_model = PlanetarySystemModel(employees=employees_list)
planet_system_model.configure_traits()


# Create the demo:
# demo = Department(employees=employees)

# # Run the demo (if invoked from the command line):
# if __name__ == '__main__':
#     demo.configure_traits()
