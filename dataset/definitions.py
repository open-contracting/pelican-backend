from dataset.distribution import (buyer,
                                  main_procurement_category,
                                  tender_status,
                                  value_repetition,
                                  value)
from dataset.misc import url_availability
from dataset.unique import id

definitions = {
    "distribution.main_procurement_category": main_procurement_category,
    "unique.id": id,
    "distribution.contracts_value": value.ModuleType("contracts.value"),
    "distribution.awards_value": value.ModuleType("awards.value"),
    "distribution.tender_value": value.ModuleType("tender.value"),
    "distribution.buyer": buyer,
    "distribution.tender_value_repetition": value_repetition.ModuleType("tender"),
    "distribution.awards_value_repetition": value_repetition.ModuleType("awards"),
    "distribution.contracts_value_repetition": value_repetition.ModuleType("contracts"),
    "distribution.tender_status": tender_status,
    "misc.url_availability": url_availability
}
