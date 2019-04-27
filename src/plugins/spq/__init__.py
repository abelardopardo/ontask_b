# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import random

import pandas as pd
from builtins import str

from dataops.plugin import OnTaskPluginAbstract

# The field class_name contains the name of the class to load to execute the
# plugin.
class_name = 'SPQEvaluate'


def spq_encode(answers):
    """Function that receives an array of 20 answers and encodes the results
       for the SPQ survey. It returns the following tuple:

       (DA: Deep approach,
        SA: Surface approach,
        DM: Deep motive,
        SM: Surface motive,
        DS: Deep strategy,
        SS: Surface strategy)

        They are the averages of the corresponding questions.
        :param answers: Array of 20 answers that encodes the results of the
        survey
    """

    dm_idx = [1, 5, 9, 13, 17]
    ds_idx = [2, 6, 10, 14, 18]
    sm_idx = [3, 7, 11, 15, 19]
    ss_idx = [4, 8, 12, 16, 20]

    # Calculate the four accumulations first
    dm_val = 1.0 * sum([answers[i - 1] for i in dm_idx])
    ds_val = 1.0 * sum([answers[i - 1] for i in ds_idx])
    sm_val = 1.0 * sum([answers[i - 1] for i in sm_idx])
    ss_val = 1.0 * sum([answers[i - 1] for i in ss_idx])

    # Return the six values
    return ((dm_val + ds_val) / (len(dm_idx) + len(ds_idx)),
            (sm_val + ss_val) / (len(sm_idx) + len(ss_idx)),
            dm_val / len(dm_idx),
            sm_val / len(sm_idx),
            ds_val / len(ds_idx),
            ss_val / len(ss_idx))


class SPQEvaluate(OnTaskPluginAbstract):
    """
    Plugin to process the results of the SPQ test.

    The possible input values are given as the param answer_list
    """

    def __init__(self):
        self.name = 'SPQ Score calculation'
        self.description_txt = """Plugin to calculate the scores of SPQ
        The names of the columns must be SPQ_Q01 to SPQ_Q44."""
        self.input_column_names = [
            'SPQ_Q01', 'SPQ_Q02', 'SPQ_Q03', 'SPQ_Q04', 'SPQ_Q05',
            'SPQ_Q06', 'SPQ_Q07', 'SPQ_Q08', 'SPQ_Q09', 'SPQ_Q10',
            'SPQ_Q11', 'SPQ_Q12', 'SPQ_Q13', 'SPQ_Q14', 'SPQ_Q15',
            'SPQ_Q16', 'SPQ_Q17', 'SPQ_Q18', 'SPQ_Q19', 'SPQ_Q20'
        ]
        self.output_column_names = ['SPQ_DA', 'SPQ_SA',
                                    'SPQ_DM', 'SPQ_SM',
                                    'SPQ_DS', 'SPQ_SS']
        self.parameters = [
            ('answer_list',
             'string',
             [],
             'Slightly true of me,'
             'Moderately true of me,'
             'Always true of me,'
             'Never true of me,'
             'Frequently true of me',
             'Comma-separated list of possible answer values')
        ]

    def run(self, data_frame, parameters=dict):
        """
        Runs the algorithm and returns a pandas data frame structure that is
        merged with the existing data frame in the workflow 

        :param data_frame: Input data for the plugin
        :param parameters: Dictionary with (name, value) pairs.

        :return: a Pandas data_frame to merge with the existing one 
        """

        alist = parameters.get('answer_list', None)

        if not alist:
            raise Exception('Required parameter "answer_list" not found.')

        if not isinstance(alist, str):
            raise Exception('Parameter "answer_list" must be a string.')

        answer_values = [x.strip() for x in alist.split(',')]

        if not answer_values:
            raise Exception('Parameter "answer_values" must contain the '
                            'comma-separated list of answer values.')

        # Transform text answers to numeric answers
        new_df = pd.DataFrame()
        for qidx in range(1, len(self.input_column_names) + 1):
            new_df['SPQ_Q{:02}'.format(qidx)] = \
                [answer_values.index(x) + 1
                 for x in data_frame['SPQ_Q{:02}'.format(qidx)]]

        return pd.DataFrame([spq_encode(x) for __, x in new_df.iterrows()],
                            columns=self.output_column_names)


def main():
    # Create a synthetic data frame

    plugin_instance = SPQEvaluate()

    num_rows = 20
    answers = plugin_instance.parameters[0][3].split(',')

    s = pd.Series(['student{:02}@bogus.com'.format(x)
                   for x in range(1, num_rows + 1)])
    df = pd.DataFrame(data=s, columns=['email'])
    for qidx in range(1, len(plugin_instance.input_column_names) + 1):
        df['SPQ_Q{:02}'.format(qidx)] = [answers[random.randint(0, 4)]
                                         for __ in range(num_rows)]

    # df.to_csv('spq_sample.csv', index=False)
    result = plugin_instance.run(
        df,
        'email',
        parameters={'answer_list': plugin_instance.parameters[0][3]}
    )

    print(result)


if __name__ == "__main__":
    main()
