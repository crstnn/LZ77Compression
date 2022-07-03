from LZ77Compression.Utils.huffman_tree import Vertex

# FROM MY FIT2004 submission (adjusted and refactored)


class MinHeap:
    """Standard minimum heap"""
    left_child: int = lambda v: 2 * v + 1
    right_child: int = lambda v: 2 * v + 2
    parent: int = lambda v: (v - 1) // 2

    def __init__(self):
        self.elements: list[Vertex] = []

    def _percolate_down(self, index: int) -> None:
        smallest_idx = index
        smallest_vertex = self.elements[smallest_idx]
        left_idx = MinHeap.left_child(index)
        right_idx = MinHeap.right_child(index)
        if left_idx < len(self.elements) and smallest_vertex > self.elements[left_idx]:
            smallest_idx = left_idx
            smallest_vertex = self.elements[smallest_idx]
        if right_idx < len(self.elements) and smallest_vertex > self.elements[right_idx]:
            smallest_idx = right_idx

        if smallest_idx != index:
            self.elements[index], self.elements[smallest_idx] = self.elements[smallest_idx], self.elements[index]
            self._percolate_down(smallest_idx)

    def _percolate_up(self, index: int) -> None:
        if index <= 0:
            return
        parent_idx = MinHeap.parent(index)
        if self.elements[index] < self.elements[parent_idx]:
            # swap element places
            self.elements[index], self.elements[parent_idx] = self.elements[parent_idx], self.elements[index]
            self._percolate_up(parent_idx)

    def add_vertex(self, vertex: Vertex):
        self.elements.append(vertex)
        self._percolate_up(len(self.elements)-1)

    def pop_min(self) -> Vertex:
        self.elements[0], self.elements[-1] = self.elements[-1], self.elements[0]  # swap element places
        min_node = self.elements.pop()
        if len(self.elements) > 1:
            self._percolate_down(0)  # percolate down from the root (hence `0`)
        return min_node

    def is_empty(self):
        return len(self.elements) == 0

    def size(self):
        return len(self.elements)
