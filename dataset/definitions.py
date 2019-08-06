from dataset.distribution import (awards_value, contracts_value,
                                  main_procurement_category, tender_value)
from dataset.unique import id
from dataset.misc import url_availability

definitions = {
    "distribution.main_procurement_category": main_procurement_category,
    "unique.id": id,
    "distribution.contracts_value": contracts_value,
    "distribution.awards_value": awards_value,
    "distribution.tender_value": tender_value,
    "misc.url_availability": url_availability
}
