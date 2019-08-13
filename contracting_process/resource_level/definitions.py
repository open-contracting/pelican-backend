import functools

from contracting_process.resource_level.coherent import (
    awards_status, contracts_status, dates, period,
    procurement_method_vs_number_of_tenderers, tender_status)
from contracting_process.resource_level.consistent import (
    contracts_value, number_of_tenderers, org_ref_name_consistent, roles,
    tender_value)
from contracting_process.resource_level.reference import (contract_in_awards,
                                                          parties)

definitions = {
    "consistent.number_of_tenderers": [number_of_tenderers.calculate],
    "consistent.tender_value": [tender_value.calculate],
    "consistent.contracts_value": [contracts_value.calculate],
    "consistent.supplier_in_parties_roles": [
        functools.partial(roles.calculate_path_role, path="awards.suppliers", role="supplier")
    ],
    "consistent.tenderer_in_parties_roles": [
        functools.partial(roles.calculate_path_role, path="tender.tenderers", role="tenderer")
    ],
    "consistent.buyer_in_parties_roles": [
        functools.partial(roles.calculate_path_role, path="buyer", role="buyer")
        
    ],
    "consistent.procuring_entity_in_parties_roles": [
        functools.partial(roles.calculate_path_role, path="tender.procuringEntity", role="procuringEntity")
    ],
    "consistent.payer_in_parties_roles": [
        functools.partial(roles.calculate_path_role, path="contracts.implementation.transactions.payer", role="payer")
    ],
    "consistent.payee_in_parties_roles": [
        functools.partial(roles.calculate_path_role, path="contracts.implementation.transactions.payee", role="payee")
    ],
    "reference.supplier_in_parties": [
        functools.partial(parties.calculate_path, path="awards.suppliers"),
        functools.partial(org_ref_name_consistent.calculate, path="awards.suppliers")
    ],
    "reference.tenderer_in_parties": [
        functools.partial(parties.calculate_path, path="tender.tenderers"),
        functools.partial(org_ref_name_consistent.calculate, path="tender.tenderers")
    ],
    "reference.buyer_in_parties": [
        functools.partial(parties.calculate_path, path="buyer"),
        functools.partial(org_ref_name_consistent.calculate, path="buyer")
    ],
    "reference.procuring_entity_in_parties": [
        functools.partial(parties.calculate_path, path="tender.procuringEntity"),
        functools.partial(org_ref_name_consistent.calculate, path="tender.procuringEntity")
    ],
    "reference.payer_in_parties": [
        functools.partial(parties.calculate_path, path="contracts.implementation.transactions.payer"),
        functools.partial(org_ref_name_consistent.calculate, path="contracts.implementation.transactions.payer")
    ],
    "reference.payee_in_parties": [
        functools.partial(parties.calculate_path, path="contracts.implementation.transactions.payee"),
        functools.partial(org_ref_name_consistent.calculate, path="contracts.implementation.transactions.payee")
    ],
    "reference.contract_in_awards": [contract_in_awards.calculate],
    "coherent.procurement_method_vs_number_of_tenderers": [procurement_method_vs_number_of_tenderers.calculate],
    "coherent.tender_status": [tender_status.calculate],
    "coherent.period": [period.calculate],
    "coherent.dates": [dates.calculate],
    "coherent.contracts_status": [contracts_status.calculate],
    "coherent.awards_status": [awards_status.calculate]
}
