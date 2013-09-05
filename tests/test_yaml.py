from unittest import TestCase
from brules import StepSet, UnmatchedStepError
from brules.steps import RegexStep, YamlStep, YamlFuncStep


class YamlTest(TestCase):
    def setUp(self):
        self.step_set = StepSet()

        def yaml_func(context, args):
            context.setdefault('args', {}).update(args)

        self.yaml_step = YamlFuncStep(yaml_func)
        self.step_set.add_step(self.yaml_step)

    def test_yaml_step(self):
        steps = self.step_set.parse('foo: bar\nbar: baz')
        expected = [({'foo': 'bar', 'bar': 'baz'}, self.yaml_step)]
        self.assertEqual(steps, expected)

    def test_multiple_yaml_steps(self):
        steps = self.step_set.parse('foo: bar\n...\nbar: baz\n...')
        expected = [({'foo': 'bar'}, self.yaml_step),
                    ({'bar': 'baz'}, self.yaml_step)]
        self.assertEqual(steps, expected)
        self.step_set.run('foo: bar\n...\nbar: baz\n...')
        expected = {
            'foo': 'bar',
            'bar': 'baz'
        }
        self.assertEqual(self.step_set.context.args, expected)

    def test_mixed_steps(self):
        re_step = RegexStep('%hello%')
        self.step_set.add_step(re_step)

        steps = self.step_set.parse('foo: bar\n...\n%hello%')
        expected = [
            ({'foo': 'bar'}, self.yaml_step),
            ({}, re_step)
        ]
        self.assertEquals(steps, expected)
