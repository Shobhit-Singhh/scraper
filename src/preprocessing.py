import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from utility_functions import load_config
import spacy
import nltk
import yaml

# Replace '/Users/shobhitsingh/nltk_data' with your actual NLTK data path
nltk_data_path = '/Users/shobhitsingh/nltk_data'

# Append the specified directory to the NLTK data path
nltk.data.path.append(nltk_data_path)

# Now, you can download specific NLTK resources or use them without downloading
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# Load spaCy model
spacy_model_name = 'en_core_web_sm'
try:
    # Try loading spaCy model
    nlp = spacy.load(spacy_model_name)
except IOError:
    # If model not found, download it
    spacy.cli.download(spacy_model_name)
    nlp = spacy.load(spacy_model_name)


def preprocess(text, config_path):
    """
    Preprocesses the input text based on the specified configuration.

    Parameters:
    - text (str): The input text to be preprocessed.
    - config_path (str): The path to the configuration file.

    Returns:
    - tuple: A tuple containing the preprocessed words, POS tags, and personal pronoun count.
    """
    config = load_config(config_path)
    custom_stopword_folder = config["dictionary"]["custom_stopword_folder"]

    # Step 0: count "US"
    US_count = text.count("US")
    
    # Step 1: Text Cleaning
    text = text.lower()
    text = ''.join([char for char in text if char.isalnum() or char.isspace()])

    # Step 2: Tokenization
    words = word_tokenize(text)

    # Step 3: Count Personal Pronouns
    personal_pronouns = ["i", "you", "he", "she", "it", "we", "they", "them", "us", "him", "her", "his", "hers", "its", "theirs", "our", "your"]
    personal_pronoun_count = sum(1 for word in words if word in personal_pronouns)

    # Step 4: Stopword Removal
    stop_words = set(stopwords.words('english'))
    if custom_stopword_folder:
        for filename in os.listdir(custom_stopword_folder):
            file_path = os.path.join(custom_stopword_folder, filename)
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    custom_stopwords = file.read().splitlines()
                    stop_words.update(custom_stopwords)
            except FileNotFoundError as e:
                print(f"File not found: {file_path}")
                raise e
            except Exception as e:
                print(f"An error occurred while reading the file: {e}")
                raise e

    words = [word for word in words if word not in stop_words]

    # Step 5: Lemmatization
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]

    # Step 6: Part-of-Speech (POS) Tagging using spaCy
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(' '.join(words))
    pos_tags = [(token.text, token.pos_) for token in doc]
    
    return words, pos_tags, personal_pronoun_count-US_count
