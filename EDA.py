"""
Remember to install packages before starting!
pip install deep_translator
pip install wordcloud
pip install accelerate
"""

import pandas as pd
from deep_translator import GoogleTranslator
import nltk
from nltk.corpus import stopwords
from collections import Counter
from nltk.util import everygrams
import matplotlib.pyplot as plt
from matplotlib import style
from wordcloud import WordCloud, STOPWORDS
import csv

"""
Establish dataset
"""
search_terms = pd.read_pickle("support/_current_/searchTerms.pkl")
comment_list = pd.read_pickle("support/%s/comment_list.pkl" % search_terms)

print("Search terms:", search_terms)
print("Number of comments:", len(comment_list))

"""
** Translate to english
"""
# for i in range(15):                       # translate the first 15 comments
for i in range(len(comment_list)):        # translate all
    try:
        print(i, comment_list[i])
        comment_list[i] = GoogleTranslator(source='auto', target='en').translate(str(comment_list[i]))
        print(i, comment_list[i])
    except:
        print("Exceeded 5000 characters.")

"""
Preprocessing
"""
import re

def clean_text(text):                               # user defined function for cleaning text
    if text is None:
        return ("")
    else:
      text = text.lower()                             # all lower case
      text = re.sub(r'\[.*?\]', ' ', text)            # remove text within [ ] (' ' instead of '')
      text = re.sub(r'\<.*?\>', ' ', text)            # remove text within < > (' ' instead of '')
      text = re.sub(r'http\S+', ' ', text)            # remove website ref http
      text = re.sub(r'www\S+', ' ', text)             # remove website ref www

      text = text.replace('€', 'euros')               # replace special character with words
      text = text.replace('£', 'gbp')                 # replace special character with words
      text = text.replace('$', 'dollar')              # replace special character with words
      text = text.replace('%', 'percent')             # replace special character with words
      text = text.replace('\n', ' ')                  # remove \n in text that has it

      text = text.replace('\'', '’')                  # standardise apostrophe
      text = text.replace('&#39;', '’')               # standardise apostrophe

      text = text.replace('’d', ' would')             # remove ’ (for would, should? could? had + PP?)
      text = text.replace('’s', ' is')                # remove ’ (for is, John's + N?)
      text = text.replace('’re', ' are')              # remove ’ (for are)
      text = text.replace('’ll', ' will')             # remove ’ (for will)
      text = text.replace('’ve', ' have')             # remove ’ (for have)
      text = text.replace('’m', ' am')                # remove ’ (for am)
      text = text.replace('can’t', 'can not')         # remove ’ (for can't)
      text = text.replace('won’t', 'will not')        # remove ’ (for won't)
      text = text.replace('n’t', ' not')              # remove ’ (for don't, doesn't)

      text = text.replace('’', ' ')                   # remove apostrophe (in general)
      text = text.replace('&quot;', ' ')              # remove quotation sign (in general)

      text = text.replace('cant', 'can not')          # typo 'can't' (note that cant is a proper word)
      text = text.replace('dont', 'do not')           # typo 'don't'

      text = re.sub(r'[^a-zA-Z0-9]', r' ', text)      # only alphanumeric left
      text = text.replace("   ", ' ')                 # remove triple empty space
      text = text.replace("  ", ' ')                  # remove double empty space
      return text

for i in range(len(comment_list)):
    print(comment_list[i])                          # pre-clean
    comment_list[i] = clean_text(comment_list[i])   # overwrite with clean_text function
    print(comment_list[i])                          # post-clean


"""
Join all comments into a corpus
"""
def combine_text(list_of_text):                     # define combine_text to take (list_of_text)
    combined_text = ' '.join(list_of_text)          # do this
    return combined_text                            # and give combined_text back

all_comments = combine_text(comment_list)

print(all_comments)

"""
Load stopwords
"""
nltk.download('stopwords')
stopwords = stopwords.words('english')      # set as English
# Show stopwords
print(stopwords)
# Remove stopwords
all_comments = " ".join(word for word in all_comments.split() if word not in stopwords)
print(all_comments)

"""
Find top words
"""
print("Finding top words...")

top_length = 3                # top_length > 1 not useful after removing stopwords
num_top = 30

e_grams_counts = Counter(everygrams(all_comments.split(), max_len=top_length))
e_grams_most = e_grams_counts.most_common(num_top)
print(e_grams_most)
top_word = e_grams_most[0][0][0]
print("Top Word:", top_word)
top_word_count = e_grams_most[0][1]
print("Top Word Count:", top_word_count)
print("Number of e-grams found:", len(e_grams_most))

##### ------------------------------------------------------------------------------------------------------------------------------------------ #####

"""
Plot data #Comment out if not needed.
"""
style.use("ggplot")

print("Plotting graph...")

x = []
y = []

for i in range(len(e_grams_most)):
    x.append(e_grams_most[i][0][0])       # assume 1 word
    y.append(e_grams_most[i][1])

fig = plt.figure(figsize=(8, 6))
plt.bar(x, y, color='r')
plt.title('Top Words Found')
plt.ylabel('Number of times')
plt.xlabel('Words')
plt.xticks(rotation=70, fontsize=8)
plt.savefig("support/%s/data_words.png" % search_terms)
plt.show()

##### ------------------------------------------------------------------------------------------------------------------------------------------ #####

"""
Generate WordCloud #Comment out if not needed.
"""
STOPWORDS.update(stopwords)
print("Creating WordCloud...")

wc = WordCloud(stopwords=STOPWORDS, background_color="white", colormap="Dark2", collocations=False,
               max_font_size=150, include_numbers=True, random_state=42, max_words=50)

wc.generate(all_comments)

plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.title("%s" % search_terms, fontsize=15)
plt.savefig("support/%s/WordCloud.png" % search_terms)
plt.show()

