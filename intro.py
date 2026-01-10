%pip install --upgrade tensorflow
%pip install --upgrade protobuf
import numpy as nnp
import pandas as pd
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppresses INFO and WARNING messages
import warnings
warnings.filterwarnings("ignore")
# Loop through all directories and filenames in the input folder
for dirname, _, filenames in os.walk('/kaggle/input'):
    # Print the first 10 filenames
    for i, filename in enumerate(filenames):
        if i >= 5:
            break
        print(os.path.join(dirname, filename))
