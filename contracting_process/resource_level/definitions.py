import functools

from contracting_process.resource_level.coherent import (
    amendments_dates,
    awards_status,
    contracts_status,
    dates,
    documents_dates,
    milestone_status,
    milestones_dates,
    period,
    procurement_method_vs_number_of_tenderers,
    release_date,
    tender_status,
    value_realistic,
)
from contracting_process.resource_level.consistent import (
    contracts_implementation_transactions_value,
    contracts_value,
    number_of_tenderers,
    org_ref_name,
    parties_role,
    period_duration_in_days,
    roles,
    tender_value,
)
from contracting_process.resource_level.reference import contract_in_awards, parties

definitions = {
    # Consistent
    "consistent.number_of_tenderers": number_of_tenderers.calculate,
    "consistent.tender_value": tender_value.calculate,
    "consistent.contracts_value": contracts_value.calculate,
    "consistent.parties_roles": parties_role.calculate,
    "consistent.supplier_in_parties_roles": functools.partial(
        roles.calculate_path_role, path="awards.suppliers", role="supplier"
    ),
    "consistent.tenderer_in_parties_roles": functools.partial(
        roles.calculate_path_role, path="tender.tenderers", role="tenderer"
    ),
    "consistent.buyer_in_parties_roles": functools.partial(roles.calculate_path_role, path="buyer", role="buyer"),
    "consistent.procuring_entity_in_parties_roles": functools.partial(
        roles.calculate_path_role, path="tender.procuringEntity", role="procuringEntity"
    ),
    "consistent.payer_in_parties_roles": functools.partial(
        roles.calculate_path_role, path="contracts.implementation.transactions.payer", role="payer"
    ),
    "consistent.payee_in_parties_roles": functools.partial(
        roles.calculate_path_role, path="contracts.implementation.transactions.payee", role="payee"
    ),
    "consistent.contracts_implementation_transactions_value": contracts_implementation_transactions_value.calculate,
    "consistent.period_duration_in_days": period_duration_in_days.calculate,
    "consistent.supplier_name_in_parties": functools.partial(org_ref_name.calculate, path="awards.suppliers"),
    "consistent.tenderer_name_in_parties": functools.partial(org_ref_name.calculate, path="tender.tenderers"),
    "consistent.buyer_name_in_parties": functools.partial(org_ref_name.calculate, path="buyer"),
    "consistent.procuring_entity_name_in_parties": functools.partial(
        org_ref_name.calculate, path="tender.procuringEntity"
    ),
    "consistent.payer_name_in_parties": functools.partial(
        org_ref_name.calculate, path="contracts.implementation.transactions.payer"
    ),
    "consistent.payee_name_in_parties": functools.partial(
        org_ref_name.calculate, path="contracts.implementation.transactions.payee"
    ),
    # Reference
    "reference.supplier_in_parties": functools.partial(parties.calculate_path, path="awards.suppliers"),
    "reference.tenderer_in_parties": functools.partial(parties.calculate_path, path="tender.tenderers"),
    "reference.buyer_in_parties": functools.partial(parties.calculate_path, path="buyer"),
    "reference.procuring_entity_in_parties": functools.partial(parties.calculate_path, path="tender.procuringEntity"),
    "reference.payer_in_parties": functools.partial(
        parties.calculate_path, path="contracts.implementation.transactions.payer"
    ),
    "reference.payee_in_parties": functools.partial(
        parties.calculate_path, path="contracts.implementation.transactions.payee"
    ),
    "reference.contract_in_awards": contract_in_awards.calculate,
    # Coherent
    "coherent.amendments_dates": amendments_dates.calculate,
    "coherent.awards_status": awards_status.calculate,
    "coherent.contracts_status": contracts_status.calculate,
    "coherent.dates": dates.calculate,
    "coherent.documents_dates": documents_dates.calculate,
    "coherent.milestone_status": milestone_status.calculate,
    "coherent.milestones_dates": milestones_dates.calculate,
    "coherent.period": period.calculate,
    "coherent.procurement_method_vs_number_of_tenderers": procurement_method_vs_number_of_tenderers.calculate,
    "coherent.release_date": release_date.calculate,
    "coherent.tender_status": tender_status.calculate,
    "coherent.value_realistic": value_realistic.calculate,
}
