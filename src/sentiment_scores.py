import yaml
from utility_functions import load_config, load_dictionary

def sentiment_scores(word_list, config_path="config.yaml"):
    '''
    Calculate sentiment scores for a list of words.
    Parameters:
    - word_list (list): List of words.
    - config_path (str): Path of config.yaml file
    Returns:
    - tuple: A tuple containing the positive and negative sentiment scores.
    '''
    
    # Load configuration parameters
    config = load_config(config_path)
    positive_dictionary_path = config["dictionary"]["positive_dictionary_path"]
    negative_dictionary_path = config["dictionary"]["negative_dictionary_path"]

    # Load positive and negative dictionaries
    positive_dictionary = load_dictionary(positive_dictionary_path,"config.yaml")
    negative_dictionary = load_dictionary(negative_dictionary_path,"config.yaml")

    # Initialize scores
    positive_score = 0
    negative_score = 0

    # Calculate scores
    for word in word_list:
        if word in positive_dictionary:
            positive_score += 1
        if word in negative_dictionary:
            negative_score += 1

    # Return sentiment scores
    return positive_score, -negative_score

