from contracting_process.resource_level.consistent import number_of_tenderers
from contracting_process.resource_level.reference import supplier_in_parties

definitions = {
    "consistent.number_of_tenderers": [number_of_tenderers.calculate],
    "reference.supplier_in_parties": [supplier_in_parties.calculate]
}
