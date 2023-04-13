# WnD: Faster App Screen Search via Word + Doodle

# Index all texts in Elasticsearch
1. Extract the [curatedtexts](TextExtraction/curatedtexts) zip file located in the TextExtraction folder.
2. Install Elasticsearch.
3. Run the [ElasticWriter.py](TextExtraction/Synonym.txt) and change the data_folder in the script accordingly. 
4. Place the [Synonym.txt](TextExtraction/Synonym.txt) file into the config folder of your Elasticsearch installation.

# Downloads
1. Download the [dictionary file](https://drive.google.com/file/d/1LoZbn8y5_xSeBbvipsd--7IqwuSvJQL4/edit) and put it in the similarUI folder 
2. Download the [dictionary file](https://drive.google.com/file/d/1WtiIYpwYWNSSEQk7iLHhK7lJdkmNOcu9) and put it in the DragAndDrop folder



# Dependencies-
1. Flask
2. Tensorflow 1.15
3. Python 3.6
4. Elasticsearch

# Create Virtual environment with Anaconda-
conda create -n yourenvname python=3.6 anaconda

# Install all dependencies
pip install -r requirements.txt

# Run Search-By-Sketch
Run app.py script

# For accessing the tool
http://127.0.0.1:5000/WnD
