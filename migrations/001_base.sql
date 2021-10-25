CREATE TABLE dataset (
    id bigserial PRIMARY KEY,
    name character varying(255),
    meta jsonb,
    ancestor_id bigint,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX dataset_name_idx ON dataset (name);

CREATE INDEX dataset_meta_idx ON dataset USING gin (meta jsonb_path_ops);

CREATE INDEX dataset_created_idx ON dataset (created);

CREATE INDEX dataset_modified_idx ON dataset (modified);

CREATE TABLE dataset_filter (
    id bigserial PRIMARY KEY,
    dataset_id_original bigint,
    dataset_id_filtered bigint,
    filter_message jsonb,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX dataset_filter_filter_message_idx ON dataset_filter USING gin (filter_message jsonb_path_ops);

CREATE INDEX dataset_filter_dataset_id_original_idx ON dataset_filter (dataset_id_original);

CREATE INDEX dataset_filter_dataset_id_filtered_idx ON dataset_filter (dataset_id_filtered);

CREATE INDEX dataset_filter_created_idx ON dataset_filter (created);

CREATE INDEX dataset_filter_modified_idx ON dataset_filter (modified);

CREATE TYPE report_type AS ENUM (
    'field_level_check',
    'resource_level_check',
    'dataset_level_check'
);

CREATE TABLE report (
    id bigserial PRIMARY KEY,
    dataset_id bigint,
    type report_type,
    data jsonb,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX report_dataset_id_idx ON report (dataset_id);

CREATE INDEX type_report_idx ON report (type);

CREATE INDEX report_data_idx ON report USING gin (data jsonb_path_ops);

CREATE INDEX report_modified_idx ON report (modified);

CREATE TABLE progress_monitor_dataset (
    id bigserial PRIMARY KEY,
    dataset_id bigint,
    state character varying(255),
    phase character varying(255),
    size integer,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX progress_monitor_dataset_modified_idx ON progress_monitor_dataset (modified);

CREATE UNIQUE INDEX progress_monitor_dataset_dataset_id_idx ON progress_monitor_dataset (dataset_id);

CREATE INDEX progress_monitor_dataset_state_idx ON progress_monitor_dataset (state);

CREATE INDEX progress_monitor_dataset_phase_idx ON progress_monitor_dataset (phase);

ALTER TABLE progress_monitor_dataset
    ADD CONSTRAINT unique_dataset_id UNIQUE USING INDEX progress_monitor_dataset_dataset_id_idx;

CREATE TABLE progress_monitor_item (
    id bigserial PRIMARY KEY,
    dataset_id bigint,
    item_id character varying(255),
    state character varying(255),
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX progress_monitor_item_modified_idx ON progress_monitor_item (modified);

CREATE INDEX progress_monitor_item_dataset_id_idx ON progress_monitor_item (dataset_id);

CREATE INDEX progress_monitor_item_item_id_idx ON progress_monitor_item (item_id);

CREATE INDEX progress_monitor_item_state_idx ON progress_monitor_item (state);

CREATE UNIQUE INDEX unique_dataset_id_item_id ON progress_monitor_item (dataset_id, item_id);

ALTER TABLE progress_monitor_item
    ADD CONSTRAINT unique_dataset_id_item_id UNIQUE USING INDEX unique_dataset_id_item_id;

CREATE TABLE data_item (
    id bigserial PRIMARY KEY,
    data jsonb,
    dataset_id bigint,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX data_item_data_idx ON data_item USING gin (data jsonb_path_ops);

CREATE INDEX data_item_modified_idx ON data_item (modified);

CREATE INDEX data_item_dataset_id_idx ON data_item (dataset_id);

CREATE INDEX data_item_ocid_idx ON data_item ((data ->> 'ocid'));

ALTER INDEX data_item_ocid_idx
    ALTER COLUMN expr SET STATISTICS 10000;

ALTER TABLE data_item
    ALTER COLUMN dataset_id SET STATISTICS 10000;

CREATE TABLE field_level_check (
    id bigserial PRIMARY KEY,
    data_item_id bigint,
    dataset_id bigint,
    result jsonb,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX field_level_check_result_idx ON field_level_check USING gin (result jsonb_path_ops);

CREATE INDEX field_level_check_data_item_id_idx ON field_level_check (data_item_id);

CREATE INDEX field_level_check_dataset_id_idx ON field_level_check (dataset_id);

CREATE INDEX field_level_check_modified_idx ON field_level_check (modified);

CREATE TABLE field_level_check_examples (
    id bigserial PRIMARY KEY,
    dataset_id bigint,
    data jsonb,
    path varchar,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX field_level_check_examples_data_idx ON field_level_check_examples USING gin (data jsonb_path_ops);

CREATE INDEX field_level_check_examples_dataset_id_idx ON field_level_check_examples (dataset_id);

CREATE INDEX field_level_check_examples_path_idx ON field_level_check_examples (path);

CREATE INDEX field_level_check_examples_modified_idx ON field_level_check_examples (modified);

CREATE TABLE resource_level_check (
    id bigserial PRIMARY KEY,
    data_item_id bigint,
    dataset_id bigint,
    result jsonb,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX resource_level_check_result_idx ON resource_level_check USING gin (result jsonb_path_ops);

CREATE INDEX resource_level_check_data_item_id_idx ON resource_level_check (data_item_id);

CREATE INDEX resource_level_check_dataset_id_idx ON resource_level_check (dataset_id);

CREATE INDEX resource_level_check_modified_idx ON resource_level_check (modified);

CREATE TABLE resource_level_check_examples (
    id bigserial PRIMARY KEY,
    dataset_id bigint,
    data jsonb,
    check_name varchar,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX resource_level_check_examples_data_idx ON resource_level_check_examples USING gin (data jsonb_path_ops);

CREATE INDEX resource_level_check_examples_dataset_id_idx ON resource_level_check_examples (dataset_id);

CREATE INDEX resource_level_check_examples_check_name_idx ON resource_level_check_examples (check_name);

CREATE INDEX resource_level_check_examples_modified_idx ON resource_level_check_examples (modified);

CREATE TABLE dataset_level_check (
    id bigserial PRIMARY KEY,
    check_name character varying,
    result boolean,
    value int,
    meta jsonb,
    dataset_id bigint,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX dataset_level_check_dataset_id_idx ON dataset_level_check (dataset_id);

CREATE INDEX dataset_level_check_modified_idx ON dataset_level_check (modified);

CREATE TABLE time_variance_level_check (
    id bigserial PRIMARY KEY,
    check_name character varying,
    coverage_result boolean,
    coverage_value int,
    check_result boolean,
    check_value int,
    meta jsonb,
    dataset_id bigint,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX time_variance_level_check_dataset_id_idx ON time_variance_level_check (dataset_id);

CREATE INDEX time_variance_level_check_modified_idx ON time_variance_level_check (modified);

CREATE TABLE exchange_rates (
    id bigserial PRIMARY KEY,
    valid_on date NOT NULL UNIQUE,
    rates jsonb NOT NULL,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX exchange_rates_rates_idx ON exchange_rates USING gin (rates jsonb_path_ops);

CREATE INDEX exchange_rates_valid_on_idx ON exchange_rates (valid_on);
