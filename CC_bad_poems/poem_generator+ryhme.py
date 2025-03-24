import random
import os
import string
import nltk
import pronouncing
from nltk.corpus import cmudict

pronouncing_dict = cmudict.dict()

# Load and preprocess input poems sentences
with open('EdgarAllanPope_poem_inspiration.txt', 'r') as file:
    poems_inspiration = file.read().split('\n')


# Function to preprocess the poem_inspiration by removing punctuation and converting to lowercase
def preprocess_poem(poems):
    clean_inspiration = poems.translate(str.maketrans('', '', string.punctuation)).lower()
    return clean_inspiration


poems_inspiration = [preprocess_poem(poem) for poem in poems_inspiration]


# Build a Markov chain model based on inspiring sets
def build_markov_chain(poems):
    chain = {}
    for poem in poems:
        words = poem.split()
        for i in range(len(words) - 1):
            current_word = words[i]
            next_word = words[i + 1]
            if current_word in chain:
                chain[current_word].append(next_word)
            else:
                chain[current_word] = [next_word]
    return chain


markov_chain = build_markov_chain(poems_inspiration)


def find_rhymes(word):
    # Get the phonetic representation of the input word
    word = word.lower()
    rhyme_with = word[-3:]

    # Find words with the same phonetic ending
    rhymes = []
    for w, phonemes in pronouncing_dict.items():
        rhyme = w[-3:]
        if rhyme == rhyme_with:
            rhymes.append(w)
    return rhymes


def find_rhymes_pronounced(word):
    rhymes = pronouncing.rhymes(word)

    correct_rhymes = [rhyme for rhyme in rhymes if rhyme in pronouncing_dict.values()]
    return correct_rhymes


def get_most_common_pos_tag(word):
    tokens = nltk.word_tokenize(word)
    pos_tags = nltk.pos_tag(tokens)
    for elem in pos_tags:
        tag = elem[1]
        return tag


def choose_rhyme(rhymes, tag, index):
    if tag[:2] == 'NN':
        after_tag = 'VB'
    elif tag[:2] == 'VB':
        after_tag = 'JJ'
    elif tag[:2] == 'JJ':
        after_tag = 'NN'
    elif tag == 'PRP':
        after_tag = 'VB'
    elif tag == 'PRP$':
        after_tag = 'NN'
    elif tag == 'IN':
        after_tag = 'NN'
    elif tag == 'DT':
        after_tag = 'NN'
    else:
        after_tag = 'NN'
    for rhyme in rhymes:
        if get_most_common_pos_tag(rhyme) == after_tag:
            return rhyme
    if len(rhymes) > 1:
        return rhymes[index]
    else:
        return None


def generate_poem(chain, words_per_line, lines=4):
    poem = []

    # Array to store the rhymes for further processing
    used_rhymes = []
    index = 0

    for _ in range(lines):
        current_word = random.choice(list(chain.keys()))
        line = [current_word]

        for _ in range(words_per_line - 1):
            if current_word in chain:
                next_word = random.choice(chain[current_word])
                if next_word == 'i': next_word = 'I'
                line.append(next_word)
                current_word = next_word
            else:
                break

        if line:
            line[0] = line[0].capitalize()

        # A rhyme needs to be added only for even lines
        if len(poem) % 2 != 0:
            first_line = poem[len(poem) - 1]
            second_line = line
            lista = first_line.split(' ')
            last_word = lista[len(lista) - 1]
            if len(last_word) >= 3:
                rhymes = find_rhymes(last_word)
            else:
                rhymes = find_rhymes_pronounced(last_word)

            # Get second-last word of second line to set a speech tag for rhyme
            second_last = second_line[len(second_line) - 2]
            tag_second_last = get_most_common_pos_tag(second_last)
            rhyme = choose_rhyme(rhymes, tag_second_last, index)
            if rhyme in used_rhymes:
                index = index + 1
            if rhyme is not None:
                line.append(rhyme)

        poem.append(' '.join(line))

    return '\n'.join(poem)


def create_poems_book(poems_directory, num_poems):
    if not os.path.exists(poems_directory):
        os.makedirs(poems_directory)

    for i in range(num_poems):
        poem_content = generate_poem(markov_chain, 4, 8)
        print(poem_content)
        print()
        poem_filename = os.path.join(poems_directory, f'poem{i + 1}.txt')
        with open(poem_filename, 'w') as f:
            f.write(poem_content)


create_poems_book('poems_book', 3)
print("poems book successfully generated")
