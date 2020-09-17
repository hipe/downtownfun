def notecards_via_path(ncs_path, listener):
    def rng(pool_size):
        from random import randrange
        return randrange(1, pool_size)  # avoid 222 #open [#867.V]

    coll = collection_via_path_(ncs_path, listener, rng)
    if coll is None:
        return
    return _Notecards(coll)


class _Notecards:  # #testpoint

    def __init__(self, coll):
        self._coll = coll

    # (the #history-A.2 commit comment expounds the pattern of the below 3)

    # -- Update

    def update_notecard(self, eid, cuds, listener, is_dry=False):
        bpf = self._big_patchfile_for_update(eid, cuds, listener)
        if bpf is None:
            return
        return bpf.APPLY_PATCHES(listener, is_dry=is_dry)

    def _big_patchfile_for_update(self, eid, cuds, listener):
        assert(isinstance(eid, str))  # #[#011]
        eid_tup = ('update_entity', eid)
        return self._big_patchfile(eid_tup, cuds, listener)

    # -- Create

    def create_notecard(self, dct, listener, is_dry):
        bpf = self._big_patchfile_for_create(dct, listener)
        if bpf is None:
            return
        return bpf.APPLY_PATCHES(listener, is_dry=is_dry)

    def _big_patchfile_for_create(self, dct, listener):
        # cuds = tuple(('create_attribute', k, v) for k, v in dct.items())
        eid_tup = ('create_entity',)
        return self._big_patchfile(eid_tup, dct, listener)

    # -- Delete

    def delete_notecard(self, eid, listener, is_dry):
        bpf = self._big_patchfile_for_delete(eid, listener)
        if bpf is None:
            return
        return bpf.APPLY_PATCHES(listener, is_dry=is_dry)

    def _big_patchfile_for_delete(self, eid, listener):  # #testpoint
        assert(isinstance(eid, str))  # #[#011]
        eid_tup = ('delete_entity', eid)
        return self._big_patchfile(eid_tup, (), listener)

    def _big_patchfile(self, eid_tup, mixed, listener):

        edit = self._prepare_edit(eid_tup, mixed, listener)
        if edit is None:
            return
        ci = self._coll.COLLECTION_IMPLEMENTATION

        # The below list is the keys in order from neighbor [#822.M], minus
        # one of them. Whenever it gets annoying, load that module & change to:
        # d = {k: None for k in formals.keys()}; d.pop('identifier'); d.keys()

        order = (
          'parent', 'previous', 'natural_key', 'heading', 'document_datetime',
          'body', 'children', 'next', 'annotated_entity_revisions')

        ifc_dct = (ifc := edit.index_file_change) and ifc.to_dictionary()

        bent = edit.main_business_entity  # fail earlier if this isn't here

        return ci.BIG_PATCHFILE_FOR_BATCH_UPDATE(
            index_file_change=ifc_dct,
            entities_units_of_work=edit.units_of_work,
            result_document_entityer=lambda: bent,
            order=order, listener=listener)

    def _prepare_edit(self, eid_tup, mixed, listener):  # #testpoint
        from .magnetics_.edited_notecard_via_request_and_notecards \
                import prepare_edit_
        return prepare_edit_(eid_tup, mixed, self, listener)

    def retrieve_notecard(self, ncid, listener):
        ent_dct = self._coll.retrieve_entity(ncid, listener)
        return self._notecard_via_any_entity(ent_dct, listener)

    def retrieve_notecard_via_identifier(self, iden, listener):
        ent_dct = self._coll.retrieve_entity_via_identifier(iden, listener)
        return self._notecard_via_any_entity(ent_dct, listener)

    def _notecard_via_any_entity(self, ent_dct, listener):
        if ent_dct is None:
            return
        nid_s, core_attributes = _validate_entity_dictionary_names(** ent_dct)
        return self.entity_via_definition_(nid_s, core_attributes, listener)

    def entity_via_definition_(self, nid_s, core_attributes, listener):
        from .magnetics_.notecard_via_definition import notecard_via_definition
        return notecard_via_definition(nid_s, core_attributes, listener)

    def to_identifier_stream(self, listener):
        return self._coll.to_identifier_stream(listener)

    @property
    def IMPLEMENTATION_(self):
        return self._coll


def _validate_entity_dictionary_names(identifier_string, core_attributes):
    return identifier_string, core_attributes


def repr_(value):
    def do_repr():
        return ''.join((': ', repr(value)))

    if not isinstance(value, str):
        assert(isinstance(value, tuple))  # ..
        return do_repr()

    if len(value) <= _SOMEWHAT_LESS_THAN_A_LINES_WIDTH:  # meh
        return do_repr()

    return ''


_SOMEWHAT_LESS_THAN_A_LINES_WIDTH = 60


# == stowaway support for magnetics

def big_index_via_collection_(coll, listener):
    from pho.magnetics_.big_index_via_collection import \
            big_index_via_collection
    return big_index_via_collection(coll, listener)


def collection_via_path_(collection_path, listener, rng=None):
    from kiss_rdb import collectionerer
    return collectionerer().collection_via_path(
            collection_path, listener, rng=rng)


# ==

def xx(msg=None):
    use_msg = ''.join(('oops/write me', * ((': ', msg) if msg else ())))
    raise RuntimeError(use_msg)


HELLO_FROM_PHO = "hello from pho"

# #history-A.2
# #history-A.1: archive all C, swift and PythonKit experiments
# #born.
