from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from future import standard_library
from future.builtins import *

from .common import Context, u
from .stepset import StepSet
from io import StringIO
from os.path import join
import copy
import glob
import yaml


class Rule(object):

    def __init__(self, parent=None):
        if parent is None:
            self.step_set = StepSet()
            self.context = Context()
        else:
            self.step_set = parent.step_set
            self.context = parent.context.__class__(
                data_provider=parent.context)

        self.metadata = Context()
        self.steps = []
        self.file_path = None

    def add_step(self, step):
        self.step_set.add_step(step)

    def add_step_set(self, step_set):
        self.step_set = self.step_set.concat(step_set)

    def run(self, **extra_context):
        self.context.update(extra_context)
        self.step_set.run(parsed_steps=self.steps, context=self.context)

    def load(self, path):
        content = open(path, 'r').read()
        self.parse(content)
        self.file_path = path

    def load_directory(self, path, filter_by=None, rule_ext='.rule'):
        rules = []
        rule_glob = join(path, '*{}'.format(rule_ext))
        for rulepath in glob.iglob(rule_glob):
            rule = Rule(parent=self)
            rule.load(rulepath)
            if self._rule_matches_filter(rule, filter_by):
                rules.append(rule)
        return rules

    def _rule_matches_filter(self, rule, filter_by):
        for attr, val in filter_by.items():
            if rule.metadata.get(attr, '') != val:
                return False
        return True

    def copy(self):
        rule = Rule()
        rule.context = self.context.copy()
        rule.step_set = copy.copy(self.step_set)
        return rule

    def parse(self, toparse):
        try:
            self.metadata, i = self.parse_metadata(toparse, 0)
        except yaml.error.YAMLError:
            i = 0

        self.steps = self.parse_steps(toparse, i)

    def parse_metadata(self, rule_text, start_index):
        rule_io = StringIO(u(rule_text))
        rule_io.seek(start_index, 0)

        loader = yaml.Loader(rule_io)
        loader.check_node()
        node = loader.get_node()
        metadata = loader.construct_mapping(node)
        metadata_end = loader.get_mark().index
        return metadata, metadata_end

    def parse_steps(self, rule_text, start_index):
        return self.step_set.parse(rule_text, start_index)
