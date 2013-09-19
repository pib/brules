from unittest import TestCase
from brules import StepSet

#pylint: disable=unused-variable, unused-argument


class ConcatTest(TestCase):
    def test_concat(self):
        rs1 = StepSet()
        rs2 = StepSet()

        @rs1.step('Step 1')
        def step1(ctx, args):
            ctx.step1 = True

        @rs2.step('Step 2')
        def step2(ctx, args):
            ctx.step2 = True

        rs3 = rs1.concat(rs2)
        context = rs3.run('Step 1\nStep 2')
        self.assertTrue(context.step1)
        self.assertTrue(context.step2)
