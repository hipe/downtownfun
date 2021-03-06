STORAGE_ADAPTER_CAN_LOAD_DIRECTORIES = True
STORAGE_ADAPTER_CAN_LOAD_SCHEMALESS_SINGLE_FILES = False
STORAGE_ADAPTER_IS_AVAILABLE = True


def ADAPTER_OPTIONS_VIA_SCHEMA_FILE_SCANNER(schema_file_scanner, listener):
    dct = schema_file_scanner.flush_to_config(
            listener, storage_schema='allowed')
    if dct is None:
        return

    from .schema_via_file_lines import Schema_ as func
    schema = func(**dct)
    # something about above being null (Case5918)

    if schema is None:
        return
    return {'toml_schema': schema}


def FUNCTIONSER_VIA_DIRECTORY_AND_ADAPTER_OPTIONS(
        path, listener, toml_schema, opn=None, fs=None, rng=None):

    if opn and fs is None:
        fs = opn.THE_WORST_HACK_EVER_FILESYSTEM_

    ci = _CI_via(path, toml_schema, fs, rng)

    class fxr:  # #class-as-namespace
        def PRODUCE_EDIT_FUNCTIONS_FOR_DIRECTORY():
            return ci

        def PRODUCE_READ_ONLY_FUNCTIONS_FOR_DIRECTORY():
            return ci

        def PRODUCE_IDENTIFIER_FUNCTIONER():
            return ci.build_identifier_function_

        CUSTOM_FUNCTIONS_OLD_WAY = ci  # #open [#877.B] (Case4322)
    return fxr


def _CI_via(directory, schema, fs, rng):
    from .collection_via_directory import \
        collection_implementation_via_directory_and_schema as func
    return func(directory, schema, fs, rng)

# #history-B.4
# #born late
