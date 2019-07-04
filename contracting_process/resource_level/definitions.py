from contracting_process.consistent import number_of_tenderers
from contracting_process.number_checks import positive_integer
from contracting_process.object_checks import non_empty

definitions = {
    "language": ["language", non_empty],
    "consistent.number_of_tenderers": ["", number_of_tenderers.calculate]
}
