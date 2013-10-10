from unittest import TestCase
from brules import StepSet
from brules.steps import (
    CompositeStep, PredicateStep, PrefixStep, RegexFuncStep, YamlFuncStep)


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
  c: 42
  d: yep
"""
        steps = self.step_set.parse(rule)
        expected = [
            ({1: 'foo', 2: 'bar', 'x': 'foo', 'y': 'bar'}, self.set_step),
            ({1: 'foo', 2: 'blah', 'x': 'foo', 'y': 'blah', 'a': 2,
              'b': 'nope'},
             pred_step),
            ({1: 'foo', 2: 'bar', 'x': 'foo', 'y': 'bar', 'c': 42,
              'd': 'yep'},
             pred_step)
        ]
        self.assertEqual(steps, expected)
        context = self.step_set.run(rule)
        expected = {
            'foo': 'bar',
            'c': 42,
            'd': 'yep',
            1: 'foo',
            2: 'bar',
            'x': 'foo',
            'y': 'bar',
            'last_return': None
        }
        self.assertEqual(context, expected)

    def test_recursive_parse_conditional(self):
        def if_func(context, args):
            return context.get(args[1]) == args[2]
        if_step = RegexFuncStep(
            r'\s*if (.+) is (\w+) ', if_func, multiline=True)

        def set_from_yaml(context, args):
            context.setdefault('args', {}).update(
                {k: v for k, v in args.items() if isinstance(k, str)})
        set_from_yaml_step = CompositeStep(PrefixStep('then set:'),
                                           YamlFuncStep(set_from_yaml))
        self.step_set.add_step(PredicateStep(if_step))
        self.step_set.add_step(set_from_yaml_step)
        rule = """
               if a is b then set:
                 x: blah
                 y: 42

               set a to b
               if a is b then set:
                 foo: x
                 bar: 0
               """
        context = self.step_set.run(rule)
        self.assertEqual(context.args, {'foo': 'x', 'bar': 0})

    def test_yaml_prefix(self):
        def yaml_func(context, args):
            context.setdefault('args', {}).update(args)

        yaml_step = YamlFuncStep(yaml_func)
        prefix_step = PrefixStep('YAML!')
        prefixed_yaml_step = CompositeStep(prefix_step, yaml_step)
        self.step_set.add_step(prefixed_yaml_step)

        rule = """YAML!
                       a: foo
                       b: bar
                    """
        expected = {'a': 'foo', 'b': 'bar'}
        context = self.step_set.run(rule)
        self.assertEqual(context.args, expected)
