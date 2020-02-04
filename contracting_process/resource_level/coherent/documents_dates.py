
from tools.checks import get_empty_result_resource
from tools.getter import get_values
from tools.helpers import parse_date

version = 1.0


def calculate(item):
    result = get_empty_result_resource(version)

    date = {
        'value': item['date'] if 'date' in item else None,
        'path': 'date'
    }
    document_paths = [
        'planning.documents',
        'tender.documents',
        'awards.documents',
        'contracts.documents',
        'contracts.implementation.documents'
    ]

    documents = []
    for path in document_paths:
        documents.extend(get_values(item, path))

    failed_paths = []
    result['application_count'] = 0
    result['pass_count'] = 0
    for document in documents:
        date_published = {
            'value': document['value']['datePublished'] if 'datePublished' in document['value'] else None,
            'path': document['path'] + '.datePublished'
        }
        date_modified = {
            'value': document['value']['dateModified'] if 'dateModified' in document['value'] else None,
            'path': document['path'] + '.dateModified'
        }

        # checking document.datePublished and document.dateModified
        first_date = parse_date(date_published['value'])
        second_date = parse_date(date_modified['value'])
        if first_date and second_date:
            result['application_count'] += 1

            if first_date <= second_date:
                result['pass_count'] += 1
            else:
                failed_paths.append(
                    {
                        'path_1': date_published['path'],
                        'value_1': date_published['value'],
                        'path_2': date_modified['path'],
                        'value_2': date_modified['value']
                    }
                )

        # checking document.datePublished and date
        first_date = parse_date(date_published['value'])
        second_date = parse_date(date['value'])
        if first_date and second_date:
            result['application_count'] += 1

            if first_date <= second_date:
                result['pass_count'] += 1
            else:
                failed_paths.append(
                    {
                        'path_1': date_published['path'],
                        'value_1': date_published['value'],
                        'path_2': date['path'],
                        'value_2': date['value']
                    }
                )

        # checking document.dateModified and date
        first_date = parse_date(date_modified['value'])
        second_date = parse_date(date['value'])
        if first_date and second_date:
            result['application_count'] += 1

            if first_date <= second_date:
                result['pass_count'] += 1
            else:
                failed_paths.append(
                    {
                        'path_1': date_modified['path'],
                        'value_1': date_modified['value'],
                        'path_2': date['path'],
                        'value_2': date['value']
                    }
                )

    if result['application_count'] == 0:
        result['application_count'] = None
        result['pass_count'] = None
        result['meta'] = {'reason': 'insufficient data for check'}
    else:
        result['result'] = result['application_count'] == result['pass_count']
        if not result['result']:
            result['meta'] = {
                'failed_paths': failed_paths
            }

    return result
