from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from future import standard_library
from future.builtins import *

from .common import UnmatchedStepError, combined_match_dict, u
from copy import copy
from io import StringIO
import re
import yaml


class Step(object):

    def parse(self, step_set, toparse, start_index):
        raise NotImplementedError('Step subclasses must implement parse')

    def __call__(self, context, args):
        raise NotImplementedError('Step subclasses must implement __call__')


class RegexStep(Step):

    def __init__(self, regex, multiline=False):
        self.multiline = multiline
        self.regex = re.compile(regex)

    def parse(self, step_set, toparse, start_index):
        if self.multiline:
            return self.parse_multiline(toparse, start_index)
        else:
            return self.parse_line(toparse, start_index)

    def parse_multiline(self, toparse, start_index):
        match = self.regex.match(toparse, start_index)
        if match:
            match_dict = combined_match_dict(match)
            end = match.end()
            return (match_dict, self), end
        line = toparse[start_index:].split('\n', 1)[0]
        raise UnmatchedStepError(line)

    def parse_line(self, toparse, start_index):
        end = len(toparse)
        line_end = toparse.find('\n', start_index)
        if line_end == -1:
            line_end = end
        line = toparse[start_index:line_end]
        match = self.regex.search(line)
        if match:
            match_dict = combined_match_dict(match)

            start = match.start()
            end = match.end()

            if start > 0:
                match_dict['prefix_content'] = line[:start]
            if end < len(line):
                match_dict['suffix_content'] = line[end:]

            return (match_dict, self), line_end + 1
        raise UnmatchedStepError(line)

    def __repr__(self):
        return '<{}.{} "{}">'.format(self.__class__.__module__,
                                     self.__class__.__name__,
                                     self.regex.pattern)


class RegexFuncStep(RegexStep):

    def __init__(self, regex, func, multiline=False):
        super(RegexFuncStep, self).__init__(regex, multiline)
        self.func = func

    def __call__(self, context, args):
        return self.func(context, args)

    @classmethod
    def make(cls, regex, multiline=False):
        """Decorator which wraps the specified regex and func in a
        RegexFuncStep instance
        """
        def make_inst(func):
            return cls(regex, func, multiline)

        return make_inst

    def __repr__(self):
        return '<{}.{} {}.{} "{}">'.format(
            self.__class__.__module__, self.__class__.__name__,
            self.func.__module__, self.func.__name__,
            self.regex.pattern)


class PrefixStep(RegexStep):

    """ A simple step which matches a regex and returns True

    For use with composite steps to require a prefix before another
    step. For example, to add a prefix before a YamlFuncStep.

    Defaults to multiline=True so it can match in the middle of a
    line.
    """

    def __init__(self, regex, multiline=True):
        super(PrefixStep, self).__init__(regex, multiline)

    def __call__(self, context, args):
        return True


class YamlStep(Step):

    def parse(self, step_set, toparse, start_index):
        step_io = StringIO(u(toparse))
        step_io.seek(start_index, 0)

        loader = yaml.Loader(step_io)
        try:
            val = loader.get_data()
        except yaml.error.YAMLError:
            line = toparse[start_index:].split('\n', 1)[0]
            raise UnmatchedStepError(line)

        if loader.tokens:
            val_end = loader.tokens[0].start_mark.index
        else:
            val_end = loader.get_mark().index
        return (val, self), start_index + val_end


class YamlFuncStep(YamlStep):

    def __init__(self, func):
        self.func = func

    def __call__(self, context, args):
        return self.func(context, args)

    @classmethod
    def make(cls, func):
        """Decorator which wraps the specified func in a
        YamlFuncStep instance
        """
        return cls(func)


class CompositeStep(Step):

    def __init__(self, first_step, second_step):
        self.first_step = first_step
        self.second_step = second_step

    def parse(self, step_set, toparse, start_index):
        (args, _), i = self.first_step.parse(step_set, toparse, start_index)
        (args2, _), i = self.second_step.parse(step_set, toparse, i)
        args.update(args2)
        return (args, self), i

    def __call__(self, context, args):
        context.last_return = self.first_step(context, args)
        self.second_step(context, args)


class PredicateStep(CompositeStep):

    """ A composite of two other steps, a predicate step, and a
    conditional step.

    When parsing, both steps must parse, or the step doesn't match.

    If a conditional step is not specified, the parse method will call
    step_set.parse and create a new PredicateStep with the returned
    instance as its conditional step.

    When running, if the predicate step returns a truthy value, then
    the conditional step is run. Otherwise, the conditional step is
    not run.
    """

    def __init__(self, first_step, second_step=None):
        super(PredicateStep, self).__init__(first_step, second_step)

    def parse(self, step_set, toparse, start_index):
        if self.second_step:
            return super(PredicateStep, self).parse(step_set, toparse,
                                                    start_index)

        (args, _), i = self.first_step.parse(step_set, toparse, start_index)
        (args2, second_step), i = step_set.parse_one(toparse, i)
        args.update(args2)

        step = copy(self)
        step.second_step = second_step
        return (args, step), i

    def __call__(self, context, args):
        last_return = context.get('last_return')

        if self.first_step(context, args):
            self.second_step(context, args)

        return last_return


class LoopStep(PredicateStep):

    def __init__(self, regex, context_var, loop_step=None, multiline=True):
        prefix_step = PrefixStep(regex, multiline)
        super(LoopStep, self).__init__(prefix_step, loop_step)
        self.context_var = context_var

    def __call__(self, context, args):
        for it in context.get(self.context_var, []):
            context.it = it
            context.last_return = self.second_step(context, args)

        return context.get('last_return')
