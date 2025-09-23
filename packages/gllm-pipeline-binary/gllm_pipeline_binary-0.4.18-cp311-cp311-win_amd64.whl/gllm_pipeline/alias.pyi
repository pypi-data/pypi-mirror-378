from gllm_pipeline.steps.pipeline_step import BasePipelineStep as BasePipelineStep
from gllm_pipeline.types import Val as Val

PipelineSteps = BasePipelineStep | list[BasePipelineStep]
InputMapSpec = dict[str, str | Val] | list[str | dict[str, str] | dict[str, Val]]
