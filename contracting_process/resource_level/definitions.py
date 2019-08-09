import functools

from contracting_process.resource_level.coherent import (
    awards_status,
    contracts_status,
    dates,
    period,
    procurement_method_vs_number_of_tenderers,
    tender_status
)

from contracting_process.resource_level.consistent import (
    buyer_roles,
    contracts_value,
    number_of_tenderers,
    tender_value
)

from contracting_process.resource_level.reference import (
    parties,
    contract_in_awards
)

definitions = {
    "consistent.number_of_tenderers": [number_of_tenderers.calculate],
    "consistent.buyer_roles": [buyer_roles.calculate],
    "consistent.tender_value": [tender_value.calculate],
    "consistent.contracts_value": [contracts_value.calculate],
    "reference.supplier_in_parties": [
        functools.partial(parties.calculate_path, path="awards.suppliers")
    ],
    "reference.tenderer_in_parties": [
        functools.partial(parties.calculate_path, path="tender.tenderers")
    ],
    "reference.buyer_in_parties": [
        functools.partial(parties.calculate_path, path="buyer")
    ],
    "reference.procuring_entity_in_parties": [
        functools.partial(parties.calculate_path, path="tender.procuringEntity")
    ],
    "reference.payer_in_parties": [
        functools.partial(parties.calculate_path, path="contracts.implementation.transactions.payer")
    ],
    "reference.payee_in_parties": [
        functools.partial(parties.calculate_path, path="contracts.implementation.transactions.payee")
    ],
    "reference.contract_in_awards": [contract_in_awards.calculate],
    "coherent.procurement_method_vs_number_of_tenderers": [procurement_method_vs_number_of_tenderers.calculate],
    "coherent.tender_status": [tender_status.calculate],
    "coherent.period": [period.calculate],
    "coherent.dates": [dates.calculate],
    "coherent.contracts_status": [contracts_status.calculate],
    "coherent.awards_status": [awards_status.calculate]
}
