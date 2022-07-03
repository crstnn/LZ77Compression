#!/usr/bin/python3.10
import sys

from bitarray import bitarray

from LZ77Compression.LZ77 import lz_77_encode_binary
from LZ77Compression.Utils.convert_base import convert_base_2_to_10, convert_base_10_to_2_fixed_width
from LZ77Compression.elias_omega_coding import elias_generalised_decode, elias_generalised_encode
from LZ77Compression.huffman_coding import create_huffman_table

ASCII_FIXED_BINARY_WIDTH = 8


def decode_character_metadata_format(sequence: bitarray, start_index: int) -> tuple[int, str, bitarray]:
    """Represents convention/format for decoding (of the original encoding).
    For different formats replace the callers of this function to another `..._format` function
    Both decode and encode `..._format` functions must match"""
    ascii_8bit = chr(convert_base_2_to_10(sequence[start_index:start_index + ASCII_FIXED_BINARY_WIDTH]))
    start_index += ASCII_FIXED_BINARY_WIDTH
    huffman_encoding_len, sequence_consumed_in_decode = elias_generalised_decode(sequence, start_index)
    start_index += sequence_consumed_in_decode
    huffman_encoding = sequence[start_index:start_index + huffman_encoding_len]
    start_index += huffman_encoding_len
    return start_index, ascii_8bit, huffman_encoding


def decode_character_metadata(encoding: bitarray, start_index: int) -> tuple[list[tuple[str, bitarray]], int]:
    character_encoding_pairs: list[tuple[str, bitarray]] = []
    number_of_distinct_chars, read_len = elias_generalised_decode(encoding, start_index)
    i = start_index + read_len
    while len(character_encoding_pairs) < number_of_distinct_chars:
        i, ascii_char, huffman_encoding = decode_character_metadata_format(encoding, i)
        character_encoding_pairs.append((ascii_char, huffman_encoding))
    return character_encoding_pairs, i


def encode_metadata_character_format(char: str, huffman_encoding: bitarray) -> bitarray:
    """Represents convention/format for encoding.
    For different formats replace the callers of this function to another `..._format` function.
    Both decode and encode `..._format` functions must match"""
    encoding = convert_base_10_to_2_fixed_width(ord(char), ASCII_FIXED_BINARY_WIDTH)
    encoding.extend(elias_generalised_encode(len(huffman_encoding)))
    encoding.extend(huffman_encoding)
    return encoding


def encode_character_metadata(encodings: tuple[bitarray, ...]) -> bitarray:
    character_encoding: bitarray = bitarray()
    for u_v, huff_encoding in enumerate(encodings):
        if huff_encoding is not None:
            character_encoding.extend(encode_metadata_character_format(chr(u_v), huff_encoding))
    return character_encoding


def zip_string(txt: str, search_window_size: int, lookahead_buffer_size: int) -> bitarray:
    """
    The final string that gets zipped consists of 3 parts, respectively:
        - Elias encoding of the number of distinct characters in the `txt`
        - Huffman codes for each distinct letter (ASCII representation then Huffman code following it)
        - LZ77 triples encodings:
            `offset` (Elias coding) `length` (Elias coding) and `next_unmatched_symbol` (Huffman coding)

    """
    encodings_by_unicode_value: tuple[bitarray, ...] = create_huffman_table(txt)
    number_of_encodings = sum(b is not None for b in encodings_by_unicode_value)
    number_of_distinct_chars = elias_generalised_encode(number_of_encodings)
    encoded_character_metadata = encode_character_metadata(encodings_by_unicode_value)

    txt_encoding = lz_77_encode_binary(txt, encodings_by_unicode_value, search_window_size, lookahead_buffer_size)

    return number_of_distinct_chars + encoded_character_metadata + txt_encoding


def zip_file(txt: str, file_name: str, search_window_size: int = 1000, lookahead_buffer_size: int = 300):
    """
    The final string that gets zipped consists of multiple parts, respectively:
        - Length of `file_name` based on binary ASCII representation (Elias coded) then the binary ASCII representation
        of `file_name` itself
        - Number of character in `txt` (Elias coded)
        - return of `zip_string` which zips `txt`'s contents (see `zip_string` docstring)

    """
    filename_chars_ascii_encoded = bitarray()
    for c in map(ord, list(file_name)):
        filename_chars_ascii_encoded.extend(convert_base_10_to_2_fixed_width(c, ASCII_FIXED_BINARY_WIDTH))

    return elias_generalised_encode(len(file_name)) + filename_chars_ascii_encoded + \
           elias_generalised_encode(len(txt)) + zip_string(txt, search_window_size, lookahead_buffer_size)


def main():
    """CLI input: python myzip.py <inputfilename> <search window> <lookahead_buffer>"""
    file_name: str = sys.argv[1]
    text: str = open(file_name, "r").read()
    search_window_size: int = int(sys.argv[2])
    lookahead_buffer_size: int = int(sys.argv[3])
    zip_bin = zip_file(text, file_name, search_window_size, lookahead_buffer_size)
    with open(file_name + ".bin", "wb") as output_file:
        zip_bin.tofile(output_file)


if __name__ == "__main__":
    main()
    # print(zip_file("aacaacabcaba", "test.asc"))

