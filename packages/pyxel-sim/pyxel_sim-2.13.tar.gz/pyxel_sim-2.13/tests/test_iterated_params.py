from pyxel.observation import Observation
from pyxel.observation import ParameterValues
from pyxel.pipelines import Processor
from pyxel.pipelines.processor import MISSING
from pyxel.exposure import Readout
from pyxel.detectors import Detector
from pyxel.pipelines import DetectionPipeline
from typing import Any
import pytest


class DummyProcessor(Processor):
    """Processor without any registered parameters, to simulate lookup."""

    def __init__(self):
        detector = Detector()
        pipeline = DetectionPipeline()
        super().__init__(detector=detector, pipeline=pipeline)

    def has(self, key: str) -> bool:
        return False

    def get(self, key: str, default: Any = MISSING) -> Any:
        return None


def test_invalid_parameter_key_triggers_clear_error():
    """Ensure invalid parameter keys produce an improved KeyError message."""

    parameters = [
        ParameterValues(
            key="cfg.pipeline.charge_generation.exponential_qe.arguments.x_epi",  # Invalid key
            values=[0.5],
            enabled=True,
        )
    ]

    obs = Observation(
        parameters=parameters,
        readout=Readout(),
        mode="product",
    )

    processor = DummyProcessor()

    # try:
    with pytest.raises(KeyError, match=r"prout"):
        obs.validate_steps(processor)
    # except KeyError as e:
    #     message = str(e)
    #     assert "cfg.pipeline.charge_generation.exponential_qe.arguments.x_epi" in message
    #     assert "Non-existing parameter" in message
    # else:
    #     raise AssertionError("Expected KeyError for invalid parameter key.")
