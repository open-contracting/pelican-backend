CREATE TABLE IF NOT EXISTS collection (
    id bigint NOT NULL PRIMARY KEY,
    source_id text NOT NULL,
    data_version timestamp with time zone NOT NULL,
    store_start_at timestamp with time zone NOT NULL,
    store_end_at timestamp with time zone,
    sample boolean NOT NULL,
    transform_type text NOT NULL,
    deleted_at timestamp with time zone,
    cached_releases_count integer,
    cached_records_count integer,
    cached_compiled_releases_count integer,
    transform_from_collection_id bigint,
    options jsonb NOT NULL,
    steps jsonb NOT NULL,
    expected_files_count integer,
    data_type jsonb NOT NULL,
    compilation_started boolean NOT NULL,
    completed_at timestamp with time zone,
    scrapyd_job text NOT NULL
);

CREATE TABLE IF NOT EXISTS collection_file (
    id bigint NOT NULL PRIMARY KEY,
    filename text NOT NULL,
    url text NOT NULL,
    collection_id bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS collection_file_item (
    id bigint NOT NULL PRIMARY KEY,
    number integer NOT NULL,
    collection_file_id bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS compiled_release (
    id bigint NOT NULL PRIMARY KEY,
    ocid text NOT NULL,
    collection_id bigint NOT NULL,
    collection_file_item_id bigint NOT NULL,
    data_id bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS data (
    id bigint NOT NULL PRIMARY KEY,
    hash_md5 text NOT NULL,
    data jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS package_data (
    id bigint NOT NULL PRIMARY KEY,
    hash_md5 text NOT NULL,
    data jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS record (
    id bigint NOT NULL PRIMARY KEY,
    ocid text NOT NULL,
    collection_id bigint NOT NULL,
    collection_file_item_id bigint NOT NULL,
    data_id bigint NOT NULL,
    package_data_id bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS release (
    id bigint NOT NULL PRIMARY KEY,
    release_id text NOT NULL,
    ocid text NOT NULL,
    collection_id bigint NOT NULL,
    collection_file_item_id bigint NOT NULL,
    data_id bigint NOT NULL,
    package_data_id bigint NOT NULL
);
