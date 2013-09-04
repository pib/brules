from .common import AttrDict, UnmatchedStepError, combined_match_dict
from .steps import RegexFuncStep


class StepSet(object):
    def __init__(self):
        self.context = AttrDict()
        self._steps = []
        self._multiline_steps = []

    def run(self, step_text):
        steps = self.parse(step_text)
        for args, step in steps:
            self.context['last_return'] = step(self.context, args)

    def concat(self, other):
        new_rs = StepSet()
        for name in '_steps', '_multiline_steps':
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
            match_found = False
            for step in self._steps:
                try:
                    match, i = step.parse(toparse, i)
                    matches.append(match)
                    match_found = True
                except UnmatchedStepError:
                    continue
            if not match_found:
                line = toparse[i:].split('\n', 1)[0]
                if line.strip() == '':
                    i += len(line) + 1
                    continue
                raise UnmatchedStepError(
                    'No matching steps for "{}"'.format(line))
        return matches
