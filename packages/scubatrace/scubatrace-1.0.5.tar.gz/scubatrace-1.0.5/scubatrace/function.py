from __future__ import annotations

from collections import defaultdict, deque
from functools import cached_property
from typing import TYPE_CHECKING, Callable, Generator

import networkx as nx
from tree_sitter import Node

from . import language as lang
from .identifier import Identifier
from .statement import BlockStatement, Statement

if TYPE_CHECKING:
    from .file import File


class Function(BlockStatement):
    """
    A function in the source code.
    """

    def __init__(self, node: Node, file: File | BlockStatement):
        super().__init__(node, file)
        self._is_build_cfg = False

    @staticmethod
    def create(node: Node, parent: File | BlockStatement):
        """
        Factory function to create a Function instance based on the language of the file.

        Args:
            node (Node): The tree-sitter node representing the function.
            file (File): The file containing the function.

        Returns:
            Function: An instance of a language-specific Function subclass corresponding to the file's language.
        """
        if parent.project.language == lang.C:
            from .cpp.function import CFunction

            return CFunction(node, parent)
        elif parent.project.language == lang.JAVA:
            from .java.function import JavaFunction

            return JavaFunction(node, parent)
        elif parent.project.language == lang.JAVASCRIPT:
            from .javascript.function import JavaScriptFunction

            return JavaScriptFunction(node, parent)
        elif parent.project.language == lang.PYTHON:
            from .python.function import PythonFunction

            return PythonFunction(node, parent)
        elif parent.project.language == lang.GO:
            from .go.function import GoFunction

            return GoFunction(node, parent)
        elif parent.project.language == lang.PHP:
            from .php.function import PHPFunction

            return PHPFunction(node, parent)
        elif parent.project.language == lang.RUBY:
            from .ruby.function import RubyFunction

            return RubyFunction(node, parent)
        elif parent.project.language == lang.RUST:
            from .rust.function import RustFunction

            return RustFunction(node, parent)
        elif parent.project.language == lang.SWIFT:
            from .swift.function import SwiftFunction

            return SwiftFunction(node, parent)
        elif parent.project.language == lang.CSHARP:
            from .csharp.function import CSharpFunction

            return CSharpFunction(node, parent)
        else:
            return Function(node, parent)

    @cached_property
    def statements(self) -> list[Statement]:
        """
        Statements in the function.
        """
        if self.body_node is None:
            return []
        return BlockStatement.build_statements(self.body_node, self)

    @cached_property
    def first_statement(self) -> Statement | None:
        if len(self.statements) == 0:
            return None
        return self.statements[0]

    def __str__(self) -> str:
        return (
            f'"{self.name.replace("::", "--")} ({self.file.name}\\:{self.start_line})"'
        )

    @property
    def signature(self) -> str:
        """
        A unique signature for the function.
        """
        return (
            '"'
            + self.file.signature
            + "#"
            + self.name.replace("::", "--")  # dot bug
            + "#"
            + str(self.start_line)
            + "#"
            + str(self.end_line)
            + '"'
        )

    @property
    def lines(self) -> dict[int, str]:
        """
        A dictionary mapping line numbers to their corresponding lines of text.
        """
        return {
            i + self.start_line: line for i, line in enumerate(self.text.split("\n"))
        }

    @property
    def body_node(self) -> Node | None:
        """
        The tree-sitter body node of the function.
        """
        return self.node.child_by_field_name("body")

    @property
    def body_start_line(self) -> int:
        """
        The starting line number of the body of the function.
        """
        if self.body_node is None:
            return self.start_line
        else:
            return self.body_node.start_point[0] + 1

    @property
    def body_end_line(self) -> int:
        """
        The ending line number of the body of the function.
        """
        if self.body_node is None:
            return self.end_line
        else:
            return self.body_node.end_point[0] + 1

    @property
    def dot_text(self) -> str:
        return '"' + f"{self.name}#{self.file.name}#{self.start_line}" + '"'

    @cached_property
    def parameter_lines(self) -> list[int]:
        """
        The lines where the parameters of the function are defined.
        """
        params = self.query_identifiers(self.language.query_function_parameter)
        if len(params) == 0:
            return [self.start_line]
        return list(range(params[0].start_line, params[-1].end_line + 1))

    @cached_property
    def parameters(self) -> list[Identifier]:
        """
        The parameter statements of the function.
        """
        params = self.query_identifiers(self.language.query_function_parameter)
        if len(params) == 0:
            return self.block_variables
        return params

    @cached_property
    def name_node(self) -> Node:
        """
        The tree-sitter node representing the name of the function.
        """
        node = self.node.child_by_field_name("name")
        if node is None:
            raise ValueError(f"Function name node not found: {self.node}")
        return node

    @property
    def name(self) -> str:
        """
        The name of the function.
        """
        name_node = self.name_node
        assert name_node.text is not None
        return name_node.text.decode()

    @cached_property
    def exits(self) -> list[Statement]:
        """
        The exit statements of the function, such as return statements.
        """
        exits = self.statements_by_types(self.language.EXIT_STATEMENTS, recursive=True)
        return exits

    @cached_property
    def accessible_functions(self) -> list[Function]:
        funcs = []
        for file in self.file.imports:
            for function in file.functions:
                funcs.append(function)
        for func in self.file.functions:
            funcs.append(func)
        return funcs

    @property
    def is_external(self) -> bool:
        """
        Checks if the function is external (not part of the project).
        """
        return self.file.is_external

    @cached_property
    def calls(self) -> list[Statement]:
        """
        Call statements within the function.
        """
        return self.query(self.language.query_call)

    @cached_property
    def callees(self) -> dict[Function | FunctionDeclaration, list[Statement]]:
        """
        The functions or function declarations that are called by this function and their corresponding call sites.
        """
        lsp = self.lsp
        callees = defaultdict(set[Statement])
        for call_stat in self.calls:
            for identifier in call_stat.identifiers:
                call_hierarchys = lsp.request_prepare_call_hierarchy(
                    self.file.relpath,
                    identifier.node.start_point[0],
                    identifier.node.start_point[1],
                )
                if len(call_hierarchys) == 0:
                    continue
                callee_def = lsp.request_definition(
                    call_stat.file.relpath,
                    identifier.node.start_point[0],
                    identifier.node.start_point[1],
                )
                if len(callee_def) == 0:
                    continue
                callee_def = callee_def[0]
                # external file
                if callee_def["uri"] not in self.file.project.files_uri:
                    if len(callee_def["uri"]) == 0:
                        continue
                    from .file import File

                    self.file.project.files_uri[callee_def["uri"]] = File.create(
                        callee_def["uri"],
                        self.file.project,
                    )
                callee_file = self.file.project.files_uri[callee_def["uri"]]
                callee_line = callee_def["range"]["start"]["line"] + 1
                callee_func = callee_file.function_by_line(callee_line)
                if callee_func == self:
                    continue  # avoid self-references
                if callee_func is None:
                    declar = callee_file.lines[callee_line - 1]
                    callee_func = FunctionDeclaration(
                        identifier.text, declar, callee_file
                    )
                callees[callee_func].add(identifier.statement)
        callees = {k: list(v) for k, v in callees.items()}
        return callees

    @cached_property
    def callers(self) -> dict[Function, list[Statement]]:
        """
        The functions that call this function and their corresponding call sites.
        """
        lsp = self.lsp
        call_hierarchy = lsp.request_prepare_call_hierarchy(
            self.file.relpath,
            self.name_node.start_point[0],
            self.name_node.start_point[1],
        )
        if len(call_hierarchy) == 0:
            return {}
        call_hierarchy = call_hierarchy[0]
        calls = lsp.request_incoming_calls(call_hierarchy)
        callers = defaultdict(list[Statement])
        for call in calls:
            from_ = call["from_"]
            fromRanges = call["fromRanges"]
            caller_file = self.file.project.files_uri[from_["uri"]]
            for fromRange in fromRanges:
                callsite_line = fromRange["start"]["line"] + 1
                callsite_stats = caller_file.statements_by_line(callsite_line)
                for stat in callsite_stats:
                    if self.name in stat.text:
                        callers[stat.function].append(stat)
                        break
        return callers

    def walk_backward(
        self,
        filter: Callable[[Statement], bool] | None = None,
        stop_by: Callable[[Statement], bool] | None = None,
        depth: int = -1,
        base: str = "call",
    ) -> Generator[Function, None, None]:
        for caller in super().walk_backward(
            filter=filter,
            stop_by=stop_by,
            depth=depth,
            base=base,
        ):
            assert isinstance(caller, Function)
            yield caller

    def walk_forward(
        self,
        filter: Callable[[Statement], bool] | None = None,
        stop_by: Callable[[Statement], bool] | None = None,
        depth: int = -1,
        base: str = "call",
    ) -> Generator[Function, None, None]:
        for callee in super().walk_forward(
            filter=filter,
            stop_by=stop_by,
            depth=depth,
            base=base,
        ):
            assert isinstance(callee, Function)
            yield callee

    def __build_callgraph(self, depth: int = -1) -> nx.MultiDiGraph:
        cg = nx.MultiDiGraph()
        cg.add_node(
            self,
            color="red",
            shape="box",
            style="rounded",
        )
        forward_depth = 2048 if depth == -1 else depth
        dq: deque[Function | FunctionDeclaration] = deque([self])
        visited: set[Function | FunctionDeclaration] = set([self])
        while len(dq) > 0 and forward_depth > 0:
            size = len(dq)
            for _ in range(size):
                caller = dq.popleft()
                if not isinstance(caller, Function):
                    continue
                for callee, callsites in caller.callees.items():
                    for callsite in callsites:
                        cg.add_edge(
                            caller,
                            callee,
                            key=callsite.signature,
                            label=callsite.start_line,
                        )
                    if callee not in visited:
                        visited.add(callee)
                        dq.append(callee)
            forward_depth -= 1

        backward_depth = 2048 if depth == -1 else depth
        dq = deque([self])
        visited = set([self])
        while len(dq) > 0 and backward_depth > 0:
            size = len(dq)
            for _ in range(size):
                callee = dq.popleft()
                if not isinstance(callee, Function):
                    continue
                for caller, callsites in callee.callers.items():
                    for callsite in callsites:
                        cg.add_edge(
                            caller,
                            callee,
                            key=callsite.signature,
                            label=callsite.start_line,
                        )
                    if caller not in visited:
                        visited.add(caller)
                        dq.append(caller)
            backward_depth -= 1
        return cg

    def export_callgraph(self, path: str, depth: int = -1) -> nx.MultiDiGraph:
        """
        Exports the call graph of the function to a DOT file.

        Args:
            path (str): The path to save the DOT file.
            depth (int): The depth of the call graph to export. -1 means no limit.

        Returns:
            nx.MultiDiGraph: The call graph of the function.
        """
        cg = self.__build_callgraph(depth)
        nx.nx_pydot.write_dot(cg, path)
        return cg

    def slice_by_statements(
        self,
        statements: list[Statement],
        *,
        control_depth: int = 1,
        data_dependent_depth: int = 1,
        control_dependent_depth: int = 1,
    ) -> list[Statement]:
        """
        Slices the function to retrieve relevant statements based on the provided statements.

        Args:
            statements (list[Statement]): Slice criteria statements.
            control_depth (int): Slice depth for control flow dependencies.
            data_dependent_depth (int): Slice depth for data dependencies.
            control_dependent_depth (int): Slice depth for control-dependent statements.

        Returns:
            list[Statement]: A list of statements that are sliced based on the provided statements.
        """
        res = set()
        for stat in statements:
            for s in stat.walk_backward(depth=control_depth, base="control"):
                res.add(s)
            for s in stat.walk_forward(depth=control_depth, base="control"):
                res.add(s)
            for s in stat.walk_backward(
                depth=data_dependent_depth, base="data_dependent"
            ):
                res.add(s)
            for s in stat.walk_forward(
                depth=data_dependent_depth, base="data_dependent"
            ):
                res.add(s)
            for s in stat.walk_backward(
                depth=control_dependent_depth, base="control_dependent"
            ):
                res.add(s)
            for s in stat.walk_forward(
                depth=control_dependent_depth, base="control_dependent"
            ):
                res.add(s)
        return sorted(list(res), key=lambda x: x.node.start_byte)

    def slice_by_lines(
        self,
        lines: list[int],
        *,
        control_depth: int = 1,
        data_dependent_depth: int = 1,
        control_dependent_depth: int = 1,
    ) -> list[Statement]:
        """
        Slices the function to retrieve relevant statements based on the specified lines.

        Args:
            lines (list[int]): Slice criteria lines. Note that only support the lines in the function body currently.
            control_depth (int): Slice depth for control flow dependencies.
            data_dependent_depth (int): Slice depth for data dependencies.
            control_dependent_depth (int): Slice depth for control-dependent statements.

        Returns:
            list[Statement]: A list of statements that are sliced based on the specified lines.
        """
        statements = set()
        for line in lines:
            stats: list[Statement] = self.statements_by_line(line)
            if stats:
                statements.update(stats)

        return self.slice_by_statements(
            sorted(list(statements), key=lambda x: x.start_line),
            control_depth=control_depth,
            data_dependent_depth=data_dependent_depth,
            control_dependent_depth=control_dependent_depth,
        )

    def build_cfg(self):
        def build_pre_cfg(statements: list[Statement]):
            for i in range(len(statements)):
                cur_stat = statements[i]
                for post_stat in cur_stat.post_controls:
                    post_stat._pre_control_statements.append(cur_stat)
                if isinstance(cur_stat, BlockStatement):
                    build_pre_cfg(cur_stat.statements)

        build_pre_cfg(self.statements)
        if len(self.statements) > 0:
            self.statements[0]._pre_control_statements.insert(0, self)
            self._post_control_statements = [self.statements[0]]
        else:
            self._post_control_statements = []
        self._is_build_cfg = True

    def __build_cfg_graph(self, graph: nx.DiGraph, statments: list[Statement]):
        for stat in statments:
            color = "blue" if isinstance(stat, BlockStatement) else "black"
            graph.add_node(stat.signature, label=stat.dot_text, color=color)
            for post_stat in stat.post_controls:
                graph.add_node(post_stat.signature, label=post_stat.dot_text)
                graph.add_edge(stat.signature, post_stat.signature, label="CFG")
            if isinstance(stat, BlockStatement):
                self.__build_cfg_graph(graph, stat.statements)

    def __build_cdg_graph(self, graph: nx.MultiDiGraph, statments: list[Statement]):
        for stat in statments:
            color = "blue" if isinstance(stat, BlockStatement) else "black"
            graph.add_node(stat.signature, label=stat.dot_text, color=color)
            for post_stat in stat.post_control_dependents:
                graph.add_node(post_stat.signature, label=post_stat.dot_text)
                graph.add_edge(
                    stat.signature,
                    post_stat.signature,
                    label="CDG",
                    color="green",
                )
            if isinstance(stat, BlockStatement):
                self.__build_cdg_graph(graph, stat.statements)

    def __build_ddg_graph(self, graph: nx.MultiDiGraph, statments: list[Statement]):
        for stat in statments:
            color = "blue" if isinstance(stat, BlockStatement) else "black"
            graph.add_node(stat.signature, label=stat.dot_text, color=color)
            for identifier, post_stats in stat.post_data_dependents.items():
                for post_stat in post_stats:
                    graph.add_node(post_stat.signature, label=post_stat.dot_text)
                    graph.add_edge(
                        stat.signature,
                        post_stat.signature,
                        label=f"DDG [{identifier.text}]",
                        color="red",
                    )
            if isinstance(stat, BlockStatement):
                self.__build_ddg_graph(graph, stat.statements)

    def export_cfg_dot(
        self, path: str, with_cdg: bool = False, with_ddg: bool = False
    ) -> nx.DiGraph:
        """
        Exports the CFG of the function to a DOT file.

        Args:
            path (str): The path to save the DOT file.
            with_cdg (bool): Whether to include the Control Dependence Graph (CDG).
            with_ddg (bool): Whether to include the Data Dependence Graph (DDG).
        """
        if not self._is_build_cfg:
            self.build_cfg()
        graph = nx.MultiDiGraph()
        graph.add_node("graph", bgcolor="ivory", splines="true")
        graph.add_node(
            "node",
            fontname="SF Pro Rounded, system-ui",
            shape="box",
            style="rounded",
            margin="0.5,0.1",
        )
        graph.add_node("edge", fontname="SF Pro Rounded, system-ui", arrowhead="vee")
        graph.add_node(self.signature, label=self.dot_text, color="red")
        if self.first_statement is None:
            graph.add_node(
                self.signature, label="No statements found", color="red", shape="box"
            )
        else:
            graph.add_edge(self.signature, self.first_statement.signature, label="CFG")
        self.__build_cfg_graph(graph, self.statements)

        if with_cdg:
            self.__build_cdg_graph(graph, self.statements)

        if with_ddg:
            for identifier, post_stats in self.post_data_dependents.items():
                for post_stat in post_stats:
                    graph.add_node(post_stat.signature, label=post_stat.dot_text)
                    graph.add_edge(
                        self.signature,
                        post_stat.signature,
                        label=f"DDG [{identifier.text}]",
                        color="red",
                    )
            self.__build_ddg_graph(graph, self.statements)

        nx.nx_pydot.write_dot(graph, path)
        return graph


class FunctionDeclaration:
    """
    Represents a function declaration in the code.

    For example, in C/C++, this would be a function prototype without the body.
    """

    name: str
    """
    The name of the function declaration.
    """

    text: str
    """
    The text of the function declaration.
    """

    file: File
    """
    The file where the function declaration is located.
    """

    def __init__(self, name: str, text: str, file: File):
        self.name = name
        self.text = text
        self.file = file

    def __hash__(self):
        return hash(self.signature)

    def __str__(self) -> str:
        return self.name

    @property
    def signature(self) -> str:
        """
        The unique signature of the function declaration.
        """
        return self.name + self.text + self.file.abspath

    @property
    def dot_text(self) -> str:
        return self.name
