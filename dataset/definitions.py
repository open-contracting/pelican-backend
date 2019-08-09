from dataset.distribution import (awards_value, awards_value_repetition, buyer,
                                  contracts_value, contracts_value_repetition,
                                  main_procurement_category, tender_status,
                                  tender_value, tender_value_repetition)
from dataset.misc import url_availability
from dataset.unique import id

definitions = {
    "distribution.main_procurement_category": main_procurement_category,
    "unique.id": id,
    "distribution.contracts_value": contracts_value,
    "distribution.awards_value": awards_value,
    "distribution.tender_value": tender_value,
    "distribution.buyer": buyer,
    "distribution.tender_value_repetition": tender_value_repetition,
    "distribution.awards_value_repetition": awards_value_repetition,
    "distribution.contracts_value_repetition": contracts_value_repetition,
    "distribution.tender_status": tender_status,
    "misc.url_availability": url_availability
}
