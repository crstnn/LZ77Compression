#!/usr/bin/python3.10
from bitarray import bitarray
from LZ77Compression.Utils.huffman_tree import Vertex
from LZ77Compression.Utils.min_heap import MinHeap


def create_huffman_table(sequence: str) -> tuple[bitarray, ...]:
    """
    Huffman coding: FOR ENCODING
    :return: a lookup table indexed by its unicode integer representation (using `ord`). each element contains its
    """
    sequence_unicode: list[int] = list(map(ord, sequence))
    max_symbol: int = max(sequence_unicode)

    idx_to_chr = lambda i: chr(i)
    char_to_idx = lambda c: ord(c)
    symbol_count: list[int] = [0] * (max_symbol + 1)

    for el in sequence_unicode:
        symbol_count[el] += 1

    min_heap = MinHeap()

    for idx, count in enumerate(symbol_count):
        if count:
            min_heap.add_vertex(Vertex.create_leaf_vertex(idx_to_chr(idx), count))

    while min_heap.size() > 1:
        highest_priority = min_heap.pop_min()
        second_highest_priority = min_heap.pop_min()
        new_vert = Vertex(highest_priority.count + second_highest_priority.count)
        new_vert.set_children(highest_priority, second_highest_priority)
        min_heap.add_vertex(new_vert)

    root = min_heap.pop_min()

    encodings_by_unicode_value = tuple(bitarray() if s != 0 else None for s in symbol_count)

    visited = [False] * (Vertex.vertex_id_counter * (Vertex.vertex_id_counter + 1))  # finished tree has n(n-1) vertices
    current_encoding = bitarray()

    def dfs(v):
        visited[v.id] = True
        if v.is_leaf():
            encodings_by_unicode_value[char_to_idx(v.char)].extend(current_encoding)
        for (bin_e_num, child_edge) in v.get_children():  # traverse down the two (binary) edges
            if child_edge is not None and not visited[child_edge.id]:
                current_encoding.append(bin_e_num)
                dfs(child_edge)
                current_encoding.pop()

    dfs(root)

    return encodings_by_unicode_value


def create_huffman_pairs(huffman_table: tuple[bitarray, ...]) -> list[tuple[str, bitarray]]:
    pairs = []

    for idx, huff_code in enumerate(huffman_table):
        if huff_code:
            p = (chr(idx), huff_code)
            print(p)
            pairs.append(p)

    return pairs

def create_huffman_tree(encoding_pairs: list[tuple[str, bitarray]]) -> Vertex:
    """
    Huffman coding: FOR DECODING
    :return: the root vertex for the (decode) Huffman tree.
    """

    ROOT = Vertex.create_empty_vertex()
    for (char, huffman_encoding) in encoding_pairs:
        curr_vertex = ROOT
        for idx, b in enumerate(huffman_encoding):
            if curr_vertex.get_child(b) is None:
                curr_vertex.set_child(b, Vertex.create_empty_vertex())
            curr_vertex = curr_vertex.get_child(b)
            if idx == len(huffman_encoding) - 1:
                curr_vertex.char = char

    return ROOT


def huffman_encode(char: str, encoding_table: tuple[bitarray, ...]) -> bitarray:
    return encoding_table[ord(char)]


def huffman_decode(sequence: bitarray, start_index: int, decode_tree_root: Vertex) -> tuple[str, int]:
    current_child = decode_tree_root
    idx = start_index
    while True:
        current_child = current_child.get_child(sequence[idx])
        idx += 1
        if current_child is None: raise Exception("Huffman code does not exist in tree")
        if current_child.is_leaf(): return current_child.char, idx - start_index



if __name__ == "__main__":
    string_to_encode = "-a;raiahhhrsnlharri"
    encoding_table = create_huffman_table(string_to_encode)
    print(create_huffman_pairs(encoding_table))
    print(encoding_table)
    decoding_tree = create_huffman_tree([("A", bitarray('10')),
                                         ("B", bitarray('1111')),
                                         ("C", bitarray('1110')),
                                         ("D", bitarray('00')),
                                         ("E", bitarray('110')),
                                         ("_", bitarray('01'))])

