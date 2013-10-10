from .common import Context, UnmatchedStepError
from .steps import RegexFuncStep


class StepSet(object):

    def __init__(self, *steps):
        self._steps = list(steps)

    def run(self, step_text=None, parsed_steps=None, context=None):
        context = context if context is not None else Context()
        steps = parsed_steps or self.parse(step_text)
        for args, step in steps:
            context['last_return'] = step(context, args)

        return context

    def concat(self, other):
        new_rs = StepSet()
        for name in ('_steps',):
            new_list = getattr(self, name) + getattr(other, name)
            setattr(new_rs, name, new_list)

        return new_rs

    def step(self, pattern):
        def attach_step(f):
            step = RegexFuncStep(pattern, f)
            self.add_step(step)
            return f
        return attach_step

    def multiline_step(self, pattern):
        def attach_multiline_step(f):
            step = RegexFuncStep(pattern, f, multiline=True)
            self.add_step(step)
            return f
        return attach_multiline_step

    def add_step(self, step):
        self._steps.append(step)

    def parse(self, toparse, start_index=0):
        matches = []
        i = start_index
        end = len(toparse)
        while i < end:
            match, i = self.parse_one(toparse, i)
            if match is not None:
                matches.append(match)
        return matches

    def parse_one(self, toparse, start_index):
        for step in self._steps:
            try:
                return step.parse(self, toparse, start_index)
            except UnmatchedStepError:
                continue

        line = toparse[start_index:].split('\n', 1)[0]
        if line.strip() == '':
            return None, start_index + len(line) + 1

        raise UnmatchedStepError(
            'No matching steps for "{}"'.format(line))

    def doc(self):
        """ Generate documentation for the steps in this StepSet """
