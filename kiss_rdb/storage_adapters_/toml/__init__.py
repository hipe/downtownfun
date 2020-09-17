STORAGE_ADAPTER_CAN_LOAD_DIRECTORIES = True
STORAGE_ADAPTER_CAN_LOAD_SCHEMALESS_SINGLE_FILES = False
STORAGE_ADAPTER_IS_AVAILABLE = True


def COLLECTION_IMPLEMENTATION_VIA_SCHEMA(
        schema_file_scanner, collection_path, opn, rng, listener):

    schema = __schema_via(schema_file_scanner, listener)
    if schema is None:
        return

    if opn:
        fs = opn.THE_WORST_HACK_EVER_FILESYSTEM_
    else:
        fs = None

    from .collection_via_directory import collection_via_directory_and_schema
    return collection_via_directory_and_schema(
            collection_directory=collection_path, collection_schema=schema,
            random_number_generator=rng, filesystem=fs)


def __schema_via(schema_file_scanner, listener):

    # parse the schema file using our own .. meta-schema we define here:
    dct = schema_file_scanner.flush_to_config(
            listener,
            storage_schema='required')
    if dct is None:
        return

    # ok good job
    from .schema_via_file_lines import Schema_
    schema = Schema_(**dct)
    # something about above being null (Case5918)

    return schema


# #born late
