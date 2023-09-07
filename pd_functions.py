import pandas as pd
import numpy as np
import glob

# generate a 1000 row pandas series in python
s = pd.Series(np.random.randn(1000))

# generate a mask of values between 0 and 0.25
#mask = (s > 0) & (s < 0.25)
#print([mask][0:10])
#print(s)

files = glob.glob("_data/*.csv")

pd = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)


print(pd.head())



