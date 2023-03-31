# -*- coding: utf-8 -*-

from django.test import TestCase

from ontask.dataops import formula


class HasVariableTest(TestCase):
    formula1 = {u'not': False, u'rules': [
        {u'value': u'df', u'field': u'Course_Code_a', u'operator': u'equal',
         u'input': u'text', u'type': u'string', u'id': u'Course_Code_a'},
        {u'value': u'v2', u'field': u'ANOTHER', u'operator': u'equal',
         u'input': u'text', u'type': u'string', u'id': u'ANOTHER'}],
                u'valid': True, u'condition': u'AND'}

    formula2 = {u'not': False, u'rules': [
        {u'value': u'df', u'field': u'Course_Code_a', u'operator': u'equal',
         u'input': u'text', u'type': u'string', u'id': u'Course_Code_a'},
        {u'value': u'v2', u'field': u'ANOTHER', u'operator': u'equal',
         u'input': u'text', u'type': u'string', u'id': u'ANOTHER'}],
                u'valid': True, u'condition': u'AND'}

    formula3 = {u'not': False, u'rules': [
        {u'value': u'df', u'field': u'Course_Code_b', u'operator': u'equal',
         u'input': u'text', u'type': u'string', u'id': u'Course_Code_b'},
        {u'value': u'v2', u'field': u'ANOTHER', u'operator': u'equal',
         u'input': u'text', u'type': u'string', u'id': u'ANOTHER'}],
                u'valid': True, u'condition': u'AND'}

    def compare(self, f1, f2):

        if 'condition' in f1 and 'condition' not in f2:
            return False

        if 'condition' not in f1 and 'condition' in f2:
            return False

        if 'condition' in f1 and 'condition' in f2:
            # Assumes that the literals are in the same order
            return all([self.compare(a, b)
                        for a, b in zip(f1['rules'], f2['rules'])])

        # Dictionaries should have the same items (identically)
        return f1 == f2

    def test(self):

        self.assertTrue(self.compare(self.formula1, self.formula2))

        f3 = formula.rename_variable(
            self.formula1,
            'Course_Code_a',
            'Course_Code_b')

        self.assertTrue(self.compare(self.formula3, f3))

        formula.rename_variable(
            self.formula1,
            'Course_Code_b',
            'Course_Code_a')

    def test_evaluate_formula(self):

        self.assertTrue(
            formula.evaluate(
                self.formula1,
                formula.EVAL_EXP,
                {'Course_Code_a': 'df', 'ANOTHER': 'v2'}))
