import os
import tempfile
from collections.abc import Callable, Sequence

from cat.analysis import OP, monte_carlo, step_param
from cat.core.circuit import Circuit
from cat.core.components import Resistor, Vdc
from cat.core.net import GND
from cat.spice.base import RunArtifacts, RunResult
from cat.spice.registry import get_run_directives, set_run_directives

ASCII_TEMPLATE = """Title:  op
Date:   Thu Sep  1 12:00:00 2025
Plotname: Operating Point
Flags: real
No. Variables: 2
No. Points: 1
Variables:
        0       time    time
        1       v(n1)   voltage
Values:
        0       0.0     {value}
"""


def _fake_runner_value(val: float) -> Callable[[str, Sequence[str]], RunResult]:
    def _runner(netlist: str, directives: Sequence[str]) -> RunResult:
        td = tempfile.mkdtemp()
        raw = os.path.join(td, "sim.raw")
        with open(raw, "w") as f:
            f.write(ASCII_TEMPLATE.format(value=val))
        log = os.path.join(td, "ngspice.log")
        with open(log, "w") as f:
            f.write("ok\n")
        art = RunArtifacts(netlist_path=os.path.join(td, "deck.cir"), log_path=log, raw_path=raw)
        return RunResult(artifacts=art, returncode=0, stdout="", stderr="")

    return _runner


def test_step_param_preserves_order_parallel() -> None:
    old = get_run_directives()
    try:
        # Sequence of values in grid: we'll return different last points to detect reorderings
        runners: list[Callable[[str, Sequence[str]], RunResult]] = [
            _fake_runner_value(v) for v in (1.0, 2.0, 5.0)
        ]
        idx = {0: 0}

        def multiplex_runner(net: str, dirs: Sequence[str]) -> RunResult:
            i = idx[0]
            idx[0] = (i + 1) % len(runners)
            return runners[i](net, dirs)

        set_run_directives(multiplex_runner)
        c = Circuit("step_order")
        V1 = Vdc("1", 1.0)
        R1 = Resistor("1", "{R}")
        c.add(V1, R1)
        c.connect(V1.ports[0], R1.ports[0])
        c.connect(R1.ports[1], GND)
        c.connect(V1.ports[1], GND)
        step = step_param(c, "R", ["1k", "2k", "5k"], analysis_factory=lambda: OP(), workers=2)
        vals = [r.traces["v(n1)"].values[-1] for r in step.runs]
        assert list(vals) == [1.0, 2.0, 5.0]
    finally:
        set_run_directives(old)


def test_montecarlo_preserves_order_parallel() -> None:
    old = get_run_directives()
    try:
        runners: list[Callable[[str, Sequence[str]], RunResult]] = [
            _fake_runner_value(v) for v in (10.0, 20.0, 30.0, 40.0)
        ]
        idx = {0: 0}

        def multiplex_runner(net: str, dirs: Sequence[str]) -> RunResult:
            i = idx[0]
            idx[0] = (i + 1) % len(runners)
            return runners[i](net, dirs)

        set_run_directives(multiplex_runner)
        c = Circuit("mc_order")
        V1 = Vdc("1", 1.0)
        R1 = Resistor("1", 1000.0)
        c.add(V1, R1)
        c.connect(V1.ports[0], R1.ports[0])
        c.connect(R1.ports[1], GND)
        c.connect(V1.ports[1], GND)
        from cat.analysis import NormalPct

        mc = monte_carlo(
            c, {R1: NormalPct(0.01)}, n=4, analysis_factory=lambda: OP(), seed=1, workers=3
        )
        vals = [r.traces["v(n1)"].values[-1] for r in mc.runs]
        assert list(vals) == [10.0, 20.0, 30.0, 40.0]
    finally:
        set_run_directives(old)
