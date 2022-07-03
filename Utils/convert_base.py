#!/usr/bin/python3.10
from math import log2, floor

from bitarray import bitarray


def convert_base_10_to_2(integer: int) -> bitarray:
    number_of_bits_to_represent_integer = floor(log2(integer)) + 1
    bit_array = bitarray(number_of_bits_to_represent_integer)
    number = integer
    i = number_of_bits_to_represent_integer
    while number > 0:
        i -= 1
        bit = number % 2
        quotient = number // 2
        bit_array[i] = bit
        number = quotient

    return bit_array


def convert_base_2_to_10(bits: bitarray):
    number = 0
    for bit in bits:
        number = (number << 1) | bit
    return number


def convert_base_10_to_2_fixed_width(integer: int, fixed_width: int) -> bitarray:
    conv = convert_base_10_to_2(integer)
    return ((fixed_width - len(conv)) * bitarray('0')) + conv

if __name__ == "__main__":
    print(convert_base_10_to_2(908127343))
    print(convert_base_2_to_10(bitarray('0011010')))
