Markov Text Generator
=====================

This Python script generates pseudo-random text using a Markov chain model.  
The Markov chain encodes the statistical properties of a source text with a user-specified n-gram length.  
More details on the algorithm can be found on the following page:  
http://www.cs.princeton.edu/courses/archive/spr05/cos126/assignments/markov.html  

The script can be used with two kind of sources:  
1. A text file from which the Markov chain is built.  
2. A text file with a pre-generated Markov chain from a previous run.  

The generated text can be output on the console or written to a file,  
while the Markov chain can be exported to a file and used later.  

Usage examples:  

    generate_markov_text -s input_text.txt -l 7 -n 1000 -o output_file.txt -w markov.txt  

Generates 1000 letters using a 7 letter n-gram and writes the Markov chain to "markov.txt".  

    generate_markov_text -r markov.txt -n 1000 -c  
Reads a Markov chain from a file and prints 1000 letters on the console.  
