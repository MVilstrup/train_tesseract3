import os
import argparse
from TesseractTrainer import TesseractTrainer
# Create the argpaser to enforce the right parameters
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", required=True, help="Path to the directory containing the images")
ap.add_argument("-l", "--language", required=True, help="The language used to read the file")
args = vars(ap.parse_args())

trainer = TesseractTrainer(args["directory"], args["language"])
trainer.generate_training_files(remove_output=True)
trainer.extract_unicharset(remove_output=True)
trainer.run_mftraining(remove_output=True)
trainer.run_cntraining(remove_output=True)
trainer.combine_tessdata(output_dir="/usr/share/tesseract-ocr/tessdata")
