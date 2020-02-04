

import click

from tools.bootstrap import bootstrap
from tools.db import commit, get_cursor, rollback
from tools.logging_helper import get_logger


@click.command()
@click.argument("environment")
@click.argument("dataset_id")
def run(environment, dataset_id):
    bootstrap(environment, "delete_dataset")

    global logger
    logger = get_logger()

    global cursor
    cursor = get_cursor()

    logger.info("Script initialized")

    cursor.execute(
        """
        select exists (
            select 1
            from dataset
            where id = %s
        );
        """, [dataset_id]
    )
    if not cursor.fetchall()[0][0]:
        logger.error(f'Dataset with dataset_id {dataset_id} does not exist.')
        return

    logger.info(f'Deleting dataset with dataset_id {dataset_id}.')
    cursor.execute(
        """
        delete from dataset
        where id = %(dataset_id)s;

        delete from report
        where dataset_id = %(dataset_id)s;

        delete from progress_monitor_dataset
        where dataset_id = %(dataset_id)s;

        delete from progress_monitor_item
        where dataset_id = %(dataset_id)s;

        delete from data_item
        where dataset_id = %(dataset_id)s;

        delete from field_level_check
        where dataset_id = %(dataset_id)s;

        delete from field_level_check_examples
        where dataset_id = %(dataset_id)s;

        delete from resource_level_check
        where dataset_id = %(dataset_id)s;

        delete from resource_level_check_examples
        where dataset_id = %(dataset_id)s;

        delete from dataset_level_check
        where dataset_id = %(dataset_id)s;

        delete from time_variance_level_check
        where dataset_id = %(dataset_id)s;
        """, {'dataset_id': dataset_id}
    )
    commit()

    logger.info(f'Dataset with dataset_id {dataset_id} has been deleted.')


if __name__ == '__main__':
    run()
