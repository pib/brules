from brules import StepSet
from brules.steps import RegexFuncStep
from brules.rules import Rule
from textwrap import dedent

from mock import Mock
from unittest import TestCase


class RuleTest(TestCase):
    def setUp(self):
        self.rule = Rule()

        def step_fn(context, args):
            context.calls = context.get('calls', 0) + 1
            return args[1] + str(context.calls)

        self.step = RegexFuncStep('(.+)', step_fn)
        self.rule.step_set.add_step(self.step)

        self.rule_text = dedent("""\
            title: Check yo self
            category: test rule
            points: 42
            ...
            This bit: the step text.
            """)

    def test_add_step(self):
        self.rule.step_set.add_step = Mock(self.rule.step_set.add_step)
        self.rule.add_step('notastep')
        self.rule.step_set.add_step.assert_called_with('notastep')

    def test_add_step_set(self):
        ss = self.rule.step_set
        replacement_ss = StepSet()
        ss.concat = Mock(return_value=replacement_ss)

        new_step_set = StepSet()
        self.rule.add_step_set(new_step_set)
        ss.concat.assert_called_with(new_step_set)
        self.assertIs(self.rule.step_set, replacement_ss)

    def test_parse_metadata(self):
        metadata, i = self.rule.parse_metadata(self.rule_text, 0)
        expected = {
            'title': 'Check yo self',
            'category': 'test rule',
            'points': 42}
        self.assertEqual(metadata, expected)
        self.assertEqual(i, 55)

    def test_parse_steps(self):
        steps = self.rule.parse_steps(self.rule_text, 55)
        expected = [({1: 'This bit: the step text.'}, self.step)]
        self.assertEqual(steps, expected)

    def test_parse(self):
        self.rule.parse(self.rule_text)

        expected_meta = {
            'title': 'Check yo self',
            'category': 'test rule',
            'points': 42}
        self.assertEqual(self.rule.metadata, expected_meta)

        expected_steps = [({1: 'This bit: the step text.'}, self.step)]
        self.assertEqual(self.rule.steps, expected_steps)

    def test_run(self):
        self.rule.parse(self.rule_text)
        self.rule.run('This bit: the step text.\nThis bit: the step text.')
        expected_ctx = {
            'calls': 2,
            'last_return': 'This bit: the step text.2'
        }
        self.assertEqual(self.rule.step_set.context, expected_ctx)
        self.assertIs(self.rule.context, self.rule.step_set.context)
