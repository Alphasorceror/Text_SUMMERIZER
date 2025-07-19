import logging
import re
from string import punctuation
from heapq import nlargest
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define stopwords manually to avoid NLTK dependency
ENGLISH_STOPWORDS = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"}

# Hindi stopwords list
HINDI_STOPWORDS = {'के', 'का', 'एक', 'में', 'की', 'है', 'यह', 'और', 'से', 'हैं', 'को', 'पर', 'इस', 'होता', 'कि', 'जो', 'कर', 'मे', 'गया', 'करने', 'किया', 'लिये', 'अपने', 'ने', 'बनी', 'नहीं', 'तो', 'ही', 'या', 'हो', 'था', 'तक', 'साथ', 'हुआ', 'थे', 'थी', 'होती', 'अपनी', 'उनके', 'थी', 'वह', 'वे', 'होने', 'बाद', 'लिए', 'कुछ', 'जब', 'हम', 'थे', 'कभी', 'होते', 'हुई', 'जा', 'ना', 'इसके', 'धर', 'उस', 'दो', 'वाले', 'न', 'उनकी', 'तुम', 'मैं', 'ये', 'जिस', 'तरह', 'रहा', 'उन', 'रहे', 'आप', 'भी', 'वो', 'हमारे', 'सकते', 'नए', 'सभी', 'कौन', 'चाहिए', 'सकता', 'रखें', 'अपना', 'सके', 'आज', 'बहुत', 'वर्ष', 'दिया', 'तीन', 'वहाँ', 'गए', 'होता', 'द्वारा', 'हुए', 'अब', 'कई', 'जाता', 'तथा', 'बताया', 'आदि', 'कहा', 'जाती', 'सबसे', 'हुए', 'उनका', 'उसके', 'प्रति', 'दिन', 'सभी', 'मैंने', 'काम', 'क्योंकि', 'कम', 'हो', 'दौरान', 'इन', 'होना', 'वाली', 'पहले', 'महिला', 'तौर', 'उसे', 'हमें', 'जिसके', 'पास', 'अपने', 'समय', 'कहते', 'नाम', 'अभी', 'इसे', 'जाने', 'विशेष', 'खुद', 'यही', 'आज', 'लेकिन', 'अगर', 'तेरा', 'जाएगा', 'पांच', 'उसकी', 'गये', 'वहीं', 'दी', 'जीवन', 'कर', 'लेकर', 'दे', 'क्या', 'हमने', 'हाँ', 'इतना', 'जिससे', 'वाला', 'साल'}

def detect_language(text):
    """
    Detect the language of the text.
    Currently supports English and Hindi.
    
    Args:
        text (str): The text to detect language for
        
    Returns:
        str: Detected language ('english' or 'hindi')
    """
    # Simple detection based on script
    hindi_pattern = re.compile(r'[\u0900-\u097F]')
    hindi_chars = hindi_pattern.findall(text)
    
    # If text contains Hindi characters, classify as Hindi
    if len(hindi_chars) > len(text) * 0.3:  # If more than 30% characters are Hindi
        return 'hindi'
    else:
        return 'english'

def split_into_sentences(text, language='english'):
    """
    Split text into sentences using regex for better performance.
    
    Args:
        text (str): The text to split into sentences
        language (str): The language of the text ('english' or 'hindi')
        
    Returns:
        list: List of sentences
    """
    # Common sentence patterns
    if language == 'english':
        # This pattern will split text into sentences based on periods, question marks, and exclamation points
        # followed by a space or the end of the string
        sentence_enders = r'[.!?][\s]{1,2}|[.!?]$'
    elif language == 'hindi':
        # Hindi uses the same punctuation marks as English for sentence endings
        # But we'll add Devanagari-specific punctuation like । (danda) and ॥ (double danda)
        sentence_enders = r'[.!?।॥][\s]{1,2}|[.!?।॥]$'
    else:
        # Default to English if language not supported
        sentence_enders = r'[.!?][\s]{1,2}|[.!?]$'
    
    sentences = re.split(sentence_enders, text)
    # Remove empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def tokenize_text(text, language='english'):
    """
    Tokenize text into words using regex for better performance.
    
    Args:
        text (str): The text to tokenize
        language (str): The language of the text ('english' or 'hindi')
        
    Returns:
        list: List of tokens
    """
    if language == 'english':
        # English tokenization - alphanumeric with apostrophes
        return re.findall(r'\b[a-zA-Z0-9\']+\b', text.lower())
    elif language == 'hindi':
        # Hindi tokenization - handle Hindi Unicode range
        # \u0900-\u097F is the Unicode range for Devanagari script (used for Hindi)
        return re.findall(r'[\u0900-\u097F]+', text.lower())
    else:
        # Default to English if language not supported
        return re.findall(r'\b[a-zA-Z0-9\']+\b', text.lower())

def calculate_word_frequencies(text, language='english'):
    """
    Calculate word frequencies in the text.
    
    Args:
        text (str): The text to analyze
        language (str): The language of the text ('english' or 'hindi')
        
    Returns:
        Counter: A Counter object with word frequencies
    """
    # Get appropriate stopwords
    stopwords = ENGLISH_STOPWORDS if language == 'english' else HINDI_STOPWORDS
    
    # Tokenize the text
    words = tokenize_text(text, language)
    
    # Remove stopwords and punctuation
    words = [word for word in words if word not in stopwords and word not in punctuation]
    
    # Count word frequencies
    word_frequencies = Counter(words)
    
    # Normalize frequencies
    max_frequency = max(word_frequencies.values()) if word_frequencies else 1
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_frequency
    
    return word_frequencies

def summarize_text(text, ratio=0.3, language='english'):
    """
    Summarize text by extracting the most important sentences.
    
    Args:
        text (str): The text to summarize
        ratio (float): The ratio of sentences to include in the summary (0.0 to 1.0)
        language (str): The language of the text ('english' or 'hindi')
        
    Returns:
        str: The summarized text
    """
    # Handle empty or very short text
    if not text or len(text) < 10:
        return text
    
    # Split text into sentences
    sentences = split_into_sentences(text, language)
    
    # If there's only one sentence, return it
    if len(sentences) <= 1:
        return text
    
    # Calculate word frequencies
    word_frequencies = calculate_word_frequencies(text, language)
    
    # Calculate sentence scores based on word frequencies
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        for word in tokenize_text(sentence, language):
            if word in word_frequencies:
                if i not in sentence_scores:
                    sentence_scores[i] = 0
                sentence_scores[i] += word_frequencies[word]
    
    # Determine number of sentences for the summary
    summary_sentences = max(1, int(len(sentences) * ratio))
    
    try:
        if not sentence_scores:
            logger.warning("Sentence scores are empty. Falling back to the first few sentences.")
            summary = ' '.join(sentences[:summary_sentences])
        else:
            summary_indices = nlargest(summary_sentences, sentence_scores, key=lambda i: sentence_scores.get(i, 0))
            summary_indices.sort()  # Sort indices to maintain original order
            summary = ' '.join([sentences[i] for i in summary_indices])
    except Exception as e:
        logger.error(f"Error selecting summary sentences: {str(e)}. Falling back to the first few sentences.")
        summary = ' '.join(sentences[:summary_sentences])
    
    return summary