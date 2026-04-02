import spacy

try:
    nlp = spacy.load("en_core_web_sm")
    NLP_AVAILABLE = True
except:
    print("Warning: spaCy model not available. Location extraction will be limited.")
    NLP_AVAILABLE = False
    nlp = None