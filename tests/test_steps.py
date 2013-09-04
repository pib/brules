from unittest import TestCase
from brules.steps import Step


class StepsTest(TestCase):
    def setUp(self):
        self.step = Step()

    def test_unimplemented(self):
        self.assertRaises(NotImplementedError, self.step.parse, 'whatever', 0)
        self.assertRaises(NotImplementedError, self.step, {}, {})
