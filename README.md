# Pelican backend

## Getting started

Install development dependencies:

```shell
pip install pip-tools
pip-sync requirements_dev.txt
```

Set up the git pre-commit hook:

```shell
pre-commit install
```

[Developer documentation](https://docs.google.com/document/d/1cfunGPyP-QLHOeQT3olFEHJh0J_aieUJZzxirT7Y8wk/edit)

## Develop

Start workers:

```shell
python -m core.finisher [environment]
python -m checker.time_variance_checker [environment]
python -m checker.dataset [environment]
python -m checker.contracting_process [environment]
python -m extractor.ocds_kingfisher [environment]
python -m core.starter [environment] [name_in_database] [kingfisher_collection_id] [num_of_items_to_download:optional]
```

To restart a job, send this message to RabbitMQ:

```
{"resend", "dataset_id": [dataset.id_in_postgres]}
```

* If published to the *dqt_development_ocds_kingfisher_extractor_init* queue, work is resumed at `checker.contracting_process`
* If published to the *dqt_development_ocds_kingfisher_extractor* queue, work is resumed at `checker.dataset`

Reset the database:

```shell
psql DBNAME -f migrations/truncate.sql
```

## Test

```shell
pytest
```
