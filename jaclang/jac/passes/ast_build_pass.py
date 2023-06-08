"""Pass that builds well formed AST from parse tree AST."""
from jaclang.jac.ast import AstNode, AstNodeKind as Ak
from jaclang.jac.passes.ir_pass import Pass


class AstBuildPass(Pass):
    """Ast build pass."""

    # def __init__(self: "AstBuildPass", ir: AstNode = None) -> None:
    #     """Initialize pass."""
    #     super().__init__(ir)

    def exit_start(self: "AstBuildPass", node: AstNode) -> None:
        """Exit start node."""
        node.kind = Ak.WHOLE_BUILD
        node.kid = node.kid[0].kid

    def exit_element_list(self: "AstBuildPass", node: AstNode) -> None:
        """Exit element list node."""
        if len(node.kid) == 2:
            node.kid = node.kid[0].kid + [node.kid[1]]

    def exit_element(self: "AstBuildPass", node: AstNode) -> None:
        """Exit element node."""
        node = replace_node(node, node.kid[0])
        if node.kind == Ak.TOKEN:
            node.kind = Ak.DOC_STRING

    def exit_global_var(self: "AstBuildPass", node: AstNode) -> None:
        """Exit global var node."""
        node.kind = Ak.GLOBAL_VAR

    def exit_global_var_clause(self: "AstBuildPass", node: AstNode) -> None:
        """Exit global var clause node."""
        node.kind = Ak.NAMED_ASSIGN
        if len(node.kid) == 5:
            node.parent.kid = [node.kid[0], node]
        node.kid = [node.kid[-3], node.kid[-1]]

    def exit_test(self: "AstBuildPass", node: AstNode) -> None:
        """Exit test node."""
        node.kind = Ak.TEST
        node.kid = node.kid[1:]

    def exit_import_stmt(self: "AstBuildPass", node: AstNode) -> None:
        """Exit import stmt node."""
        kid = node.kid
        node.kind = Ak.IMPORT
        if len(node.kid) == 7:
            node.kind = Ak.IMPORT_FROM
            node.kid = [kid[1], kid[3], kid[5]]
        elif len(node.kid) == 6:
            node.kid = [kid[1], kid[2], kid[4]]
        else:
            node.kid = [kid[1], kid[2]]

    # def exit_import_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_import_path(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_import_path_prefix(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_import_path_tail(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_name_as_list(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_architype(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_arch_decl_tail(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_inherited_archs(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_sub_name(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_ability_spec(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_attr_block(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_attr_stmt_list(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_attr_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_has_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_has_assign_clause(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_param_var(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_has_tag(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_type_spec(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_type_name(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_builtin_type(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_can_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_can_ds_ability(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_can_func_ability(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_event_clause(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_func_decl(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_func_decl_param_list(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_name_list(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_code_block(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_statement_list(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_statement(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_if_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_elif_stmt_list(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_else_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_try_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_else_from_try(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_for_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_while_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_assert_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_ctrl_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_delete_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_report_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_return_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_walker_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_ignore_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_visit_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_revisit_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_disengage_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_yield_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_sync_stmt(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_assignment(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_expression(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_walrus_assign(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_pipe(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_elvis_check(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_logical(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_compare(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_arithmetic(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_term(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_factor(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_power(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_connect(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_spawn_walker(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_spawn_object(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_spawn_edge_node(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_unpack(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_walrus_op(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_cmp_op(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_spawn_op(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_atom(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_atom_literal(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_atom_collection(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_multistring(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_list_val(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_expr_list(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_dict_val(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_kv_pairs(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_ability_run(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_atomic_chain(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_atomic_chain_unsafe(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_atomic_chain_safe(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_call(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_param_list(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_assignment_list(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_index_slice(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_global_ref(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_arch_ref(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_node_ref(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_edge_ref(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_walker_ref(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_object_ref(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_ability_ref(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_edge_op_ref(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_edge_to(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_edge_from(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_edge_any(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_connect_op(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_connect_to(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_connect_from(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_connect_any(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_filter_ctx(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_spawn_ctx(self: "AstBuildPass", node: AstNode) -> None:
    # def exit_filter_compare_list(self: "AstBuildPass", node: AstNode) -> None:


def replace_node(node: AstNode, new_node: AstNode) -> None:
    """Replace node with new_node."""
    node.parent.kid[node.parent.kid.index(node)] = new_node
    return new_node
