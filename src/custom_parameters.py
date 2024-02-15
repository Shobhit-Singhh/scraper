import logging
import yaml
from nltk.tokenize import sent_tokenize
import syllables
from preprocessing import preprocess
from utility_functions import load_config, load_dictionary
from sentiment_scores import sentiment_scores


def calculate_metrics(text, config_path="config.yaml"):
    '''
    Calculate custom parameters for a given text.
    Parameters:
    - text (str): Text to calculate custom parameters for.
    - config_path (str): Path of config.yaml file
    Returns:
    - dict: A dictionary containing the custom parameters.
    '''
    
    # Load configuration
    logging.info("Loading configuration...")
    config = load_config(config_path)
    logging.info("Config loaded successfully")

    # Sentiment dictionaries paths from configuration
    positive_dict_path = config["dictionary"]["positive_dictionary_path"]
    negative_dict_path = config["dictionary"]["negative_dictionary_path"]

    sentences = sent_tokenize(text)

    total_words = 0
    total_complex_words = 0
    total_syllables = 0
    positive_score = 0
    negative_score = 0
    personal_pronouns = 0
    char_count = 0
    
    for sentence in sentences:
        words, pos_tags, pronoun_count = preprocess(sentence, "config.yaml")
        pos_score, neg_score = sentiment_scores(words, "config.yaml")
        char_count += sum(len(word) for word in words)

        total_words += len(words)
        personal_pronouns += pronoun_count
        positive_score += pos_score
        negative_score -= neg_score

        for word in words:
            total_syllables += syllables.estimate(word)
            if syllables.estimate(word) >= 2:
                total_complex_words += 1

    # calculate custom parameters
    avg_sentence_length = total_words / len(sentences)
    percentage_complex_words = (total_complex_words / total_words) * 100
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)
    logging.info("Calculations stage 1 completed successfully")

    # Sentiment Analysis
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (total_words + 0.000001)
    logging.info("Calculations stage 2 completed successfully")

    # Word and Syllable Count
    
    avg_word_length = char_count / total_words
    
    return {
        "POSITIVE SCORE": positive_score,
        "NEGATIVE SCORE": negative_score,
        "POLARITY SCORE": polarity_score,
        "SUBJECTIVITY SCORE": subjectivity_score,
        "AVG SENTENCE LENGTH": avg_sentence_length,
        "PERCENTAGE OF COMPLEX WORDS": percentage_complex_words,
        "FOG INDEX": fog_index,
        "AVG NUMBER OF WORDS PER SENTENCE": avg_sentence_length,
        "COMPLEX WORD COUNT": total_complex_words,
        "WORD COUNT": total_words,
        "SYLLABLE PER WORD": total_syllables / total_words,
        "PERSONAL PRONOUNS": personal_pronouns,
        "AVG WORD LENGTH": avg_word_length
    }