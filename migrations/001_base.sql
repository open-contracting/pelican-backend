DROP SCHEMA IF EXISTS development CASCADE;

CREATE SCHEMA development;

SET search_path TO development;

CREATE TABLE progress_monitor_dataset (
    id SERIAL PRIMARY KEY,
    dataset_id character varying(255),
    state character varying(255),
    phase character varying(255),
    size integer,
    created timestamp without time zone,
    modified timestamp without time zone
);

CREATE INDEX progress_monitor_dataset_modified_idx ON progress_monitor_dataset (modified);
CREATE UNIQUE INDEX progress_monitor_dataset_dataset_id_idx ON progress_monitor_dataset (dataset_id);
CREATE INDEX progress_monitor_dataset_state_idx ON progress_monitor_dataset (state);
CREATE INDEX progress_monitor_dataset_phase_idx ON progress_monitor_dataset (phase);

ALTER TABLE progress_monitor_dataset
ADD CONSTRAINT unique_dataset_id
UNIQUE USING INDEX progress_monitor_dataset_dataset_id_idx;


CREATE TABLE progress_monitor_item (
    id SERIAL PRIMARY KEY,
    dataset_id character varying(255),
    item_id character varying(255),
    state character varying(255),
    created timestamp without time zone,
    modified timestamp without time zone
);

CREATE INDEX progress_monitor_item_modified_idx ON progress_monitor_item (modified);
CREATE INDEX progress_monitor_item_dataset_id_idx ON progress_monitor_item (dataset_id);
CREATE INDEX progress_monitor_item_item_id_idx ON progress_monitor_item (item_id);
CREATE INDEX progress_monitor_item_state_idx ON progress_monitor_item (state);
CREATE UNIQUE INDEX unique_dataset_id_item_id ON progress_monitor_item (dataset_id, item_id);

ALTER TABLE progress_monitor_item
ADD CONSTRAINT unique_dataset_id_item_id
UNIQUE USING INDEX unique_dataset_id_item_id;