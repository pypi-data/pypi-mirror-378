"""
This file is part of ImpactX

Copyright 2025 ImpactX contributors
Authors: Parthib Roy
License: BSD-3-Clause-LBNL
"""

from typing import Any

from impactx import distribution, elements
from impactx.impactx_pybind import ImpactX, RefPart

from .. import state
from .defaults_helper import InputDefaultsHelper

DISTRIBUTION_MODULE_NAME = distribution
LATTICE_MODULE_NAME = elements

TRACKING_MODE_PROPERTIES: dict[str, dict[str, Any]] = {
    "Reference Tracking": {
        "space_charge": False,
        "csr": False,
        "disable_space_charge": True,
        "disable_csr": True,
        "space_charge_list": ["false"],
    },
    "Envelope Tracking": {
        "csr": False,
        "disable_space_charge": False,
        "disable_csr": True,
        "space_charge_list": ["false", "2D", "3D"],
    },
    "Particle Tracking": {
        "disable_space_charge": False,
        "disable_csr": False,
        "space_charge_list": ["false", "3D"],
    },
}

BEAM_MONITOR_DEFAULT_NAME = "DefaultName"

CONVERSION_FACTORS = {
    "eV": 1.0e-6,
    "keV": 1.0e-3,
    "MeV": 1.0,
    "GeV": 1.0e3,
    "TeV": 1.0e6,
}


