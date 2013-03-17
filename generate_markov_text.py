# This script generates pseudo-random text using a Markov chain model.
# The Markov chain encodes the statistical properties of a source text
# with a user-specified n-gram length.
# More details on the algorithm can be found on the following page:
# http://www.cs.princeton.edu/courses/archive/spr05/cos126/assignments/markov.html
#
# The script can be used with two kind of sources:
# 1. A text file from which the Markov chain is built.
# 2. A text file with a pre-generated Markov chain from a previous run.
#
# The generated text can be output on the console or written to a file,
# while the Markov chain can be exported to a file and used later.
#
# Usage examples:
#    generate_markov_text -s input_text.txt -l 7 -n 1000 -o output_file.txt -w markov.txt
#       generates 1000 letters using a 7 letter n-gram
#       and writes the Markov chain to "markov.txt"
#    generate_markov_text -r markov.txt -n 1000 -c
#       reads the Markov chain from a file and prints 1000 letters on the console
#
# For usage information execute the script with the --help flag.
from random import *
from optparse import *
import string

class MarkovChainNode:
    def __init__(self, ngram):
        self.ngram = ngram
        self.next_states = []

    def add_next_state(self, node, probability):
        self.next_states.append((node, probability))
        self.next_states.sort(key = lambda pair : pair[1], reverse = True)

    def get_next_state(self):
        # Randomly select a next node from the chain, giving higher
        # priority to the letters that follow this n-gram more often.
        probability = random()

        for state in self.next_states:
            if probability < state[1]:
                return state[0]
            else:
                probability -= state[1]

        # The input text is treated like a circular buffer,
        # so all chain nodes should have a next state.
        raise Exception("No next state found for '{0}", self.ngram)


def compute_ngram_counts(text, k):
    ngrams = {}
    text_length = len(text)

    if text_length < k:
        # Text is too short to extract anything useful.
        raise Exception("Text is too short. Provide more than {0} characters".format(k))

    for i in range(0, text_length):
        # Extract the n-gram from positions [i, i + k).
        # If it extends beyond the text, letters from the beginning are taken.
        if i + k < text_length:
            ngram = text[i : i + k]
        else:
            ngram = text[i : text_length] + \
                    text[0 : (k - (text_length - i))]

        # Look at the letter following the n-gram and increase the count
        # associated with it. If it is the first time it is seen, the count is 1.
        next_letter = text[i + k] if i + k < text_length else \
                      text[k - (text_length - i)]

        # The letters following a n-gram are stored as a dictionary of
        # (letter : occurrence_count) pairs.
        if not ngram in ngrams:
            ngrams[ngram] = {}

        next_ngram_letters = ngrams[ngram]

        if next_letter in next_ngram_letters:
            next_ngram_letters[next_letter] += 1
        else:
            next_ngram_letters[next_letter] = 1

    return ngrams


def print_ngram_counts(ngrams):
    for ngram, next_letters in ngrams.items():
        print("n-gram '{0}':".format(ngram))

        for letter, count in next_letters.items():
            print("    {0}: {1}".format(letter, count))


def read_source_file(file_path):
    with open(file_path, "r") as file:
        return file.read()


def string_to_decimal(text):
    return " ".join([str(ord(letter)) for letter in text])


def string_from_decimal(decimal):
    return "".join([chr(int(number)) for number in decimal.split()])


def write_ngram_counts_to_file(ngrams, ngram_length, file_path):
    with open(file_path, "w") as file:
        # On the first line write the length and number of n-grams,
        # then each n-gram on a separate line.
        file.write("{0} {1}\n".format(ngram_length, len(ngrams)))

        for ngram, next_letters in ngrams.items():
            # Write the n-gram, the letter number and the letter-count pairs.
            file.write("{0} {1} ".format(string_to_decimal(ngram), len(next_letters)))

            for letter, count in next_letters.items():
                file.write("{0} {1} ".format(string_to_decimal(letter), count))

            file.write("\n")


def read_ngram_counts_from_file(file_path):
    ngrams = {}
    ngram_length = 0

    with open(file_path, "r") as file:
        # Read the length and the number of n-grams.
        ngram_length, ngram_count = [int(number) for number in file.readline().split()]

        for i in range(0, ngram_count):
            # The line begins with the n-gram having each letter in decimal,
            # followed by the number of letter-count pairs.
            ngram_info = file.readline().split()
            ngram_value = string_from_decimal(" ".join(ngram_info[0:ngram_length]))
            next_letter_count = int(ngram_info[ngram_length])

            # Read the letter-count pairs.
            next_letters = {}

            for j in range(0, next_letter_count):
                letter = string_from_decimal(ngram_info[1 + ngram_length + (j * 2)])
                count = int(ngram_info[1 + ngram_length + (j * 2 + 1)])
                next_letters[letter] = count

            ngrams[ngram_value] = next_letters

    return (ngrams, ngram_length)


