from ontask.dataops.plugin import OnTaskModel

# The field class_name contains the name of the class to load to execute the
# plugin.
class_name = 'LinearRegressionModel'


class LinearRegressionModel(OnTaskModel):
    """
    Class implementing an OnTask plugin that given two coefficients it
    applies a linear regression model to the input column.
    """

    def __init__(self):
        self.name = 'Linear Regression Predictive Model'
        self.description_text = """
        Given a column and the coefficients A and B, it computes the linear 
        model Ax + B, where x is obtained from the input column.
        """
        super().__init__()
        self.input_column_names = list()
        self.output_column_names = ['Linear Model']
        self.parameters = [
            ('A', 'double', [], 0.0, 'Linear coefficient'),
            ('B', 'double', [], 0.0, 'Constant coefficient'),
        ]

    def run(self, data_frame, parameters=None):
        """
        :param data_frame: Input data for the plugin
        :param parameters: Dictionary with (name, value) pairs.
        :return: a Pandas data_frame to merge with the existing one (must
        contain a column with name merge_key)
        """
        # Process the given data and create the result
        result = parameters['A'] * data_frame[self.input_column_names[0]] + \
            parameters['B']

        result.col
        return result
