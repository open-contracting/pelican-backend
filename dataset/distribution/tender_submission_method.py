
from dataset.distribution.distribution_tools import add_item, get_result


global_values_for_check = []


class TenderSubmissionMethodPathClass:
    """ PathClass for tender.submissionMethod.distribution checker

        This class stores path information for test objects.

    """

    def __init__(self, number_of_samples=20):
        """ Default PathClass constructor
        """
        self.path = "tender.submissionMethod.distribution"
        self.important_enums = global_values_for_check
        self.samples_number = number_of_samples

    def add_item(self, scope, item, item_id):
        return add_item(scope, item, item_id,
                        path=self.path, important_values=self.important_enums, samples_num=self.samples_number)

    def get_result(self, scope):
        return get_result(scope, important_values=self.important_enums)
