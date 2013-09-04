from unittest import TestCase
from brules import StepSet, UnmatchedStepError
from brules.steps import RegexFuncStep


class MetadataTest(TestCase):
    def setUp(self):
        self.step_set = StepSet()

