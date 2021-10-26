ALTER TABLE ONLY data_item
    ALTER COLUMN data SET NOT NULL,
    ALTER COLUMN dataset_id SET NOT NULL,
    ADD CONSTRAINT data_item_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES dataset(id);

ALTER TABLE ONLY dataset
    ALTER COLUMN name SET NOT NULL,
    ALTER COLUMN meta SET NOT NULL;

ALTER TABLE ONLY dataset_filter
    ALTER COLUMN dataset_id_original SET NOT NULL,
    ALTER COLUMN dataset_id_filtered SET NOT NULL,
    ALTER COLUMN filter_message SET NOT NULL,
    ADD CONSTRAINT dataset_filter_dataset_id_filtered_fkey FOREIGN KEY (dataset_id_filtered) REFERENCES dataset(id),
    ADD CONSTRAINT dataset_filter_dataset_id_original_fkey FOREIGN KEY (dataset_id_original) REFERENCES dataset(id);

ALTER TABLE ONLY dataset_level_check
    ALTER COLUMN meta SET NOT NULL,
    ALTER COLUMN dataset_id SET NOT NULL,
    ADD CONSTRAINT dataset_level_check_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES dataset(id);

ALTER TABLE ONLY field_level_check
    ADD CONSTRAINT field_level_check_data_item_id_fkey FOREIGN KEY (data_item_id) REFERENCES data_item(id);

ALTER TABLE ONLY field_level_check
    ALTER COLUMN data_item_id SET NOT NULL,
    ALTER COLUMN dataset_id SET NOT NULL,
    ALTER COLUMN result SET NOT NULL,
    ADD CONSTRAINT field_level_check_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES dataset(id);

ALTER TABLE ONLY field_level_check_examples
    ALTER COLUMN dataset_id SET NOT NULL,
    ADD CONSTRAINT field_level_check_examples_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES dataset(id);

ALTER TABLE ONLY progress_monitor_dataset
    ALTER COLUMN dataset_id SET NOT NULL,
    ADD CONSTRAINT progress_monitor_dataset_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES dataset(id);

ALTER TABLE ONLY progress_monitor_item
    ALTER COLUMN item_id TYPE bigint USING item_id::bigint,
    ALTER COLUMN dataset_id SET NOT NULL,
    ALTER COLUMN item_id SET NOT NULL,
    ADD CONSTRAINT progress_monitor_item_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES dataset(id),
    ADD CONSTRAINT progress_monitor_item_item_id_fkey FOREIGN KEY (item_id) REFERENCES data_item(id);

ALTER TABLE ONLY report
    ALTER COLUMN dataset_id SET NOT NULL,
    ALTER COLUMN data SET NOT NULL,
    ADD CONSTRAINT report_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES dataset(id);

ALTER TABLE ONLY resource_level_check
    ALTER COLUMN data_item_id SET NOT NULL,
    ALTER COLUMN dataset_id SET NOT NULL,
    ALTER COLUMN result SET NOT NULL,
    ADD CONSTRAINT resource_level_check_data_item_id_fkey FOREIGN KEY (data_item_id) REFERENCES data_item(id),
    ADD CONSTRAINT resource_level_check_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES dataset(id);

ALTER TABLE ONLY resource_level_check_examples
    ALTER COLUMN dataset_id SET NOT NULL,
    ADD CONSTRAINT resource_level_check_examples_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES dataset(id);

ALTER TABLE ONLY time_variance_level_check
    ALTER COLUMN meta SET NOT NULL,
    ALTER COLUMN dataset_id SET NOT NULL,
    ADD CONSTRAINT time_variance_level_check_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES dataset(id);

