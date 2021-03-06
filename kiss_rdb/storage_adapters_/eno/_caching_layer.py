def _property_from_back(orig_f):
    def use_f(self):
        return getattr(self._back, orig_f.__name__)
    return property(use_f)


class ReadOnlyCollectionLayer_:

    def __init__(self, back):
        self._back = back

    def retrieve_entity_via_identifier(self, iden, listener):
        return self._back.retrieve_entity(iden.to_primitive(), listener)

    def retrieve_entity(self, eid, listener):
        return self._back.retrieve_entity(eid, listener)

    def open_identifier_traversal(self, listener):
        return self._back.open_identifier_traversal(listener)

    def open_EID_traversal_EXPERIMENTAL(self, listener):
        return self._back.open_EID_traversal_EXPERIMENTAL(listener)

    def open_entity_traversal(self, listener):
        return self._back.open_entity_traversal(listener)

    # == BEGIN #cover-me [pho]

    @_property_from_back
    def mixed_collection_identifier(self):
        pass

    @_property_from_back
    def VALUE_FUNCTION_RIGHT_HAND_SIDES(self):
        pass

    @_property_from_back
    def VALUE_FUNCTION_VARIABLE_RIGHT_HAND_SIDES(self):
        pass

    @_property_from_back
    def custom_functions(self):
        pass

    # == END


class Caching_FS_Reader_:  # #testpoint

    def __init__(self, ci, max_num_lines_to_cache=None, opn=None):
        self._back = ci
        self._opn = opn
        self._cached_path_via_EID = {}  # #testpoint
        self._file_reader_via_path = {}  # #testpoint
        self._current_number_of_lines_cached = 0

        if max_num_lines_to_cache is None:
            max_num_lines_to_cache = 10_000  # 20 files x 500 lines per, idk

        assert -1 < max_num_lines_to_cache

        self._max_number_of_lines_to_cache = max_num_lines_to_cache

        from modality_agnostic.magnetics.doubly_linked_list_via_nothing \
            import func
        self._doubly_linked_list = func()  # #[#510.15] one of several rotbuff

    def entities_via_identifiers(self, idens, mon):
        return self._traverse_and('dereference', idens, mon)

    def entity_retrievals_via_identifiers(self, idens, mon):
        return self._traverse_and('produce_retrieval', idens, mon)

    def _traverse_and(self, which, idens, mon):
        for iden in idens:
            if iden is None:
                yield None  # [#877.C]
                continue
            mfr = self._file_reader_for(iden, mon)
            if mfr is None:
                yield None  # [#877.C]
                continue
            yield getattr(mfr, which)(iden, mon)

    def _file_reader_for(self, iden, mon):

        # If you already have a reader cached for this EID, use that
        eid = iden.to_string()
        path = self._cached_path_via_EID.get(eid)

        if path is not None:
            return self._file_reader_via_path[path]

        # Start this work object
        o = self._start_work_object(mon, identifier=iden)

        # Resolve a path from the identifier
        def main():
            o.resolve_path_given_identifier()
            return o.path
        path = o.do(main)

        # Maybe the identifier is of the wrong depth
        if path is None:
            return

        # If you already have an FR for this path, then entity not exist
        if path in self._file_reader_via_path:
            xx(f"The file for {iden.to_string()!r} exists but that entity"
               " is not in the file.\n"
               f"path: {path}")

        mfr = self._resolve_my_file_reader_given_work_with_path(o, mon)

        # If no FR, probably no path (and it emitted)
        if not mfr:
            return

        # There's no guarantee that the file has the entity (could be hole)
        if not mfr.has_section_for_EID(eid):

            # .. then create the exact same emission you would without caching
            def main():
                o.resolve_entity_given_file_reader()
                return True
            found = o.do(main)
            assert found is None
            return

        return mfr

    def file_readers_via_monitor(self, mon):
        # Build FR builder hackily
        def forever():
            while True:
                assert 1 == len(the_worst)
                yield the_worst.pop()
        the_worst = []
        from . import file_readers_via_paths_ as func
        itr = func(forever(), self._back, mon)

        # For each path, either use your cached FR or build a new one
        dct = self._file_reader_via_path
        paths = self._back.to_file_paths_()
        for path in paths:

            # If you have one cached, use it
            if (mfr := dct.get(path)):
                yield mfr
                continue

            # Since you don't have this cached, you need it.
            the_worst.append(path)
            fr = next(itr)
            mfr = _build_my_file_reader(fr, path, mon)
            self._rotate_stock(mfr)
            yield mfr

    def PRODUCE_FILE_READER_FOR_PATH(self, path, mon):
        # (courtesy for [pho] for document history, so no re-parsing)

        mfr = self._file_reader_via_path.get(path)
        if mfr:
            return mfr  # unlikely in practice
        o = self._start_work_object(mon)
        o.path = path
        return self._resolve_my_file_reader_given_work_with_path(o, mon)

    def _resolve_my_file_reader_given_work_with_path(self, o, mon):

        # Resolve a file reader from the path
        def main():
            o.resolve_file_reader_given_path()
            return o.file_reader
        fr = o.do(main)

        # If no FR, probably no path (and it emitted)
        if fr is None:
            return

        # Build the "my FR" and rotate it in to the cache
        mfr = _build_my_file_reader(fr, o.path, mon)
        self._rotate_stock(mfr)
        return mfr

    def _rotate_stock(self, mfr):

        num = mfr.number_of_lines_in_file
        local_max = self._max_number_of_lines_to_cache - num  # negative O

        while True:
            # You can't purge the cache any more than having none cached
            if 0 == len(self._file_reader_via_path):
                break

            # Do we have enough room to add the new file reader yet?
            if self._current_number_of_lines_cached <= local_max:
                break

            # If not, get rid of one more reader and check again
            self._pop_the_oldest_file_reader()

        path = mfr.path

        # Super cautious and costly and temporary:
        dct = self._cached_path_via_EID
        for eid in mfr.to_EIDs_in_file():
            assert eid not in dct
        assert path not in self._file_reader_via_path

        # Add this path to the rotbuf
        self._doubly_linked_list.append_item(path)

        # Add this file's EIDs to the EID index
        dct = self._cached_path_via_EID
        for eid in mfr.to_EIDs_in_file():
            dct[eid] = path

        # Add this file (reader) to that index
        self._file_reader_via_path[path] = mfr

        # Update this one total
        self._current_number_of_lines_cached += num

    def _pop_the_oldest_file_reader(self):

        dll = self._doubly_linked_list
        iid = dll.head_IID  # We append to the DLL, so head is always oldest

        # Remove this path from the rotbuf
        path = dll.delete_item(iid)
        fr = self._file_reader_via_path[path]

        # Remove this file's EID's from the EID index
        dct = self._cached_path_via_EID
        for eid in fr.to_EIDs_in_file():
            x = dct.pop(eid)
            assert path == x

        # Remove this file (reader) from the index
        self._file_reader_via_path.pop(path)

        # Decrease this one total
        num = fr.number_of_lines_in_file
        assert 0 < num
        self._current_number_of_lines_cached -= num

    def _start_work_object(self, mon, identifier=None):
        from . import RetrieveEntity_ as cls
        return cls(identifier, mon, self._back, opn=self._opn)


