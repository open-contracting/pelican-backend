
from dataset.distribution.distribution_tools import add_item, get_result


global_values_for_check = []


class DocumentDocumentTypePathClass:
    """ PathClass for document.documentType.distribution checker

        This class stores path information for test objects.

    """

    def __init__(self, number_of_samples=20):
        """ Default PathClass constructor
        """
        self.paths = [
            "planning.documents.documentType",
            "tender.documents.documentType",
            "tender.documents.documentType",
            "contracts.documents.documentType",
            "contracts.implementation.documents.documentType",
            "contracts.milestones.documents.documentType"
        ]
        self.important_enums = global_values_for_check
        self.samples_number = number_of_samples

    def add_item(self, scope, item, item_id):
        result = scope
        for current_path in self.paths:
            result = add_item(result, item, item_id,
                              path=current_path, important_values=self.important_enums, samples_num=self.samples_number)
        return result

    def get_result(self, scope):
        return get_result(scope, important_values=self.important_enums)
