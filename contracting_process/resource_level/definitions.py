from contracting_process.resource_level.coherent import (
    dates, period, procurement_method_vs_number_of_tenderers, tender_status)
from contracting_process.resource_level.consistent import (buyer_roles,
                                                           number_of_tenderers,
                                                           tender_value,
                                                           contracts_value)
                                                           
from contracting_process.resource_level.reference import (
    buyer_in_parties, contract_in_awards, payee_in_parties, payer_in_parties,
    procuring_entity_in_parties, supplier_in_parties, tenderer_in_parties)

definitions = {
    "consistent.number_of_tenderers": [number_of_tenderers.calculate],
    "consistent.buyer_roles": [buyer_roles.calculate],
    "consistent.tender_value": [tender_value.calculate],
    "consistent.contracts_value": [contracts_value.calculate],
    "reference.supplier_in_parties": [supplier_in_parties.calculate],
    "reference.tenderer_in_parties": [tenderer_in_parties.calculate],
    "reference.buyer_in_parties": [buyer_in_parties.calculate],
    "reference.procuring_entity_in_parties": [procuring_entity_in_parties.calculate],
    "reference.payer_in_parties": [payer_in_parties.calculate],
    "reference.payee_in_parties": [payee_in_parties.calculate],
    "reference.contract_in_awards": [contract_in_awards.calculate],
    "coherent.procurement_method_vs_number_of_tenderers": [procurement_method_vs_number_of_tenderers.calculate],
    "coherent.tender_status": [tender_status.calculate],
    "coherent.period": [period.calculate],
    "coherent.dates": [dates.calculate]
}
