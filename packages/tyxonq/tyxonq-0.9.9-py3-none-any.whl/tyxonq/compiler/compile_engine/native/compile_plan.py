from __future__ import annotations

from typing import List, Sequence, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from tyxonq.compiler import Pass
    from tyxonq.core.ir import Circuit
    from tyxonq.devices import DeviceRule


def _resolve_stage(name: str) -> "Pass":
    """Resolve a stage name to a Pass instance.

    Supported names (initial skeleton):
      - "decompose"
      - "rewrite/measurement"
      - "layout"
      - "scheduling"
      - "scheduling/shot_scheduler"
    """

    if name == "decompose":
        from ...stages.decompose import NoOpDecomposePass

        return NoOpDecomposePass()
    if name == "decompose/rotations":
        from ...stages.decompose.rotations import RotationsDecomposePass

        return RotationsDecomposePass()
    if name == "rewrite/measurement":
        from ...stages.rewrite.measurement import MeasurementRewritePass

        return MeasurementRewritePass()
    if name == "rewrite/auto_measure":
        from ...stages.rewrite.auto_measure import AutoMeasurePass

        return AutoMeasurePass()
    if name == "rewrite/gates_transform":
        from ...stages.rewrite.gates_transform import GatesTransformPass

        return GatesTransformPass()
    if name == "rewrite/merge_prune":
        from ...stages.rewrite.merge_prune import MergePrunePass

        return MergePrunePass()
    if name == "layout":
        from ...stages.layout import NoOpLayoutPass

        return NoOpLayoutPass()
    if name == "scheduling":
        from ...stages.scheduling import NoOpSchedulingPass

        return NoOpSchedulingPass()
    if name == "scheduling/shot_scheduler":
        from ...stages.scheduling.shot_scheduler import ShotSchedulerPass

        return ShotSchedulerPass()
    if name == "gradients/parameter_shift":
        from ...stages.gradients.parameter_shift_pass import ParameterShiftPass

        return ParameterShiftPass()
    if name == "simplify/lightcone":
        from ...stages.simplify.lightcone import LightconeSimplifyPass

        return LightconeSimplifyPass()

    raise ValueError(f"Unknown stage: {name}")


class CompilePlan:
    """Composable pipeline of compilation passes.

    The pipeline applies a sequence of `Pass` instances to a circuit given
    device capabilities and options. This skeleton keeps passes simple and
    composable.
    """

    def __init__(self, passes: Sequence["Pass"]) -> None:
        self._passes: List["Pass"] = list(passes)

    @property
    def passes(self) -> Sequence["Pass"]:
        return tuple(self._passes)

    def execute_plan(self, circuit: "Circuit", **opts) -> "Circuit":
        current = circuit
        for p in self._passes:
            current = p.execute_plan(current, **opts)
        return current


def build_plan(names: Sequence[str]) -> CompilePlan:
    """Build a pipeline from a list of stage names."""

    return CompilePlan([_resolve_stage(n) for n in names])


