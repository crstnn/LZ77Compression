#!/usr/bin/python3.10
from collections import namedtuple
from bitarray import bitarray

from LZ77Compression.Utils.gusfields_z_alg import z_alg
from LZ77Compression.Utils.huffman_tree import Vertex
from LZ77Compression.elias_omega_coding import elias_generalised_decode, elias_generalised_encode
from LZ77Compression.huffman_coding import huffman_encode, huffman_decode

EncodingTriple = namedtuple("EncodingTriple", ["offset", "length", "next_unmatched_symbol"])


def check_for_match(string: str, sw_start_idx: int, lb_start_idx: int, lb_end_idx: int) -> EncodingTriple | bool:
    if sw_start_idx == lb_start_idx: return False
    lookahead_buffer_list = list(map(ord, string[lb_start_idx:lb_end_idx]))
    search_window_list = list(map(ord, string[sw_start_idx:lb_start_idx]))
    search_section = search_window_list + lookahead_buffer_list
    # Design note: Z-alg was chosen due to simplicity but in practice a suffix array/tree with dynamic deletes
    # would be far more efficient and appropriate
    matches = z_alg(lookahead_buffer_list + [max(search_section) + 1] + search_section)

    lb_size = lb_end_idx - lb_start_idx
    sw_with_lb_matches = matches[lb_size + 1:len(matches) - lb_size]

    maximum_match = max(sw_with_lb_matches)
    if maximum_match == 0: return False
    sw_idx = sw_with_lb_matches.index(maximum_match)
    if lb_start_idx + maximum_match >= len(string):
        # Reduces the match length by 1, so that there exists a `next_unmatched_symbol`. This prevents a match that goes
        # to end of the string, writing redundant zero length triples due to there being no `next_unmatched_symbol` at
        # the end of string.
        maximum_match -= 1
    return EncodingTriple(lb_start_idx - (sw_idx + sw_start_idx), maximum_match, string[lb_start_idx + maximum_match])


def lz_77_encode(string_to_encode: str, search_window_size: int, lookahead_buffer_size: int) -> list[EncodingTriple]:
    def window_start_index(comp_idx):
        if comp_idx - search_window_size < 0:
            return 0
        return comp_idx - search_window_size

    def lookahead_buffer_end_index(comp_idx):
        if comp_idx + lookahead_buffer_size < len(string_to_encode):
            return comp_idx + lookahead_buffer_size
        return len(string_to_encode)

    encoding: list[EncodingTriple] = []
    comparison_point_idx = 0
    while comparison_point_idx < len(string_to_encode):

        match = check_for_match(string_to_encode,
                                window_start_index(comparison_point_idx),
                                comparison_point_idx,
                                lookahead_buffer_end_index(comparison_point_idx))

        if not match:
            match = EncodingTriple(0, 0, string_to_encode[comparison_point_idx])

        encoding.append(match)
        comparison_point_idx += match.length + 1

    return encoding


def lz_77_decode(encoding: list[EncodingTriple]) -> str:
    decoding: list[str] = []
    for e in encoding:
        decoding = lz_77_decode_by_triple(decoding, e)
    return ''.join(decoding)


def lz_77_decode_by_triple(decoding: list[str], encoding: EncodingTriple) -> list[str]:
    backshift_index = len(decoding) - encoding.offset
    search_window_match = decoding[backshift_index: backshift_index + encoding.length]
    excess_in_lookahead_buffer = backshift_index + encoding.length - len(decoding)
    if excess_in_lookahead_buffer > 0:
        tot_window_match = search_window_match * (excess_in_lookahead_buffer // len(search_window_match) + 1)
        search_window_match.extend(tot_window_match[:excess_in_lookahead_buffer])
    decoding.extend(search_window_match + [encoding.next_unmatched_symbol])

    return decoding


def lz_77_encode_binary(string_to_encode: str, encoding_table: tuple[bitarray, ...],
                        search_window_size: int, lookahead_buffer_size: int) -> bitarray:
    lz_77_encoding = lz_77_encode(string_to_encode, search_window_size, lookahead_buffer_size)

    lz_77_binary_encoding: bitarray = bitarray()

    for e in lz_77_encoding:
        lz_77_binary_encoding.extend(elias_generalised_encode(e.offset))
        lz_77_binary_encoding.extend(elias_generalised_encode(e.length))
        lz_77_binary_encoding.extend(huffman_encode(e.next_unmatched_symbol, encoding_table))

    return lz_77_binary_encoding


def lz_77_decode_binary(encoding: bitarray, decode_tree: Vertex, number_of_chars_file_contents: int,
                        start_index: int = 0) -> str:
    decoding: list[str] = []

    idx = start_index
    while len(decoding) < number_of_chars_file_contents:
        decoded_offset, read_len = elias_generalised_decode(encoding, idx)
        idx += read_len
        decoded_length, read_len = elias_generalised_decode(encoding, idx)
        idx += read_len
        next_unmatched_symbol, read_len = huffman_decode(encoding, idx, decode_tree)
        idx += read_len
        decoding = lz_77_decode_by_triple(decoding,
                                          EncodingTriple(decoded_offset, decoded_length, next_unmatched_symbol))

    return ''.join(decoding)


if __name__ == "__main__":
    string_to_encode = "ratatatatat_a_rat_at_a_rat"
    encoding = lz_77_encode(string_to_encode, 15, 15)
    print(encoding)
    decoding = lz_77_decode(encoding)
    print(decoding)
    assert string_to_encode == decoding
