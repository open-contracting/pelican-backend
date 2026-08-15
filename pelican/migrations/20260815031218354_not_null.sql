ALTER TABLE dataset_level_check
ALTER COLUMN check_name SET NOT NULL;

ALTER TABLE field_level_check_examples
ALTER COLUMN data SET NOT NULL,
ALTER COLUMN path SET NOT NULL;

ALTER TABLE progress_monitor_dataset
ALTER COLUMN state SET NOT NULL,
ALTER COLUMN phase SET NOT NULL;

ALTER TABLE progress_monitor_item
ALTER COLUMN state SET NOT NULL;

ALTER TABLE report
ALTER COLUMN type SET NOT NULL;

ALTER TABLE resource_level_check_examples
ALTER COLUMN data SET NOT NULL,
ALTER COLUMN check_name SET NOT NULL;

ALTER TABLE time_variance_level_check
ALTER COLUMN check_name SET NOT NULL;
