import pandas as pd
import sys

# Read the file
dat = pd.read_csv(sys.argv[1])

# Remove all the columns not necessary for release
dat = dat.drop(['Cognitive Bias Triggered', 'Source'], axis=1)

# Save to the same file
dat.to_csv(sys.argv[1], index=False)
