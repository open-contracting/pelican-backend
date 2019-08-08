from dataset.distribution import (awards_value, contracts_value,
                                  main_procurement_category, tender_value, buyer)
from dataset.unique import id

definitions = {
    "distribution.main_procurement_category": main_procurement_category,
    "unique.id": id,
    "distribution.contracts_value": contracts_value,
    "distribution.awards_value": awards_value,
    "distribution.tender_value": tender_value,
    "distribution.buyer": buyer
}
