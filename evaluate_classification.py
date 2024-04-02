from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_fscore_support
import pandas as pd

"""
Establish dataset
"""
'''load data'''
labelled_data = pd.read_csv("others/Confusion_Table.csv")
# https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment
# Labels >>>>> |  0 = Negative  |  1 = Neutral  |  2 = Positive  |
print(labelled_data)

y_true = list(labelled_data['Human'])
y_pred = list(labelled_data["AI"])

'''Compute'''
print("\nConfusion Matrix summary:")
print("Number of comments:", len(labelled_data))
print("\nConfusion Table --- Labels: 0, 1, 2  |  Rows = Human (i.e. True)  |  Columns = AI (i.e. Predicted)")

print(confusion_matrix(y_true, y_pred))
print("\n(Precision, Recall, F1 Score)")
print(precision_recall_fscore_support(y_true, y_pred, average='macro')[0:3])

# Precision = Number of true entries divided by all entries in that column, followed by average of all columns
# Recall = Number of true entries divided by all entries in that row, followed by average of all rows

# average ='binary': Only report results for the class specified by pos_label. This is applicable only if targets (y_{true,pred}) are binary.
# average = 'micro': Calculate metrics globally by counting the total true positives, false negatives and false positives.
# average = 'macro': Calculate metrics for each label, and find their unweighted mean. This does not take label imbalance into account.
# average ='weighted': Calculate metrics for each label, and find their average weighted by support (the number of true instances for each label). This alters ‘macro’ to account for label imbalance; it can result in an F-score that is not between precision and recall.

# How might we adjust the prediction to meet required metrics (e.g. precision) without retraining the mmodel?