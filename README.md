# train_tesseract3
Helper functions to train tesseract 3 and test the result of the training

## Requirements
This repository is tested in Ubuntu 14.10, and might not work in earlier version
of Ubuntu since extract\_unicharset are not installed properly in earlier
versions. 

## Structure
The main part of this repository is the TrainTesseract class which contains all
the methods needed to train tesseract3. To see an example of how to use the
class, look in create_tess_trainingdata.py. 

The file folder contains example files of the files you might want to include in
your training folder, before starting the training:

* words_list = a list of words in the language you are trying to train (example
  file is a list of danish words)
* frequent_words_list = a list of the most frequent words you are trying to
  train (example file is a list of common words in a project of mine)
* font_properties = the properties of the fonts you are trying to train
