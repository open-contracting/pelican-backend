from dataset.distribution import (
    buyer,
    main_procurement_category,
    tender_status,
    value_repetition,
    value,
    tender_procurement_method
)

from dataset.misc import (
    url_availability
)

from dataset.unique import (
    id
)

from dataset.consistent import (
    related_process_title
)

from dataset.reference import (
    related_process_identifier
)

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
    "distribution.tender_procurement_method": tender_procurement_method.TenderProcurementMethodPathClass(),
    "distribution.tender_status": tender_status.TenderStatusPathClass(),
    "misc.url_availability": url_availability,
    "consistent.related_process_title": related_process_title,
    "reference.related_process_identifier": related_process_identifier
}
