import numpy as np
import pandas as pd
import os
from sklearn.tree import DecisionTreeClassifier, plot_tree

def make_prediction(wr1, wr2):
  #test_df = pd.read_csv("./test.csv")
  #test_df = test_df[test_df.error != 1] #removes fights where there was an error
  train_df = pd.read_csv("./train.csv")
  train_df = train_df[train_df.error != 1]
  features = ["winrate1", "winrate2"]
  y = train_df["outcome"]
  x = pd.get_dummies(train_df[features])
  decision_tree = DecisionTreeClassifier()
  decision_tree = decision_tree.fit(x, y) #model

  #x_test = pd.get_dummies(test_df[features])
  prediction_df = pd.DataFrame({"winrate1": [wr1], "winrate2": [wr2]})
  prediction_df = pd.get_dummies(prediction_df)
  predictions = decision_tree.predict(prediction_df)
  #submission_df = pd.DataFrame({"WR1": test_df["winrate1"], "WR2": test_df["winrate2"], "Outcome": predictions})
  #submission_df.to_csv("submission.csv", index=False)
  return predictions[0] #returns 0 if fighter 1, 1 if fighter 2