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
        ["open"]),
    "distribution.tender_status": code_distribution.CodeDistribution(
        ["tender.status"],
        ["active", "complete"]),
    "distribution.tender_award_criteria": code_distribution.CodeDistribution(["tender.awardCriteria"]),
    "distribution.tender_submission_method": code_distribution.CodeDistribution(
        ["tender.submissionMethod"]),
    "distribution.awards_status": code_distribution.CodeDistribution(
        ["awards.status"],
        ["active"]),
    "distribution.contracts_status": code_distribution.CodeDistribution(
        ["contracts.status"],
        ["active", "terminated"]),
    "distribution.milestone_status": code_distribution.CodeDistribution(
        ["planning.milestones.status", "tender.milestones.status", "contracts.milestones.status",
         "contracts.implementation.milestones.status"],
        ["met"]),
    "distribution.milestone_type": code_distribution.CodeDistribution(
        ["planning.milestones.type", "tender.milestones.type", "contracts.milestones.type",
         "contracts.implementation.milestones.type"]),
    "distribution.document_document_type": code_distribution.CodeDistribution(
        ["planning.documents.documentType", "tender.documents.documentType",
         "contracts.documents.documentType", "contracts.implementation.documents.documentType",
         "awards.documents.documentType"]),
    "distribution.value_currency": code_distribution.CodeDistribution(
        ["tender.value.currency", "tender.minValue.currency", "awards.value.currency", "contracts.value.currency",
         "planning.budget.value.currency", "contracts.implementation.transactions.value.currency"]),
    "distribution.related_process_relation": code_distribution.CodeDistribution(
        ["relatedProcesses.relationship", "contracts.relatedProcesses.relationship"]
    ),
    "misc.url_availability": url_availability,
    "consistent.related_process_title": related_process_title,
    "reference.related_process_identifier": related_process_identifier}
