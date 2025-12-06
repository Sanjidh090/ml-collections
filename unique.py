import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

df_any = pd.read_csv('/kaggle/input/anything.csv')
df = df_any
for i in df.columns:
    print(f"="*100)
    print(f" Unique values {df[i].value_counts()}")
print(f"=="*50)
print(f" Unique Value report {df.nunique()}")

df.hist(figsize=(16, 16), bins=30)
plt.tight_layout()
plt.show()
