class UnitsOfWorkForEntity:
    # Implement the DSL that field operations are defined with.
    # This assists in preparing edits that involve foreign keys (doubly-linked
    # lists or one-to-many double-links) so it's centric to a central entity.

    def __init__(self, ent_cud_type, bent, business_coll, listener):
        self._prepared_edits = []
        self._business_collection = business_coll
        self.listener = listener
        self._entity_cache = {}

        eid = bent.identifier_string
        self._EID_of_entity_being_created = None
        self._EID_of_entity_being_deleted = None
        if 'create_entity' == ent_cud_type:
            self._EID_of_entity_being_created = eid
        elif 'delete_entity' == ent_cud_type:
            self._EID_of_entity_being_deleted = eid
        self._entity_cache[eid] = bent
        self.entity_identifier_string = eid

    def release_prepared_edits(self):
        x = self._prepared_edits
        del self._prepared_edits
        return tuple(x)

    def will_set_in(self, entity, attr_cud_type, dattr, attr, value):
        eid = entity.identifier_string
        setattr(entity, attr, value)  # #here1
        if self._EID_of_entity_being_created == eid:
            # (this is a little awkward because it's grafted on to update but)
            update_or_create = 'create_entity'
        else:
            update_or_create = 'update_entity'
        self._will(update_or_create, eid, attr_cud_type, dattr, value)

    def will_delete_in(self, entity, dattr, attr):
        setattr(entity, attr, None)  # #here1
        eid = entity.identifier_string
        if self._EID_of_entity_being_deleted == eid:
            # (same as above)
            update_or_delete = 'delete_entity'  # hacky
        else:
            update_or_delete = 'update_entity'
        self._will(update_or_delete, eid, 'delete_attribute', dattr)

    def _will_update(self, *tup):
        self._prepared_edits.append(('update_entity', *tup))

    def will_delete_entity(self, eid):  # ASSUMES eid is valid
        self._will('delete_entity', eid)

    def _will(self, *tup):
        self._prepared_edits.append(tup)

    def retrieve(self, eid):
        ent = self._entity_cache.get(eid)
        if ent is not None:
            return ent
        ent = self._business_collection.retrieve_notecard(eid, self.listener)
        if ent is None:
            return
        self._entity_cache[eid] = ent
        return ent


def CUD_parser_via_formal_entity(formal_entity):

    def _parse_CUD(cud_tup):
        if (cud := maybe_has_strange_CUD_type_or_wrong_num(cud_tup)) is None:
            return
        if has_strange_attribute_name(cud):
            return
        if youve_already_seed_a_CUD_for_this_attribute_name(cud):
            return
        if maybe_its_not_editable(cud):
            return
        return cud

    def maybe_its_not_editable(cud):
        formal = cud.formal
        editable = formal.get('editable')
        if editable is True:
            return

        if not editable:
            cant_edit.append((cud, formal['reason']))
            return True

        import re
        allowed_verb = re.match('^on_(create|update|delete)$', editable)[1]
        if allowed_verb == cud.verb:
            return

        _1 = f'can only edit it on {allowed_verb}'
        _2 = formal['reason']
        cant_edit.append((cud, f'{_1} -- {_2}'))
        return True

    def youve_already_seed_a_CUD_for_this_attribute_name(cud):
        dattr = cud.document_attribute_name
        if dattr in seen_count:
            seen_count[cud.dattr] += 1
            seen_multiple.add(dattr)
            return True
        seen_count[dattr] = 1

    def has_strange_attribute_name(cud):
        formal = formal_entity.get(cud.document_attribute_name)
        if formal is None:
            strange_names.add(cud.dattr)
            return True
        cud.formal = formal

    def maybe_has_strange_CUD_type_or_wrong_num(cud_tup):
        cud_type = cud_tup[0]
        f = _XXX_via_CUD_type.get(cud_type)
        if f is None:
            strange_CUD_type.add(cud_type)
            return
        return f(cud_tup)

    def _express_errors_into(listener):
        listener('error', 'expression', 'problems_with_edit_request', many_lineser)  # noqa: E501

    def many_lineser():

        def filter(strange_set):
            our_repr = _our_repr()
            for strange in strange_set:
                s = our_repr(strange)
                if s is None:
                    continue
                yield f'  - had{s}'

        if len(strange_CUD_type):
            _ = ', '.join(_XXX_via_CUD_type.keys())
            yield f"unrecognized CUD types. known CUD types: ({_})."
            for line in filter(strange_CUD_type):
                yield line

        if len(strange_names):
            yield "had attribute name(s) not in the list of known attributes."
            for line in filter(strange_names):
                yield line

        if len(cant_edit):
            for cud, why in cant_edit:
                yield f"can't {cud.verb} {cud.dattr} because {why}"

        if len(seen_multiple):
            _ = (dattr for dattr, count in seen_count.items() if 1 < count)
            _ = ', '.join(_)
            yield f'appears multiple times: ({_})'

    def _has_errors():
        if len(strange_CUD_type) or len(strange_names) \
                or len(seen_multiple) or len(cant_edit):
            return True

    cant_edit = []
    seen_count = {}
    seen_multiple = set()
    strange_names = set()
    strange_CUD_type = set()

    class CUD_parser:

        def CUD_via_tuple(self, cud_tup):
            cud = self.parse_CUD(cud_tup)
            if not self.has_errors:
                return cud
            raise _ModuleLocalException('. '.join(many_lineser()))

        def parse_CUD(self, cud_tup):
            return _parse_CUD(cud_tup)

        @property
        def has_errors(self):
            return _has_errors()

        def express_errors_into(self, listener):
            _express_errors_into(listener)

    return CUD_parser()


def _CUD_type_extenter():

    def cud_type_decorator(orig_f):  # #decorator
        def use_f(cud_tup):
            o = _CUD(verb)
            orig_f(o, cud_tup)
            return o
        cud_type = orig_f.__name__
        verb = rx.match(cud_type)['verb']
        function_via_CUD_type[cud_type] = use_f
        return use_f

    function_via_CUD_type = {}

    import re
    rx = re.compile('^(?P<verb>[a-z]+)_attribute$')

    return cud_type_decorator, function_via_CUD_type


cud_type, _XXX_via_CUD_type = _CUD_type_extenter()


@cud_type
def update_attribute(o, cud_tup):
    o.CUD_type, o.dattr, o.requested_value = cud_tup


@cud_type
def create_attribute(o, cud_tup):
    o.CUD_type, o.dattr, o.requested_value = cud_tup


@cud_type
def delete_attribute(o, cud_tup):
    o.CUD_type, o.dattr = cud_tup


class _CUD:
    def __init__(self, verb):
        self.has_requested_value = False
        self.verb = verb

    @property
    def requested_value(self):
        return self._requested_value

    @requested_value.setter
    def requested_value(self, x):
        self.has_requested_value = True
        self._requested_value = x

    @property
    def document_attribute_name(self):
        return self.dattr  # meh


def _our_repr():
    from pho.magnetics_.text_via import our_repr as func
    return func


class _ModuleLocalException(RuntimeError):
    pass

# :#here1: YIKES

# #born
