from dataset.distribution import (
    buyer,
    main_procurement_category,
    value_repetition,
    value,
    code_distribution
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
    "distribution.main_procurement_category": main_procurement_category, "unique.id": id,
    "distribution.contracts_value": value.ModuleType("contracts.value"),
    "distribution.awards_value": value.ModuleType("awards.value"),
    "distribution.tender_value": value.ModuleType("tender.value"),
    "distribution.buyer": buyer, "distribution.tender_value_repetition": value_repetition.ModuleType("tender"),
    "distribution.awards_value_repetition": value_repetition.ModuleType("awards"),
    "distribution.contracts_value_repetition": value_repetition.ModuleType("contracts"),
    "distribution.tender_procurement_method": code_distribution.CodeDistribution(
        ["tender.procurementMethod"],
        ["open"]),
    "distribution.tender_status": code_distribution.CodeDistribution(
        ["tender.status"],
        ["planning", "planned", "active", "cancelled", "unsuccessful", "complete", "withdrawn"]),
    "distribution.tender_award_criteria": code_distribution.CodeDistribution(["tender.awardCriteria"]),
    "distribution.tender_submission_method": code_distribution.CodeDistribution(
        ["tender.submissionMethod.distribution"]),
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
        ["planning.documents.documentType", "tender.documents.documentType", "tender.documents.documentType",
         "contracts.documents.documentType", "contracts.implementation.documents.documentType",
         "contracts.milestones.documents.documentType"]),
    "distribution.value_currency": code_distribution.CodeDistribution(
        ["tender.value.currency", "tender.minValue.currency", "awards.value.currency", "contracts.value.currency",
         "planning.budget.value.currency", "contracts.implementation.transactions.value"]),
    "distribution.related_process_relation": code_distribution.CodeDistribution(["relatedProcess.relationship"]),
    "misc.url_availability": url_availability, "consistent.related_process_title": related_process_title,
    "reference.related_process_identifier": related_process_identifier}
