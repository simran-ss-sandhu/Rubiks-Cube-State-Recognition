import pickle
import os

FLIP_BIT = ['1', '0']  # element = opposite bit of index
SIX_MINUS_INDEX = [6, 5, 4, 3, 2, 1, 0]  # element = 6 - index

# element of COUNT_ONES = the number of 1's in the binary version of the index
# loads COUNTS_ONES list from pickle file
try:
    with open(os.path.join('data', 'count_ones.pkl'), 'rb') as file:
        COUNT_ONES = pickle.load(file)  # stores the list in a constant variable

# creates and stores COUNT_ONES list if it does not exist
except FileNotFoundError:
    with open(os.path.join('data', 'count_ones.pkl'), 'wb') as file:
        COUNT_ONES = []

        # the largest bit string length is 12 (for edge cubies). Base is 2 as the bit string is binary.
        iterations = 2 ** 12

        # counts and stores the number of ones in the binary equivalent of each number
        for number in range(iterations):
            COUNT_ONES.append(bin(number).count('1'))

        pickle.dump(COUNT_ONES, file, pickle.HIGHEST_PROTOCOL)  # writes the list to a pickle file


class IndexCalculator:
    def __init__(self, number_of_cubies: int, lehmer_bases: list, orientation_bases: list):
        self.number_of_cubies = number_of_cubies  # the number of cubies (8 for corners, 12 for edges)
        self.empty_bit_string = '0' * self.number_of_cubies  # 0 as a 8 bit string
        self.lehmer_bases = lehmer_bases  # lehmer bases specialised for the current cubies group (corners/edges)
        self.orientation_bases = orientation_bases
        self.hash_index = None  # the hash index associated with the current permutation

    def __calculate_lehmer_code(self, cubie_positions_permutation: list):
        bit_string = self.empty_bit_string

        # processes first digit of permutation
        first_digit = cubie_positions_permutation[0]
        self.lehmer_code = [first_digit]  # permutation[0] = lehmer_code[0] is always true (no elements less than it)
        bit_string = bit_string[:first_digit] + '1' + bit_string[first_digit + 1:]  # flips bit[i] where i = 1st digit

        # second to second last digit
        rest_of_permutation = cubie_positions_permutation[1:]  # the permutation from the 2nd digit
        for digit in rest_of_permutation:
            flipped_bit = FLIP_BIT[int(bit_string[digit])]  # the flipped bit at the index where index = digit

            # replaces the un-flipped bit at the index where index = digit
            bit_string = bit_string[:digit] + flipped_bit + bit_string[digit + 1:]

            # works out the number of elements that are less than digit by counting the number of ones in the
            # binary shift of the bitstring by the (number of cubies - digit)
            number_of_elements_less = COUNT_ONES[int(bit_string, 2) >> (self.number_of_cubies - digit)]

            lehmer_digit = digit - number_of_elements_less  # the digit - number of elements less than the digit
            self.lehmer_code.append(lehmer_digit)  # appends lehmer digit to the lehmer code

    def __add_decimal_lehmer_code(self):
        # converts lehmer code to decimal and adds it to the hash index
        for lehmer_base, lehmer_digit in zip(self.lehmer_bases, self.lehmer_code):
            self.hash_index += int(lehmer_base * lehmer_digit)

    def __add_orientations_rank(self, cubie_orientations_permutation: list):
        # converts permutation to decimal
        for base_power, permutation_digit in zip(SIX_MINUS_INDEX, cubie_orientations_permutation):
            self.hash_index += self.orientation_bases[base_power] * permutation_digit

    def calculate_hash_index(self, cubie_positions_permutation: list, cubie_orientations_permutation: list) -> int:
        self.hash_index = 0

        # adds the position rank
        self.__calculate_lehmer_code(cubie_positions_permutation)  # calculates the lehmer code of the permutation
        self.__add_decimal_lehmer_code()  # converts the lehmer code to base 10 (the hash_index)

        # multiplication avoids duplicate hash indexes
        self.hash_index = self.hash_index * self.orientation_bases[7]

        # adds the orientations rank
        self.__add_orientations_rank(cubie_orientations_permutation)

        return self.hash_index
