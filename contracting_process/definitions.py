from contracting_process.number_checks import positive_integer
from contracting_process.object_checks import non_empty

definitions = {
    "tender": [non_empty],
    "tender.items.id": [positive_integer],
    "parties.id": [positive_integer],
    "parties.roles": [positive_integer],
}