def build_markov_chain(ngrams):
    # First build the Markov nodes for all n-grams,
    # then connect the nodes using the next-letter information.
    chain_nodes = {}

    for ngram in ngrams:
        chain_nodes[ngram] = MarkovChainNode(ngram)

    for ngram, next_letters in ngrams.items():
        # For each letter compute the probability that it follows after the n-gram.
        weight = float(sum((count for letter, count in next_letters.items())))
        node = chain_nodes[ngram]

        for letter, count in next_letters.items():
            # The next n-gram consists of the first K-1 letters
            # from the current node and the last letter from the next node.
            next_state_ngram = ngram[1:] + letter
            next_state_node = chain_nodes[next_state_ngram]
            node.add_next_state(next_state_node, count / weight)

    return chain_nodes


def generate_text(chain, length):
    # Randomly select one of the chain nodes as the start node.
    # For the start node the entire n-gram is used, while for the next
    # states only the last character, until the required length is reached.
    ngrams = [key for key in chain.keys()]
    node = chain[choice(ngrams)]

    text = []
    text_length = len(node.ngram)
    
    for letter in node.ngram:
        text.append(letter)
    
    while text_length < length:
        node = node.get_next_state()
        text.append(node.ngram[-1])
        text_length += 1

    return "".join(text)


def write_text_to_file(text, file_path, words_per_line = 12):
    with open(file_path, "w") as file:
        words = 0
        
        for letter in text:
            if letter in string.whitespace:
                words += 1
                file.write("\n" if (words % words_per_line == 0) else letter)
            else:
                file.write(letter)


def main():
    parser = OptionParser()
    parser.add_option("-s", "--source", dest = "source",
                      help = "The file containing the text to be analyzed.")
    parser.add_option("-l", "--length", dest = "length",
                      help = "The length of the used n-gram (in letters).")
    parser.add_option("-n", "--number", dest = "number",
                      help = "The number of letters the output text should contain.")
    parser.add_option("-c", "--console", dest = "console", action = "store_true",
                      help = "Print the output text on the console.")
    parser.add_option("-o", "--output", dest = "output",
                      help = "The file where the output text should be written.")
    parser.add_option("-r", "--read_markov", dest = "read_markov",
                      help = "The file from where to read the Markov chains.")
    parser.add_option("-w", "--write_markov", dest = "write_markov",
                      help = "The file where to write the Markov chains.")
    options, args = parser.parse_args()
    
    # There are two supported work modes:
    # 1. Input text read from a file, followed by building the Markov chain.
    # 2. Pre-generated Markov chain read from a file.
    ngrams = None
    ngram_length = None
    output_text = None
    
    if options.number is None:
        print("Length of output text not specified!")
        return -1
    elif options.console is None and options.output is None:
        print("No type of output specified!")
        return -1
    
    if options.source is not None:
        if options.read_markov is not None:
            print("Source file and Markov chain file cannot be used at the same time!")
            return -1
        elif options.length is None:
            print("Length of used n-gram not specified!")
            return -1
        
        print("Generating {0} letters from source file {1}". \
              format(options.number, options.source))
        ngram_length = int(options.length)
        text = read_source_file(options.source)
        ngrams = compute_ngram_counts(text, ngram_length)
    else:
        if options.read_markov is None:
            print("A data source must be specified!")
            return -1
        
        print("Generating {0} letters from Markov chain file {1}". \
              format(options.number, options.read_markov))
        ngrams, ngram_length = read_ngram_counts_from_file(options.read_markov)
    
    # Now build the Markov chain and create the text.
    chain = build_markov_chain(ngrams)
    output_text = generate_text(chain, int(options.number))
    
    if options.console is not None:
        print("Output text: {0}".format(output_text))
        
    if options.output is not None:
        write_text_to_file(output_text, options.output)
        
    if options.write_markov is not None:
        write_ngram_counts_to_file(ngrams, ngram_length, options.write_markov)
    
    return 0


if __name__ == '__main__':
    main()
