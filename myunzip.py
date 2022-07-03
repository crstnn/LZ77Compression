#!/usr/bin/python3.10
import sys

from bitarray import bitarray

from LZ77Compression.LZ77 import lz_77_decode_binary
from LZ77Compression.Utils.convert_base import convert_base_2_to_10
from LZ77Compression.Utils.huffman_tree import Vertex
from LZ77Compression.elias_omega_coding import elias_generalised_decode
from LZ77Compression.huffman_coding import create_huffman_tree
from LZ77Compression.myzip import decode_character_metadata, ASCII_FIXED_BINARY_WIDTH


def unzip_bits(encoding: bitarray, number_of_chars_file_contents: int, start_index: int = 0) -> str:
    encoding_pairs, index = decode_character_metadata(encoding, start_index)
    huffman_tree_root: Vertex = create_huffman_tree(encoding_pairs)
    return lz_77_decode_binary(encoding, huffman_tree_root, number_of_chars_file_contents, index)


def unzip_file(encoding: bitarray):
    """Adheres to zipping convention in `myzip.py`"""
    filename_chars_ascii = []
    chars_for_filename_count, index = elias_generalised_decode(encoding)
    count = 0
    while count < chars_for_filename_count:
        filename_chars_ascii.append(chr(convert_base_2_to_10(encoding[index: index + ASCII_FIXED_BINARY_WIDTH])))
        index += ASCII_FIXED_BINARY_WIDTH
        count += 1
    file_name = "".join(filename_chars_ascii)
    number_of_chars_file_contents, read_len = elias_generalised_decode(encoding, index)
    index += read_len
    return file_name, unzip_bits(encoding, number_of_chars_file_contents, index)


def main():
    file_name_to_read: str = sys.argv[1]
    file_content_bits = bitarray()
    with open(file_name_to_read, 'rb') as f:
        file_content_bits.fromfile(f)
    file_name_to_write, decoding = unzip_file(file_content_bits)
    with open(file_name_to_write, "w") as output_file:
        output_file.write(decoding)


if __name__ == "__main__":
    main()
    # print(unzip_file(bitarray('0011001011101000110010101110011011101000010111001100001011100110110001100111010001000110000101010110001001100011000110110111101001001000100000101000001000001001')))
