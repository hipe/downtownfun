"""
this file has a "discussion" at #here1 #todo
"""


from modality_agnostic import memoization as _
memoize = _.memoize


def RUMSKALLA(serr, query_s):

    def my_pprint(x):
        from pprint import pprint
        pprint(x, stream=serr, width=20, indent=4)

    itr = MAKE_CRAZY_ITERATOR_THING(query_s)
    print('the model:')
    my_pprint(next(itr))

    print('the unsani:')
    unsani = next(itr)

    from script_lib.magnetics import listener_via_resources as _
    listener = _.listener_via_stderr(serr)

    wat = unsani.sanitize(listener)

    print('the sani:')
    my_pprint(wat)

    return 1 if wat is None else 0


def MAKE_CRAZY_ITERATOR_THING(query_s):
    """the obviously huge disadvantage here is hardcoded offsets (in effect).

    the advantage is progressive output, good for debugging
    """

    model = query_model_via_big_string(query_s)
    yield model

    _walker = _make_walker()
    unsani = _walker.walk(model)
    yield unsani


def _make_walker():
    """so:

    - ideally this scope will be the only place where we "wire up" all this
      parser-generator-specific stuff (including grammar) with our native,
      insulated AST model (see)

    - for now we enclose this whole doo-hah in this function call to
      load its dependency modules late for regression-friendliness and
      maybe efficiency for some cases. (no)
    """

    import tag_lyfe.the_query_model as native_models
    from tatsu.walkers import NodeWalker

    class MyWalker(NodeWalker):

        def walk_object(self, node):
            print(f'(reminder: {type(node)})')
            return node

        def walk__top_thing(self, node):
            # say something about #here1
            child_EEK_stack = self.walk(node.payload)
            child_EEK_stack.reverse()
            return native_models.UNSANITIZED_LIST(tuple(child_EEK_stack))

        def walk__conjuncted(self, node):
            a_o_o = node.and_or_or
            child_EEK_stack = self.walk(node.item_or_list)
            child_EEK_stack.append(a_o_o)
            return child_EEK_stack

        def walk__item_or_list(self, node):
            return self._same_buckstop(node)

        def walk__negated_function(self, node):
            _ohai = self.walk(node.function_that_is_negated)
            return native_models.UnsanitizedNegation(_ohai)

        def walk__tagging_matcher(self, node):
            tp = self.walk(node.tagging_path)
            mf = node.modifying_suffix
            if mf is None:
                return tp
            else:
                mf = self.walk(mf[1])
                return mf.unsanitized_via_finish(tp)

        def walk__tagging_path(self, node):
            ut = self.walk(node.surface_tag)  # unsanitized tag
            ds = node.deep_selector
            if ds is None:
                return ut
            else:
                EEK_stack = self.walk(ds)
                EEK_stack.reverse()
                return ut.become_deep__(tuple(EEK_stack))

        def walk__deep_selector(self, node):
            return self._same_buckstop(node)

        def walk__deep_selector_component(self, node):
            return native_models.UnsanitizedDeepSelectorComponent(
                    node.deep_selector_rough_stem)

        def walk__surface_tag(self, node):
            return native_models.UnsanitizedShallowOrDeepTag(node.tag_stem)

        def walk__in_suffix(self, node):
            _strings = self.walk(node.in_suffix_payload)
            from tag_lyfe.the_query_model_plugins import in_list_of_values as o
            return o.UnsanitizedInSuffix(_strings)

        def walk__list_of_values_for_in_suffix(self, node):
            x_a = self._SIMPLE_buckstop(node.values_for_in_suffix)
            x_a.reverse()
            return tuple(x_a)

        def walk__with_or_without_value(self, node):
            _yes = true_false_via_with_or_without[node.with_or_without]
            return native_models.UnsanitizedWithOrWithoutFirstStep(_yes)

        def _same_buckstop(self, node):
            return self._reversed_list_from_common_right_recursion(
                    node, self.walk, self.walk)

        def _SIMPLE_buckstop(self, node):
            return self._reversed_list_from_common_right_recursion(
                    node, lambda x: x, self._SIMPLE_buckstop)

        def _reversed_list_from_common_right_recursion(
                self, node, walk_left, walk_right):

            left = node.left
            right = node.right
            left_native_AST = walk_left(left)
            if right is None:
                return [left_native_AST]  # the buck starts :#here1
            else:
                mutable_reversed_list = walk_right(right)
                mutable_reversed_list.append(left_native_AST)
                return mutable_reversed_list

    true_false_via_with_or_without = {
            'with': True,
            'without': False,
            }

    return MyWalker()


def query_model_via_big_string(big_string):

    parser = query_parser()

    model = parser.parse(
            text=big_string,
            # semantics=JimFlim(),
            )

    return model


@memoize
def query_parser():

    with open('tag_lyfe/grammars/the-query-grammar.ebnf') as fh:
        ebnf_grammar_big_string = fh.read()

    import tatsu
    _ = tatsu.compile(
            ebnf_grammar_big_string,
            asmodel=True,
            )
    return _


# #born.
