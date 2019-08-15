
from tools.checks import get_empty_result_dataset
from tools.getter import get_values

version = 1.0
examples_cap = 100


def add_item(scope, item, item_id):
    if not scope:
        scope = {
            'original_ocid': dict(),
            'related_processes': []
        }

    ocid = item['ocid']
    values = get_values(item, 'tender.title')
    tender_title = values[0]['value'] if values else None

    if ocid and tender_title and ocid not in scope['original_ocid']:
        scope['original_ocid'][ocid] = tender_title

    related_processes = []
    related_processes.extend(
        [el['value'] for el in get_values(item, 'relatedProcesses')]
    )
    related_processes.extend(
        [el['value'] for el in get_values(item, 'contracts.relatedProcesses')]
    )

    for related_process in related_processes:
        # checking if all required fields are set
        if 'scheme' not in related_process or related_process['scheme'] != 'ocid':
            continue

        if 'identifier' not in related_process or related_process['identifier'] is None:
            continue

        if 'title' not in related_process or related_process['title'] is None:
            continue

        scope['related_processes'].append(
            {
                'ocid': related_process['identifier'],
                'title': related_process['title']
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
        if related_process['ocid'] not in scope['original_ocid']:
            continue

        original_process = {
            'ocid': related_process['ocid'],
            'title': scope['original_ocid'][related_process['ocid']]
        }

        passed = related_process['title'] == original_process['title']

        if passed and len(passed_examples) < examples_cap:
            passed_examples.append(
                'original_process': original_process,
                'related_process': related_process,
                'result': passed
            )
        elif not passed and len(failed_examples) < examples_cap:
            failed_examples.append(
                'original_process': original_process,
                'related_process': related_process,
                'result': passed
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
