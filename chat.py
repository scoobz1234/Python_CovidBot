#  Copyright (c) 2020. Stephen R. Ouellette

import random  # utilized for random choice function near the bottom
import nltk  # Natural Language Processing Kit used for stemming and tokenization
import numpy  # Creating Arrays from lists and minor other things
import tflearn  # used for Neural Network / Deep Learning  / Model creation
import tensorflow  # base for tflearn and some others
import json  # reading our json intents file.

from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

# GLOBAL PARAMS
EPOCHS = 5  # How many epochs are we running?
THRESHOLD = 0.7  # How much does the bot have to meet for the prediction percentage (50% match at 0.5)

# The intents.json file is set up to have generalized input/output
# it uses Tags to mark categories, Patterns to mark valid input, and Responses to mark what the bot can say.
# you can have as little as 1 input and 1 output for a given tag, meaning you can have very specific responses
# or you can have very generalized responses.

# Open the json file with all our intents...
with open("intents.json") as file:
    data = json.load(file)

# VARIABLES #
WORDS = []  # This holds the words from the patterns
TAGS = []  # Stores all the tags
PATTERNS = []  # Stores all the words from patterns but tokenized
PATTERN_TAGS = []  # Stores tokenized version of teh tags.

# Iterate through the files contents, look into intent
for intent in data["intents"]:
    # iterate through the patterns
    for pattern in intent["patterns"]:
        tokenized_words = nltk.word_tokenize(pattern)  # Get all the words from the dictionary.
        WORDS.extend(tokenized_words)  # add the tokenized words to the WORDS array
        PATTERNS.append(tokenized_words)  # add all the patterns to the patterns array
        PATTERN_TAGS.append(intent["tag"])  # add all the tags to the tokenized tags array

    if intent["tag"] not in TAGS:
        TAGS.append(intent["tag"])

WORDS = [stemmer.stem(word.lower()) for word in WORDS if word != "?"]  # Stems the words
WORDS = sorted(list(set(WORDS)))  # removes duplicates

TAGS = sorted(TAGS)  # Sorts the tags

training = []  # store the training data
output = []  # store the output data

out_empty = [0 for _ in range(len(TAGS))]

# for each item in the patterns, we add it to the bag of words
# here we are using 1 or 0 to indicate if the word exists or not
# were not counting their occurrences.
for x, item in enumerate(PATTERNS):
    bag_of_words = []  # our bag of words

    stemmed_words = [stemmer.stem(word.lower()) for word in item]  # Stem each word, and make sure we put it lowercase

    for word in WORDS:
        # Check if the word in our words array is in the stemmed array, if it is set the element in the bag to 1
        # else set it to 0
        if word in stemmed_words:
            bag_of_words.append(1)
        else:
            bag_of_words.append(0)

    # Here we set the output row to the out empty array
    # : means everything in the array
    output_row = out_empty[:]
    # set the tag to 1 for each word
    output_row[TAGS.index(PATTERN_TAGS[x])] = 1
    # append the bag of words to the training array
    training.append(bag_of_words)
    output.append(output_row)

training = numpy.array(training)  # Convert the list to an array
output = numpy.array(output)  # change lists to array

# MODEL NN
# Building our Neural Network model...
tensorflow.reset_default_graph()  # Reset the data graph

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)  # hidden layer 8 neurons
net = tflearn.fully_connected(net, 8)  # second hidden layer of 8 neurons
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")  # Output layer shows probability 6 neurons
net = tflearn.regression(net)  # prediction (Regression)

model = tflearn.DNN(net)  # set the Deep Neural Network to the Model.

# Pass training data to model
model.fit(training, output, n_epoch=EPOCHS, batch_size=8, show_metric=True)
model.save("model.covid")  # saves the model.


# Bag of words function to generate words from user input
# we take the users input and create a bag of words from it.
def bag_of_words(sentence_input, input_bag_of_words):
    bag = [0 for _ in range(len(input_bag_of_words))]  # set the bag up and create a zero at each position

    # Tokenize the sentences words so we can stem and add them to the bag
    tokenized_sentence_words = nltk.word_tokenize(sentence_input)
    # stem the words (make sure their lowercase as well)
    tokenized_sentence_words = [stemmer.stem(word.lower()) for word in tokenized_sentence_words]

    # Now for each sentence in the tokenized sentences we enumerate through the bag and set each
    # position to 1
    for sentence in tokenized_sentence_words:
        for i, word in enumerate(input_bag_of_words):
            if word == sentence:
                bag[i] = 1
    # Return the bag.
    return numpy.array(bag)