class DashboardDefaults:
    """
    Defaults for simulation parameters in the ImpactX dashboard.
    """

    COLLAPSABLE_SECTIONS = [
        "collapse_simulation_parameters",
        "collapse_csr",
        "collapse_isr",
        "collapse_distribution_parameters",
        "collapse_space_charge",
        "collapse_lattice_configuration",
    ]
    # -------------------------------------------------------------------------
    # Inputs by section
    # -------------------------------------------------------------------------

    SIMULATION_PARAMETERS = {
        "space_charge": "false",
        "csr": False,
        "isr": False,
        "tracking_mode": "Particle Tracking",
        "charge_qe": -1,
        "mass_MeV": 0.51099895,
        "npart": 1000,
        "kin_energy_on_ui": 2e3,
        "kin_energy_MeV": 2e3,
        "kin_energy_unit": "MeV",
        "bunch_charge_C": 1e-9,
    }

    DISTRIBUTION_PARAMETERS = {
        "distribution": "Waterbag",
        "distribution_type": "Twiss",
    }

    LATTICE_CONFIGURATION = {
        "selected_lattice_list": [],
        "selected_lattice": None,
        "periods": 1,
    }

    SPACE_CHARGE = {
        "dynamic_size": False,
        "poisson_solver": "fft",
        "particle_shape": 2,
        "max_level": 0,
        "n_cell_x": 32,
        "n_cell_y": 32,
        "n_cell_z": 32,
        "blocking_factor_x": 8,
        "blocking_factor_y": 8,
        "blocking_factor_z": 8,
        "prob_relative_first_value_fft": 1.1,
        "prob_relative_first_value_multigrid": 3.1,
        "mlmg_relative_tolerance": 1.0e-7,
        "mlmg_absolute_tolerance": 0,
        "mlmg_verbosity": 1,
        "mlmg_max_iters": 100,
    }

    CSR = {
        "particle_shape": 2,
        "csr_bins": 150,
    }

    ISR = {
        "isr_order": 1,
    }

    LISTS = {
        "tracking_mode_list": [
            "Particle Tracking",
            "Envelope Tracking",
            "Reference Tracking",
        ],
        "distribution_list": InputDefaultsHelper.select_classes(
            DISTRIBUTION_MODULE_NAME
        ),
        "lattice_list": InputDefaultsHelper.select_classes(LATTICE_MODULE_NAME),
        "kin_energy_unit_list": ["eV", "keV", "MeV", "GeV", "TeV"],
        "distribution_type_list": ["Twiss", "Quadratic"],
        "poisson_solver_list": ["fft", "multigrid"],
        "particle_shape_list": [1, 2, 3],
        "max_level_list": [0, 1, 2, 3, 4],
        "isr_order_list": [1, 2, 3],
    }

    # -------------------------------------------------------------------------
    # Main
    # -------------------------------------------------------------------------

    DEFAULT_VALUES = {
        **SIMULATION_PARAMETERS,
        **DISTRIBUTION_PARAMETERS,
        **LATTICE_CONFIGURATION,
        **SPACE_CHARGE,
        **CSR,
        **ISR,
        **LISTS,
    }

    TYPES = {
        "distribution": "float",
        "lattice": "float",
        "npart": "int",
        "kin_energy_on_ui": "float",
        "bunch_charge_C": "float",
        "mass_MeV": "float",
        "charge_qe": "int",
        "csr_bins": "int",
        "n_cell": "int",
        "blocking_factor": "int",
        "beta": "float",
        "emitt": "float",
        "alpha": "float",
        "periods": "int",
        "mlmg_relative_tolerance": "float",
        "mlmg_absolute_tolerance": "float",
        "mlmg_max_iters": "int",
        "mlmg_verbosity": "int",
        "prob_relative": "float",
    }

    VALIDATION_CONDITION = {
        "lambda": ["positive"],
        "beta": ["positive"],
        "emitt": ["positive"],
        "charge_qe": ["non_zero"],
        "mass_MeV": ["positive"],
        "csr_bins": ["positive"],
        "blocking_factor": ["positive"],
        "periods": ["positive"],
        "mlmg_relative_tolerance": ["positive"],
        "mlmg_max_iters": ["positive"],
        "prob_relative": ["positive"],
    }

    # If a parameter is not included in the dictionary, default step amount is 1.
    STEPS = {
        "mass_MeV": 0.1,
        "bunch_charge_C": 1e-11,
        "prob_relative": 0.1,
        "mlmg_relative_tolerance": 1e-12,
        "mlmg_absolute_tolerance": 1e-12,
        "beta": 0.1,
        "emitt": 1e-7,
        "alpha": 0.1,
    }

    UNITS = {
        "charge_qe": "qe",
        "mass_MeV": "MeV",
        "bunch_charge_C": "C",
        "mlmg_absolute_tolerance": "V/m",
        "beta": "m",
        "emitt": "m",
    }

    DOCUMENTATION = {
        "simulation_parameters": "https://impactx.readthedocs.io/en/latest/usage/python.html#impactx.ImpactX",
        "lattice_configuration": "https://impactx.readthedocs.io/en/latest/usage/python.html#lattice-elements",
        "distribution_parameters": "https://impactx.readthedocs.io/en/latest/usage/python.html#initial-beam-distributions",
        "space_charge": "https://impactx.readthedocs.io/en/latest/usage/parameters.html#space-charge",
        "csr": "https://impactx.readthedocs.io/en/latest/usage/parameters.html#coherent-synchrotron-radiation-csr",
        "isr": "https://impactx.readthedocs.io/en/latest/usage/parameters.html#incoherent-synchrotron-radiation-isr",
    }


class TooltipDefaults:
    """
    Defaults for input toolips in the ImpactX dashboard.
    """

    state.all_tooltips = InputDefaultsHelper.get_docstrings(
        [RefPart, ImpactX], DashboardDefaults.DEFAULT_VALUES
    )


class ToolbarDefaults:
    """
    Default styling and states for the toolbar
    section in the ImpactX dashboard.
    """

    TOOLBAR_SIZE = 64
    FOOTER_SIZE = 8


class UIDefaults:
    """
    Default UI which the input cards reply on in the ImpactX dashboard.
    """

    ROW_STYLE = {
        "dense": False,
    }

    CARD_TEXT_OVERFLOW = {
        "classes": "custom-scrollbar",
        "style": {
            "flex": "1",
            "overflow-y": "auto",
            "overflow-x": "auto",
            "max-height": "50vh",
        },
    }

    CARD_STYLE = {
        "display": "flex",
        "flex-direction": "column",
    }
