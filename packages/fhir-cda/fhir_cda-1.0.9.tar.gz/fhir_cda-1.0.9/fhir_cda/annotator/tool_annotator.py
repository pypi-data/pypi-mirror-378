from abc import ABC
from .abstract_annotator import AbstractAnnotator
class ToolAnnotator(AbstractAnnotator, ABC):
    def __init__(self, dataset_path):
        super().__init__(dataset_path, "workflow_tool")