from dataset.consistent import related_process_title
from dataset.distribution import (
    buyer,
    buyer_repetition,
    code_distribution,
    main_procurement_category,
    value,
    value_repetition,
)
from dataset.misc import url_availability
from dataset.reference import related_process_identifier
from dataset.unique import tender_id
from pelican.util.schema import get_paths

definitions = {
    "distribution.main_procurement_category": main_procurement_category,
    "unique.tender_id": tender_id,
    "distribution.contracts_value": value.ModuleType("contracts.value"),
    "distribution.awards_value": value.ModuleType("awards.value"),
    "distribution.tender_value": value.ModuleType("tender.value"),
    "distribution.buyer": buyer,
    "distribution.buyer_repetition": buyer_repetition,
    "distribution.tender_value_repetition": value_repetition.ModuleType("tender"),
    "distribution.awards_value_repetition": value_repetition.ModuleType("awards"),
    "distribution.contracts_value_repetition": value_repetition.ModuleType("contracts"),
    "distribution.tender_procurement_method": code_distribution.CodeDistribution(
        ["tender.procurementMethod"],
        ["open"],
    ),
    "distribution.tender_status": code_distribution.CodeDistribution(
        ["tender.status"],
        ["active", "complete"],
    ),
    "distribution.tender_award_criteria": code_distribution.CodeDistribution(
        ["tender.awardCriteria"],
    ),
    "distribution.tender_submission_method": code_distribution.CodeDistribution(
        ["tender.submissionMethod"],
    ),
    "distribution.awards_status": code_distribution.CodeDistribution(
        ["awards.status"],
        ["active"],
    ),
    "distribution.contracts_status": code_distribution.CodeDistribution(
        ["contracts.status"],
        ["active", "terminated"],
    ),
    "distribution.milestone_status": code_distribution.CodeDistribution(
        [f"{path}.status" for path in get_paths("Milestone")],
        ["met"],
    ),
    "distribution.milestone_type": code_distribution.CodeDistribution(
        [f"{path}.type" for path in get_paths("Milestone")]
    ),
    "distribution.document_document_type": code_distribution.CodeDistribution(
        [f"{path}.documentType" for path in get_paths("Document")]
    ),
    "distribution.value_currency": code_distribution.CodeDistribution(
        [f"{path}.currency" for path in get_paths("Value")]
    ),
    "distribution.related_process_relation": code_distribution.CodeDistribution(
        [f"{path}.relationship" for path in get_paths("RelatedProcess")]
    ),
    "misc.url_availability": url_availability,
    "consistent.related_process_title": related_process_title,
    "reference.related_process_identifier": related_process_identifier,
}
