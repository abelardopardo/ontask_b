# -*- coding: utf-8 -*-

from builtins import str
import random

import pandas as pd

from dataops.plugin.ontask_plugin import OnTaskPluginAbstract

# The field class_name contains the name of the class to load to execute the
# plugin.
class_name = 'MSLQEvaluate'


def mslq_encode(answers, num):
    """Function that receives an array of 44 answers and encodes the results
       for the MSLQ survey. It returns the following tuple:

       (IVAL: Intrinsic value,
        SEFF: Self-efficacy,
        TANX: Test anxiety,
        CSUS: Cognitive strategy use,
        SREL: Self-regulation)

        They are the averages of the corresponding questions.

        :param answers: Array of 44 integers encoding the answers
        :param num: Number of possibe answers in each question
    """
    ival_idx = [1, 4, 5, 7, 10, 14, 15, 17, 21]
    seff_idx = [2, 6, 8, 9, 11, 13, 16, 18, 19]
    tanx_idx = [3, 12, 20, 22]
    csus_idx = [23, 24, 26, 28, 29, 30, 31, 34, 36, 39, 41, 42, 44]
    srel_idx = [25, 27, 32, 33, 35, 37, 38, 40, 43]

    # Items with reverse encoding
    reverse_idx = [26, 27, 37, 38]

    # Apply the reverse encoding
    for idx in reverse_idx:
        answers[idx] = num + 1 - answers[idx]

    # Calculate and return the five values
    return (1.0 * sum([answers[i - 1] for i in ival_idx]) / len(ival_idx),
            1.0 * sum([answers[i - 1] for i in seff_idx]) / len(seff_idx),
            1.0 * sum([answers[i - 1] for i in tanx_idx]) / len(tanx_idx),
            1.0 * sum([answers[i - 1] for i in csus_idx]) / len(csus_idx),
            1.0 * sum([answers[i - 1] for i in srel_idx]) / len(srel_idx))


class MSLQEvaluate(OnTaskPluginAbstract):
    """
    Plugin to process the results of the MSLQ test.

    Pintrich, P. R., & de Groot, E. V. (1990). Motivational and self-regulated
    learning components of classroom academic performance. Journal of
    Educational Psychology, 82, 33-40. doi:10.1037//0022-0663.82.1.33

    It assumes 44 input columns named MSLQ_Q01 to MSLQ_Q44.

    It produces 5 output columns with names

    - MSLQ_IVAL: Intrinsic value
    - MSLQ_SEFF: Self efficacy
    - MSLQ_TANX: Test anxiety
    - MSLQ_CSUS: Cognitive Strategy Use
    - MSLQ_SREL: Self-regulation


    The input columns assume one of the following five values:

    'Slightly true of me,'
    'Moderately true of me,'
    'Always true of me,'
    'Never true of me,'
    'Frequently true of me'
    """

    def __init__(self):

        super().__init__()

        self.name = 'MSLQ Score calculation'
        self.description_txt = """Plugin to calculate the scores of MSLQ 
        The names of the columns must be MSLQ_Q01 to MSLQ_Q44."""
        self.input_column_names = [
            'MSLQ_Q01', 'MSLQ_Q02', 'MSLQ_Q03', 'MSLQ_Q04', 'MSLQ_Q05',
            'MSLQ_Q06', 'MSLQ_Q07', 'MSLQ_Q08', 'MSLQ_Q09', 'MSLQ_Q10',
            'MSLQ_Q11', 'MSLQ_Q12', 'MSLQ_Q13', 'MSLQ_Q14', 'MSLQ_Q15',
            'MSLQ_Q16', 'MSLQ_Q17', 'MSLQ_Q18', 'MSLQ_Q19', 'MSLQ_Q20',
            'MSLQ_Q21', 'MSLQ_Q22', 'MSLQ_Q23', 'MSLQ_Q24', 'MSLQ_Q25',
            'MSLQ_Q26', 'MSLQ_Q27', 'MSLQ_Q28', 'MSLQ_Q29', 'MSLQ_Q30',
            'MSLQ_Q31', 'MSLQ_Q32', 'MSLQ_Q33', 'MSLQ_Q34', 'MSLQ_Q35',
            'MSLQ_Q36', 'MSLQ_Q37', 'MSLQ_Q38', 'MSLQ_Q39', 'MSLQ_Q40',
            'MSLQ_Q41', 'MSLQ_Q42', 'MSLQ_Q43', 'MSLQ_Q44',
        ]
        self.output_column_names = ['MSLQ_IVAL', 'MSLQ_SEFF',
                                    'MSLQ_TANX', 'MSLQ_CSUS', 'MSLQ_SREL']
        self.parameters = [
            ('answer_list',
             'string',
             [],
             'Slightly true of me,'
             'Moderately true of me,'
             'Always true of me,'
             'Never true of me,'
             'Frequently true of me',
             'Comma separated list of possible answer values')
        ]

    def run(self, data_frame, parameters=dict):
        """
        Algorithm to encode MSLQ test responses. Creates a data frame to
        be merged with the existing data.

        :param data_frame: Input data for the plugin
        :param parameters: Dictionary with (name, value) pairs.

        :return: a Pandas data_frame to merge with the existing one 
        """

        alist = parameters.get('answer_list')
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
            new_df['MSLQ_Q{:02}'.format(qidx)] = \
                [answer_values.index(x) + 1
                 for x in data_frame['MSLQ_Q{:02}'.format(qidx)]]
        return pd.DataFrame([mslq_encode(x, len(answer_values))
                             for __, x in new_df.iterrows()],
                            columns=self.output_column_names)


def main():
    # Create a synthetic data frame

    num_rows = 20
    answers = ['Slightly true of me',
               'Moderately true of me',
               'Always true of me',
               'Never true of me',
               'Frequently true of me']

    s = pd.Series(['student{:02}@bogus.com'.format(x)
                   for x in range(1, num_rows + 1)])
    df = pd.DataFrame(data=s, columns=['email'])
    for qidx in range(1, 45):
        df['MSLQ_Q{:02}'.format(qidx)] = [answers[random.randint(0, 4)]
                                          for __ in range(num_rows)]

    # df.to_csv('mslq_sample.csv', index=False)
    plugin_instance = MSLQEvaluate()
    result = plugin_instance.run(
        df,
        parameters={'answer_list': ', '.join(answers)})

    print(result)


if __name__ == "__main__":
    main()
