-- Regarding GIN indexes, pelican-backend doesn't use the key-exists operators ?, ?| or ?&, the containment operator
-- @>, or the jsonpath match operators @? and @@. pelican-frontend uses the key-exists operator ? (has_key).
-- https://www.postgresql.org/docs/current/datatype-json.html#JSON-INDEXING
-- https://docs.djangoproject.com/en/4.2/topics/db/queries/#querying-jsonfield

CREATE TABLE dataset (
    id bigserial PRIMARY KEY,
    name character varying(255),
    meta jsonb,
    ancestor_id bigint,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- pelican-frontend/backend/api/views.py (find_by_name)
CREATE INDEX dataset_name_idx ON dataset (name);

CREATE TABLE dataset_filter (
    id bigserial PRIMARY KEY,
    dataset_id_original bigint,
    dataset_id_filtered bigint,
    filter_message jsonb,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- manage.py
CREATE INDEX dataset_filter_dataset_ids_idx ON dataset_filter (dataset_id_original, dataset_id_filtered);

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

-- Column referencing foreign key, plus type and data.
-- contracting_process/field_level/report_examples.py
-- contracting_process/resource_level/report.py
-- pelican-frontend/backend/api/views.py (field_level_report, compiled_release_level_report)
-- The key-exists operators ? (has_key) is used in:
-- pelican-frontend/backend/api/views.py (FieldLevelDetail, ResourceLevelDetail)
-- pelican-frontend/backend/exporter/template_tags/field.py
-- pelican-frontend/backend/exporter/template_tags/resource.py
CREATE INDEX report_dataset_id_type_data_idx ON report USING gin (dataset_id, type, data);

CREATE TABLE progress_monitor_dataset (
    id bigserial PRIMARY KEY,
    dataset_id bigint,
    state character varying(255),
    phase character varying(255),
    size integer,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Column referencing foreign key, plus phase or with unique constraint.
-- workers/extract/dataset_filter.py
CREATE INDEX progress_monitor_dataset_dataset_id_phase_idx ON progress_monitor_dataset (dataset_id, phase);
ALTER TABLE progress_monitor_dataset
    ADD CONSTRAINT unique_dataset_id UNIQUE (dataset_id);

CREATE TABLE progress_monitor_item (
    id bigserial PRIMARY KEY,
    dataset_id bigint,
    item_id character varying(255),
    state character varying(255),
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Column referencing foreign key, plus state or item_id.
CREATE INDEX progress_monitor_item_item_id_idx ON progress_monitor_item (item_id);
-- get_processed_items_count()
CREATE INDEX progress_monitor_item_dataset_id_state_idx ON progress_monitor_item (dataset_id, state);
-- update_items_state()
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

-- Column referencing foreign key, plus ocid.
-- time_variance/processor.py
CREATE INDEX data_item_dataset_id_ocid_idx ON data_item (dataset_id, (data ->> 'ocid'));

-- data_item is the largest and most frequently queried table, so rarely used indexes are avoided. The queries in
-- workers/extract/dataset_filter.py and pelican-frontend/backend/api/views.py are rarely run, so we don't add the
-- indexes for data->>'date', data->'buyer'->>'name' and data->'tender'->'procuringEntity'->>'name' (text_pattern_ops).

-- 10000 is the maximum.
-- https://www.postgresql.org/docs/current/sql-alterstatistics.html
-- https://www.postgresql.org/docs/current/planner-stats.html
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

-- Column referencing foreign key.
CREATE INDEX field_level_check_dataset_id_idx ON field_level_check (dataset_id);
CREATE INDEX field_level_check_data_item_id_idx ON field_level_check (data_item_id);

CREATE TABLE field_level_check_examples (
    id bigserial PRIMARY KEY,
    dataset_id bigint,
    data jsonb,
    path character varying,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Column referencing foreign key, plus path.
-- pelican-frontend/backend/api/views.py (FieldLevelDetail)
CREATE INDEX field_level_check_examples_dataset_id_path_idx ON field_level_check_examples (dataset_id, path);

CREATE TABLE resource_level_check (
    id bigserial PRIMARY KEY,
    data_item_id bigint,
    dataset_id bigint,
    result jsonb,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Column referencing foreign key.
CREATE INDEX resource_level_check_dataset_id_idx ON resource_level_check (dataset_id);
CREATE INDEX resource_level_check_data_item_id_idx ON resource_level_check (data_item_id);

CREATE TABLE resource_level_check_examples (
    id bigserial PRIMARY KEY,
    dataset_id bigint,
    data jsonb,
    check_name character varying,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- Column referencing foreign key, plus check_name.
-- pelican-frontend/backend/api/views.py (ResourceLevelDetail)
CREATE INDEX resource_level_check_examples_dataset_id_check_name_idx ON resource_level_check_examples (dataset_id, check_name);

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

-- Column referencing foreign key, plus check_name.
-- pelican-frontend/backend/exporter/template_tags/dataset.py
CREATE INDEX dataset_level_check_dataset_id_check_name_idx ON dataset_level_check (dataset_id, check_name);

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

-- Column referencing foreign key, plus check_name.
-- Note: pelican-frontend doesn't yet export time-based check results.
CREATE INDEX time_variance_level_check_dataset_id_check_name_idx ON time_variance_level_check (dataset_id, check_name);

CREATE TABLE exchange_rates (
    id bigserial PRIMARY KEY,
    valid_on date NOT NULL UNIQUE,
    rates jsonb NOT NULL,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- rates appears with valid_on in a WHERE clause. The unique index on valid_on is sufficient.
