# Pelican backend

Pelican backend ingests OCDS data and measures its quality.

## Getting started

Install development dependencies:

```bash
pip install pip-tools
pip-sync requirements_dev.txt
```

Set up the git pre-commit hook:

```bash
pre-commit install
```

[Developer documentation](https://docs.google.com/document/d/1cfunGPyP-QLHOeQT3olFEHJh0J_aieUJZzxirT7Y8wk/edit)

## Contributing

### Design

Pelican is focused on data quality. It supports an interrogation of the quality of a dataset, rather than an exploration of the data that it contains. As such, it is not designed to support many features that are more appropriate to exploration.

It is also focused on *intrinsic* quality rather than *extrinsic* quality. That said, it can include intrinsic metrics that are easy to calculate (like the number of contracting processes) to support extrinsic metrics (like the proportion of all contracts covered by the dataset).

### Development

Start workers:

```bash
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

```bash
psql DBNAME -f migrations/truncate.sql
```

## Test

```bash
pytest
```
