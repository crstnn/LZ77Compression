#!/usr/bin/python3.10
from bitarray import bitarray

from LZ77Compression.Utils.convert_base import convert_base_10_to_2, convert_base_2_to_10


def elias_encode(number: int) -> bitarray:
    elias_encoding = curr_bin_rep = convert_base_10_to_2(number)
    elias_encoding.reverse()

    while len(curr_bin_rep) > 1:
        length_component = convert_base_10_to_2(len(curr_bin_rep) - 1)
        length_component[0] = 0
        length_component.reverse()
        elias_encoding.extend(length_component)
        curr_bin_rep = length_component

    elias_encoding.reverse()
    return elias_encoding


def elias_decode(sequence: bitarray, start_index: int = 0) -> tuple[int, int]:
    component_read_len = 1
    pos = start_index

    while True:
        component = sequence[pos: pos + component_read_len]
        if component[0]:
            return convert_base_2_to_10(component), pos + component_read_len - start_index
        else:
            component[0] = 1
            pos += component_read_len
            component_read_len = convert_base_2_to_10(component) + 1


def elias_generalised_encode(number: int, offset: int = 1) -> bitarray:
    """
    Elias coding encodes positive integers, this function allows a wider range of integers to be encoded
    :param number: Number to be encoded
    :param offset: Count of the numbers below 1 (that have been chosen a priori).
                   Default value (1) models non-negative integers i.e. integer range: [0, inf).
                   And offset > 1 models the integer range: (-offset, inf).
    """
    return elias_encode(number + offset)


def elias_generalised_decode(sequence: bitarray, start_index: int = 0, offset: int = 1) -> tuple[int, int]:
    """
    Decodes the result of `elias_generalised_encode`.
    Pre-condition: `elias_generalised_encode`.offset == `elias_generalised_decode`.offset
    :param sequence: Bits to be decoded
    :param start_index: specify array start index to decode from. This avoids splicing array from start index to end of
                    array which could be an expensive operation
    :param offset: Count of the numbers below 1 (that have been chosen a priori).
                   Default value (1) models non-negative integers i.e. integer range: [0, inf).
                   And offset > 1 models the integer range: (-offset, inf).
    :return: tuple(decoded input sequence, length of sequence consumed in decode operation)
    """
    decoded_sequence, read_length = elias_decode(sequence, start_index)
    return decoded_sequence - offset, read_length


if __name__ == "__main__":
    print(elias_encode(1))
    print(elias_decode(bitarray('01')))
