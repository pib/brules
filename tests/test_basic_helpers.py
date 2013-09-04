from unittest import TestCase
from brules import StepSet
from brules.helpers.basic import if_then_set
from brules.steps import RegexFuncStep as RFS


@RFS.make(r'Does (?P<a>.+) plus (?P<b>.+) equal (?P<c>.+)\?')
def does_a_plus_b_equal_c(context, args):
    print(args)
    if int(args.a) + int(args.b) == int(args.c):
        return True
    return False


class BasicHelpersTest(TestCase):
    def setUp(self):
        self.stepset = StepSet()
        self.stepset.add_step(does_a_plus_b_equal_c)
        self.stepset.add_step(if_then_set)

    def test_if_then_set(self):
        rules = """\
            Does 1 plus 2 equal 42?
            If so, then set answer to: Life,
                the universe,
                and everything.
            If not, then set insult to: You, sir,
              are bad at math.

            Does 2 plus 2 equal 4?
            If so, then set answer to: Ok.
             Who gave you the answer to that
             one?
            If not, then set insult to: Wow, you're so bad at math
             that you actually broke this program.
            """
        self.stepset.run(rules)
        self.assertEqual(self.stepset.context.answer,
                         'Ok. Who gave you the answer to that one?')
        self.assertEqual(self.stepset.context.insult,
                         'You, sir, are bad at math.')
