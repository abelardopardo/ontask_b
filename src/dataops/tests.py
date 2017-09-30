# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from . import panda_db


class EvaluateExpressionTests(TestCase):
    all_expressions = [
        """{"condition": "AND",
            "rules": [{"id": "UOS_Code",
                       "field": "UOS_Code",
                       "type": "string",
                       "input": "text",
                       "operator": "in",
                       "value": "a, b, c, d"}],
            "not": false,
            "valid": true}""",

        """{"condition": "AND",
            "rules": [{"id": "UOS_Code",
                       "field": "UOS_Code",
                       "type": "string",
                       "input": "text",
                       "operator": "in",
                       "value": "a, b, c, d"},
                      {"id": "email",
                       "field": "email",
                       "type": "string",
                       "input": "text",
                       "operator": "equal",
                       "value": "aaa"}],
            "not": false,
            "valid": true}""",

        """{"condition": "AND",
            "rules": [{"id": "UOS_Code",
                       "field": "UOS_Code",
                       "type": "string",
                       "input": "text",
                       "operator": "in",
                       "value": "a, b, c, d"},
                      {"condition": "AND",
                       "rules": [{"id": "SID",
                                  "field": "SID",
                                  "type": "integer",
                                  "input": "number",
                                  "operator": "equal",
                                  "value": "3"},
                                 {"id": "Surname",
                                  "field": "Surname",
                                  "type": "string",
                                  "input": "text",
                                  "operator": "is_empty", 
                                  "value": null}],
                       "not": false}],
            "not": false,
            "valid": true}""",

        """{"condition": "OR",  
            "rules": [{"id": "INTFIELD",
                       "field": "INTFIELD",      
                       "type": "integer",      
                       "input": "number",      
                       "operator": "equal",      
                       "value": "1"},    
                      {"id": "INTFIELD",      
                       "field": "INTFIELD",      
                       "type": "integer",      
                       "input": "number",      
                       "operator": "not_equal",      
                       "value": "2"},    
                      {"id": "INTFIELD",      
                       "field": "INTFIELD",      
                       "type": "integer",      
                       "input": "number",      
                       "operator": "less",      
                       "value": "3"},   
                      {"id": "INTFIELD",      
                       "field": "INTFIELD",      
                       "type": "integer",      
                       "input": "number",      
                       "operator": "less_or_equal",      
                       "value": "4"},    
                      {"id": "INTFIELD",      
                       "field": "INTFIELD",      
                       "type": "integer",      
                       "input": "number",      
                       "operator": "greater",      
                       "value": "4"},    
                      {"id": "INTFIELD",      
                       "field": "INTFIELD",      
                       "type": "integer",      
                       "input": "number",      
                       "operator": "greater_or_equal",      
                       "value": "5"},    
                      {"id": "INTFIELD",      
                       "field": "INTFIELD",      
                       "type": "integer",      
                       "input": "number",      
                        "operator": "between",      
                        "value": ["4","6"]},
                       {"id": "INTFIELD",      
                        "field": "INTFIELD",      
                        "type": "integer",      
                        "input": "number",      
                        "operator": "not_between",      
                        "value": ["5", "7"]
                       }
                    ],  
            "not": true,  
            "valid": true}"""]

    def evaluate_list_of_expressions(self):
        # Row to dictionary for evaluation
        # dict(zip(df.columns, df.iloc[0]))
        vars = {
            'UOS_Code': 'a',
            'email': 'yeeeaaah',
            'SID': 33444,
            'Surname': 'asdfasdfasdf',
            'INTFIELD': 6
        }

        result = [panda_db.evaluate_top_node(x, vars)
                  for x in self.all_expressions]

        self.assertIs(result, [False, True, False, False])
