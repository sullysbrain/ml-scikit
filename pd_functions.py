import pandas as pd
import numpy as np

# generate a 1000 row pandas series in python
s = pd.Series(np.random.randn(1000))

# generate a mask of values between 0 and 0.25
#mask = (s > 0) & (s < 0.25)
#print([mask][0:10])
#print(s)

train_pd = pd.read_csv("_data/train.csv")

print(train_pd.head())



