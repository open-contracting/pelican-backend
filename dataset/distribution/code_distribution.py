from dataset.distribution.distribution_tools import add_item, get_result


class CodeDistribution:
    """ Code distribution check class

        This class stores path information and list of input values for test objects.

        paths : list
            list of paths in which enum can be
        input_values : list
            list of input values that are important to us
        samples_number : int
            desired amount of samples in result["meta"]["shares"][eum (1)]["examples"]
            1 - any found enum
    """

    def __init__(self, paths_param, input_values=[], samples_number=20):
        """ Default constructor

        """
        self.paths = paths_param
        self.important_enums = input_values
        self.samples_number = samples_number

    def add_item(self, scope, item, item_id):
        result = scope
        for current_path in self.paths:
            result = add_item(result, item, item_id,
                              path=current_path, important_values=self.important_enums, samples_num=self.samples_number)
        return result

    def get_result(self, scope):
        return get_result(scope, important_values=self.important_enums)
