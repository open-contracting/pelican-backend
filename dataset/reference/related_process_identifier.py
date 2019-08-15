
from tools.checks import get_empty_result_dataset
from tools.getter import get_values

version = 1.0
examples_cap = 100


def add_item(scope, item, item_id):
    if not scope:
        scope = {
            'original_ocid': set(),
            'related_processes': []
        }

    ocid = item['ocid']

    if ocid:
        scope['original_ocid'].add(ocid)

    related_processes = []
    related_processes.extend(get_values(item, 'relatedProcesses'))
    related_processes.extend(get_values(item, 'contracts.relatedProcesses'))

    for related_process in related_processes:
        # checking if all required fields are set
        if 'scheme' not in related_process['value'] or related_process['value']['scheme'] != 'ocid':
            continue

        if 'identifier' not in related_process['value'] or related_process['value']['identifier'] is None:
            continue

        scope['related_processes'].append(
            {
                'ocid': ocid,
                'related_ocid': related_process['value']['identifier'],
                'related_path': related_process['path']
            }
        )

    return scope


def get_result(scope):
    result = get_empty_result_dataset(version)

    application_count = 0
    pass_count = 0
    passed_examples = []
    failed_examples = []

    for related_process in scope['related_processes']:
        passed = related_process['related_ocid'] in scope['original_ocid']

        if passed and len(passed_examples) < examples_cap:
            passed_examples.append(
                {
                    'related_process': related_process,
                    'result': passed
                }
            )
        elif not passed and len(failed_examples) < examples_cap:
            failed_examples.append(
                {
                    'related_process': related_process,
                    'result': passed
                }
            )

        application_count += 1
        pass_count = pass_count + 1 if passed else pass_count

    if application_count == 0:
        result['meta'] = {
            'reason': 'there are no pairs of related processes with check-specific properties'
        }
    else:
        result['result'] = application_count == pass_count
        result['value'] = 100 * (pass_count / application_count)
        result['meta'] = {
            'total_processed': application_count,
            'total_passed': pass_count,
            'total_failed': application_count - pass_count,
            'passed_examples': passed_examples,
            'failed_examples': failed_examples
        }

    return result
