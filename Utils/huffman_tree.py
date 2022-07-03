from __future__ import annotations
from collections.abc import Iterable

class Vertex:
    vertex_id_counter = 0

    def __init__(self, count: int | None):
        self.id: int = Vertex.increment_vertex_id()
        self.char: str | None = None  # internal vertices don't have a character assigned
        self.count: int | None = count  # only `int` for encoding otherwise for decoding it is `None`

        # zero and one corresponding to the binary codes assigned
        self.edge_zero: Vertex | None = None
        self.edge_one: Vertex | None = None
        self.parent: Vertex | None = None  # in final tree only root has its parent as `None`

    def __lt__(self, other_vert: Vertex):
        return self.count < other_vert.count

    def __gt__(self, other_vert: Vertex):
        return self.count > other_vert.count

    def __eq__(self, other_vert: Vertex):
        return self.count == other_vert.count

    def __le__(self, other_vert: Vertex):
        return self == other_vert and self < other_vert

    def __ge__(self, other_vert: Vertex):
        return self == other_vert and self > other_vert

    def __repr__(self):
        return f'char: {self.char}, count: {self.count}, 0: ({self.edge_zero}), 1: ({self.edge_one})'

    def is_leaf(self) -> bool:
        return self.edge_zero is None is self.edge_one

    def is_root(self):
        return self.char is None is self.parent

    def set_parent(self, parent: Vertex):
        self.parent = parent

    def get_child(self, value: int) -> Vertex | None:
        if value == 0:
            return self.edge_zero
        elif value == 1:
            return self.edge_one

    def get_children(self) -> Iterable[tuple[int, Vertex]]:
        return iter(((0, self.edge_zero), (1, self.edge_one)))

    def set_child(self, value: int, child_vertex: Vertex):
        if value == 0:
            self.edge_zero = child_vertex
        elif value == 1:
            self.edge_one = child_vertex

    def set_children(self, zero_edge: Vertex, one_edge: Vertex) -> None:
        self.set_child(0, zero_edge)
        self.set_child(1, one_edge)

    @classmethod
    def increment_vertex_id(cls):
        cls.vertex_id_counter += 1
        return cls.vertex_id_counter

    @staticmethod
    def create_leaf_vertex(char: str, count: int):
        v = Vertex(count)
        v.char = char
        return v

    @staticmethod
    def create_empty_vertex():
        return Vertex(None)
