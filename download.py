import shutil
import os
from datetime import datetime
from IPython.display import FileLink

# 1. Define paths and get current date
# We target the specific output folder to keep the zip clean
filename = '' #enter a hint of you work Mammqa for example
folder_to_zip = '/kaggle/working/' 
current_date = datetime.now().strftime("%Y-%m-%d_%H-%M")
output_filename = f'{filename}_results_{current_date}'

# 2. Create the zip archive
# This creates /kaggle/working/mammqa_results_YYYY-MM-DD_HH-MM.zip
try:
    shutil.make_archive(f"/kaggle/working/{output_filename}", 'zip', folder_to_zip)
    print(f"✅ Folder zipped successfully as {output_filename}.zip")
except Exception as e:
    print(f"❌ Error zipping folder: {e}")

# 3. Generate a direct download link
FileLink(f'{output_filename}.zip')
