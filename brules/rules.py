from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from future import standard_library
from future.builtins import *

from .stepset import StepSet
from io import StringIO
import yaml


class Rule(object):
    def __init__(self):
        self.step_set = StepSet()
        self.context = {}
        self.metadata = {}
        self.steps = []

    def add_step(self, step):
        self.step_set.add_step(step)

    def add_step_set(self, step_set):
        self.step_set = self.step_set.concat(step_set)

    def run(self, torun):
        self.step_set.run(torun)
        self.context = self.step_set.context

    def parse(self, toparse):
        self.metadata, i = self.parse_metadata(toparse, 0)
        self.steps = self.parse_steps(toparse, i)

    def parse_metadata(self, rule_text, start_index):
        rule_io = StringIO(rule_text)
        rule_io.seek(start_index, 0)

        loader = yaml.Loader(rule_io)
        metadata = loader.get_data()
        metadata_end = loader.get_mark().index
        return metadata, metadata_end

    def parse_steps(self, rule_text, start_index):
        return self.step_set.parse(rule_text, start_index)