def _build_my_file_reader(fr, path, mon):

    # Index sections by entity identifier
    section_offset_via_EID, sections, offset = {}, [], -1
    for typ, eid, sect in fr.to_section_elements():
        offset += 1
        if 'entity_section' == typ:
            assert eid not in section_offset_via_EID
            section_offset_via_EID[eid] = offset
        else:
            assert 'document_meta' == typ
        sections.append(sect)
    sections = tuple(sections)

    # Get line number count with big hack, gonna fail one day
    who = sections[-1]._instruction['elements'][-1]
    typ = who['type']
    if 'Multiline Field Begin' == typ:
        who = who['end']
        assert 'Multiline Field End' == who['type']
        num_lines = who['line'] + 1  # 0-indexed
    else:
        xx('enjoy')

    def idenerer(): return fr.identifier_builder_

    return _MyFileReader(
        num_lines, section_offset_via_EID,
        sections, fr.body_of_text, path,
        idenerer, mon)


class _MyFileReader:

    def __init__(self, num_lines, dct, sections, bot, path, idenerer, mon):
        self.number_of_lines_in_file = num_lines
        self._section_offset_via_EID, self._sections = dct, sections
        self.path, self._BoT, self._idenerer = path, bot, idenerer

        self._monitor = mon

        self._entity_cache = {}

        from . import read_only_entity_via_section_ as func
        self._build_entity = func

    def to_entities(self):
        mon = self._monitor
        for iden in self.to_identifiers():
            ent = self.dereference(iden, mon)
            if ent is None:
                break
            yield ent

    def to_identifiers(self):  # #not-covered
        iden_via = self._idenerer()
        return (iden_via(eid) for eid in self.to_EIDs_in_file())

    def produce_retrieval(self, iden, mon):
        ent = self.dereference(iden, mon)
        if ent is None:
            return
        eid = iden.to_string()
        sect = self._section_via_EID(eid)
        return _retrieval(ent, sect, self._BoT)

    def dereference(self, iden, mon):

        # If you've already produced the entity before, use that
        eid = iden.to_string()
        ent = self._entity_cache.get(eid)
        if ent is not None:
            return ent

        # Build and cache the entity
        sect = self._section_via_EID(eid)
        ent = self._build_entity(sect, iden, mon)
        if ent is None:
            return  # don't cache failures. punish the client over and over
        self._entity_cache[eid] = ent
        return ent

    def _section_via_EID(self, eid):
        section_offset = self._section_offset_via_EID[eid]  # must exist
        return self._sections[section_offset]

    def to_EIDs_in_file(self):
        return self._section_offset_via_EID.keys()

    def has_section_for_EID(self, eid):
        return eid in self._section_offset_via_EID


def _retrieval(entity, section, bot):
    # (yes we use a RetrieveEntity_ object to retrieve entities but it's
    # too complicated to touch here)

    if (cls := getattr(_retrieval, 'x', None)) is None:
        from collections import namedtuple as func
        cls = func('_retrieval', ('entity', 'entity_section', 'body_of_text'))
        _retrieval.x = cls
    return cls(entity, section, bot)


def xx(msg=None):
    raise RuntimeError(''.join(('ohai', *((': ', msg) if msg else ()))))

# #born
