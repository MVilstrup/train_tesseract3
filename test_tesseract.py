import os
import cv2
import cv2.cv as cv
import argparse
import edit_distance

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", required=True, help="Path to the directory containing the images")
ap.add_argument("-o", "--output", required=True, help="Name of the output file is required")
ap.add_argument("-l", "--language", required=True, help="The language used to read the file")
args = vars(ap.parse_args())

images = {}

for (dirpath, _, filenames) in os.walk(args["directory"]):

    for file in filenames:
        new_name, extension = os.path.splitext(file)
        if extension in [".tiff", ".TIFF"]:
            name = new_name
            path = "%s%s" % (dirpath, file)
            images[name] = path

    break

new_path = "%sextracted_text/" % args["directory"]
if not os.path.exists(new_path):
    os.makedirs(new_path)

def test_output(correct_answer, output_result):
    correct = open(correct_answer, 'r')
    try:
        output = open(output_result, 'r')
    except:
        print "No output generated"
        return 0
    source = ""
    target = ""
    for line in correct:
        source += line 

    for line in output:
        target += line

    source_len = len(source)
    distance = edit_distance.levenshtein(source, target)
    percentage = (float(distance) / float(source_len)) * 100.0

    return 100.0 - percentage


def read_receipt(image_name, image_path):
    image_folder = os.path.dirname(image_path)
    name, _ = os.path.splitext(image_name)
    correct_answer = "%s/%s.txt" % (image_folder, name)
    output = "%s/%s-tess-result" % (image_folder, name)
    os.system("tesseract %s %s -l %s" % (image_path, output, args["language"]))
    output = "%s.txt" % output
    
    write_to_csv(name, test_output(correct_answer, output))


def write_to_csv(name, result):
    csv_name = "%s%s.csv" % (args["directory"], args["output"])
    csv = open(csv_name, "a")
    csv.write("%s,%s\n" % (name, result)) 

output = "%s%s.csv" % (args["directory"], args["output"]) 
if os.path.exists(output):
    os.remove(output)

for image_name, image_path in images.iteritems():
    read_receipt(image_name, image_path)
