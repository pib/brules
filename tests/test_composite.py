from unittest import TestCase
from brules import StepSet, UnmatchedStepError
from brules.steps import PredicateStep, RegexFuncStep, YamlFuncStep


class CompositeTest(TestCase):
    def setUp(self):
        self.step_set = StepSet()

        def set_x_to_y(context, args):
            context[args.x] = args.y
        self.set_step = RegexFuncStep('set (?P<x>.+) to (?P<y>.+)',
                                      set_x_to_y)
        self.step_set.add_step(self.set_step)

    def test_predicate_step(self):
        def if_func(context, args):
            return context[args.x] == args.y
        if_step = RegexFuncStep('if (?P<x>.+) is (?P<y>.+) then', if_func)

        def set_from_yaml(context, args):
            context.update(args)
        set_from_yaml_step = YamlFuncStep(set_from_yaml)

        pred_step = PredicateStep(if_step, set_from_yaml_step)
        self.step_set.add_step(pred_step)

        rule = """\
set foo to bar
if foo is blah then
  a: 2
  b: nope
if foo is bar then
  a: 42
  b: yep
"""
        steps = self.step_set.parse(rule)
        expected = [
            ({}, )
        ]
