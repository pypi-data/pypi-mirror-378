from trame.ui.router import RouterViewLayout
from trame.ui.vuetify3 import SinglePageWithDrawerLayout
from trame.widgets import router, xterm

from . import (
    AnalyzeSimulation,
    CSRConfiguration,
    DistributionConfiguration,
    GeneralToolbar,
    ISRConfiguration,
    LatticeConfiguration,
    NavigationComponents,
    SimulationParameters,
    SpaceChargeConfiguration,
    ctrl,
    server,
    vuetify,
)
from .Input.visualization.lattice.ui import LatticeVisualizer

server.enable_module(
    {"styles": ["https://fonts.googleapis.com/css?family=Roboto:300,400,500"]}
)

from pathlib import Path

from trame.widgets import client

CSS_FILE = Path(__file__).with_name("Input").joinpath("style.css")

from .Input.shared import SharedUtilities

shared_utilities = SharedUtilities()

simulationParameters = SimulationParameters()
distribution = DistributionConfiguration()
lattice_config = LatticeConfiguration()
space_charge = SpaceChargeConfiguration()
csr = CSRConfiguration()
isr = ISRConfiguration()

card_column_padding = {"classes": "pa-2"}
card_row_padding = {"classes": "ma-2"}
card_breakpoints = {"cols": 12, "lg": 6, "md": 12, "sm": 6}

with RouterViewLayout(server, "/Input"):
    with vuetify.VContainer(fluid=True):
        with vuetify.VRow():
            with vuetify.VCol(cols=12, md=6):
                with vuetify.VRow(**card_row_padding):
                    with vuetify.VCol(**{**card_breakpoints, **card_column_padding}):
                        simulationParameters.card()
                    with vuetify.VCol(
                        **{**card_breakpoints, **card_column_padding},
                        v_show="space_charge !== 'false'",
                    ):
                        space_charge.card()
                    with vuetify.VCol(**{**card_breakpoints, **card_column_padding}):
                        distribution.card()
                    with vuetify.VCol(
                        **{**card_breakpoints, **card_column_padding}, v_show="csr"
                    ):
                        csr.card()
                    with vuetify.VCol(
                        **{**card_breakpoints, **card_column_padding}, v_show="isr"
                    ):
                        isr.card()
                with vuetify.VRow(**card_row_padding):
                    with vuetify.VCol(cols=12, **card_column_padding):
                        lattice_config.card()
            with vuetify.VCol(cols=12, md=6):
                with vuetify.VRow(**card_row_padding):
                    with vuetify.VCol():
                        LatticeVisualizer().card()

with RouterViewLayout(server, "/Analyze"):
    with vuetify.Template(v_if="active_visualization === 'Plot Over S'"):
        AnalyzeSimulation.plot_over_s()

    with vuetify.Template(v_if="active_visualization === 'Phase Space Plots'"):
        AnalyzeSimulation.phase_space()


# ----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------
def init_terminal():
    with xterm.XTerm(v_if="$route.path == '/Run'") as term:
        ctrl.terminal_print = term.writeln


def application():
    init_terminal()
    with SinglePageWithDrawerLayout(server) as layout:
        layout.title.hide()
        with layout:
            client.Style(CSS_FILE.read_text())

        with layout.toolbar:
            with vuetify.Template(v_if="$route.path == '/Analyze'"):
                GeneralToolbar.dashboard_toolbar("analyze")
            with vuetify.Template(v_if="$route.path == '/Input'"):
                GeneralToolbar.dashboard_toolbar("input")
            with vuetify.Template(v_if="$route.path == '/Run'"):
                GeneralToolbar.dashboard_toolbar("run")

        with layout.drawer as drawer:
            drawer.width = 200
            with vuetify.VList():
                vuetify.VListSubheader("Simulation")
            NavigationComponents.create_route("Input", "mdi-file-edit")
            NavigationComponents.create_route("Run", "mdi-play")
            NavigationComponents.create_route("Analyze", "mdi-chart-box-multiple")

        with layout.content:
            NavigationComponents.create_documentation_drawer()
            router.RouterView()
            init_terminal()
    return layout
