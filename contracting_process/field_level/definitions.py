from contracting_process.field_level.number_checks import positive_integer
from contracting_process.field_level.object_checks import exists, non_empty

definitions = {
    "parties.id": [exists, non_empty],
    "parties.ids": [exists, non_empty],
    "language": [exists, non_empty],
    "publisher.name": [exists, non_empty],
}