##### ------------------------------------------------------------------------------------------------------------------------------------------ #####

"""
Classify comments by topic #Comment out if not needed. #Replace the candidates to suit your needs. #Pick 1 of the 2 models.
## Comments with emojis are outputted as NoneType in csv to prevent ValueError: You must include at least one label and at least one sequence.
"""
from transformers import pipeline

candidates = ["product", "shipping", "staff"]                   # replace the candidates to suit your needs

candidate_counts = {candidate: 0 for candidate in candidates}   # Initialize counters

model = "facebook/bart-large-mnli"                              # default model
# model = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"

# Open CSV file for writing
with open("classified_comments.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Sequence", "Label"])  # Header row

    classifier = pipeline("zero-shot-classification", model=model)
    
    labeled_comments_count = 0  # Initialize counter for labeled comments
    
    # Write results to CSV for each comment
    for comment in comment_list:
        # Classify comment only if it's not empty
        if comment.strip():
            result = classifier(comment, candidate_labels=candidates)
            sequence = result['sequence'] if result['labels'] else None
            label = result['labels'][0] if result['labels'] else None
            
            writer.writerow([sequence, label])

            # Update candidate counters and labeled comments count
            if label:
                candidate_counts[label] += 1
                labeled_comments_count += 1
        else:
            writer.writerow([None, None])

# Calculate the number of empty comments
empty_comments_count = len(comment_list) - labeled_comments_count

# Print summary
print("Candidate Counts:")
for candidate, count in candidate_counts.items():
    print(f"{candidate}: {count}")
print(f"Empty Comments: {empty_comments_count}")
print("Detailed results written to classified_comments.csv.")

##### ------------------------------------------------------------------------------------------------------------------------------------------ #####

"""
Sentiment Analysis #Comment out if not needed. #Pick 1 of the 2 models.
## Comments are truncated to 512 characters due to model limitations.
"""
from transformers import pipeline
from transformers import AutoTokenizer

# Define the maximum sequence length
max_seq_length = 512  # Adjust Truncated Length

# model = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"      # default model, binary sentiment
model = "cardiffnlp/twitter-roberta-base-sentiment"                       # negative, neutral, positive

# Initialise the tokenizer
tokenizer = AutoTokenizer.from_pretrained(model, use_fast=True)

# Filter out or truncate excessively long sequences
filtered_comments = [comment[:max_seq_length - 2] for comment in comment_list]  # -2 to account for special tokens [CLS] and [SEP]

# Initialise the pipeline with padding
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, padding=True, device_map="auto")

results = classifier(filtered_comments)

# Initialise a list to store the rows of data
csv_data = []

# Accumulate sentiment counts
print("Conducting Sentiment Analysis...")
positive_count = 0
negative_count = 0
neutral_count = 0
empty_comments_count = 0
for i in range(len(results)):
    result = results[i]
    sentiment = result['label']
    if comment_list[i].strip():  # Check if the comment is not empty
        csv_data.append([comment_list[i], sentiment])
        print(comment_list[i])
        print(result)
        print(sentiment)
        print("\n")

        if sentiment == "LABEL_2":
            positive_count += 1
        elif sentiment == "POSITIVE":
            positive_count += 1
        elif sentiment == "LABEL_0":
            negative_count += 1
        elif sentiment == "NEGATIVE":
            negative_count += 1
        elif sentiment == "LABEL_1":
            neutral_count += 1
    else:  # If the comment is empty, append it to CSV with empty sentiment
        empty_comments_count += 1
        csv_data.append([comment_list[i], ''])

# Calculate overall sentiment
overall_sentiment = "Positive" if positive_count > negative_count else "Negative" if negative_count > positive_count else "Neutral"

# Initialise counters for positive and negative sentiments
positive_count_top_word = 0
negative_count_top_word = 0
neutral_count_top_word = 0

# Accumulate sentiment counts for comments containing the top word
for comment, result in zip(filtered_comments, results):
    if top_word in comment.lower():  # Check if the top word is mentioned in the comment
        sentiment = result['label']  # Access sentiment label directly
        if sentiment == "LABEL_2":
            positive_count_top_word += 1
        elif sentiment == "POSITIVE":
            positive_count_top_word += 1
        elif sentiment == "LABEL_0":
            negative_count_top_word += 1
        elif sentiment == "NEGATIVE":
            negative_count_top_word += 1
        elif sentiment == "LABEL_1":
            neutral_count_top_word += 1

# Calculate overall sentiment when the top word is mentioned
overall_sentiment_top_word = "Positive" if positive_count_top_word > negative_count_top_word else "Negative" if negative_count_top_word > positive_count_top_word else "Neutral"

# Output CSV
with open("sentiment_analysis_results.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Comment", "Sentiment"])
    writer.writerows(csv_data)

# Print summary
print("Search terms:", search_terms)
print("Number of comments:", len(comment_list))
print("Top Word:", top_word)
print("Number of empty comments:", empty_comments_count)
print("\n")
print("Number of comments with Positive sentiment:", positive_count)
print("Number of comments with Negative sentiment:", negative_count)
print("Number of comments with Neutral sentiment:", neutral_count)
print("Overall Sentiment:", overall_sentiment)
print("\n")
print("Number of comments with the word", top_word, ":", top_word_count)
print("Number of comments when", top_word, "mentioned with Positive sentiment:", positive_count_top_word)
print("Number of comments when", top_word, "mentioned with Negative sentiment:", negative_count_top_word)
print("Number of comments when", top_word, "mentioned with Neutral sentiment:", neutral_count_top_word)
print("Overall Sentiment when", top_word, "mentioned:", overall_sentiment_top_word)
print("\n")
print("Detailed results written to sentiment_analysis_results.csv.")





