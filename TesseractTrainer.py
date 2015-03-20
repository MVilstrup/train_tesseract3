import os
import argparse

class TesseractTrainer(object):

    def __init__(self, train_dir, language):
        # Initialize all the variables needed
        self.train_dir = train_dir
        self.images = {}
        self.box_files = {}
        self.training_files = {}
        self.language = language
        
        for (dirpath, _, filenames) in os.walk(train_dir):
            for full_name in filenames:
                name, extension = os.path.splitext(full_name)
                if extension in [".tiff", ".tif", ".TIFF"]:
                    lang_descriptor = name.split(".")[0]
                    if lang_descriptor != language:
                        message = "There is a problem with file: %s" % name
                        message += "\n Please make sure all files are in the"
                        message += " format [lang].[font].exp[number]"
                        message += " and check %s is the only language" % language
                        raise ValueError(message)
                    else:
                        self.images[name] = full_name

    def update_os_directory(self):
        """
        This method is used to be able to work directly in the training
        directory no matter what order the methods are called
        """
        try:
            os.chdir(self.train_dir)
        except OSError:
            pass

    def generate_box_files(self, remove_output=False):
        """
        Create a box file for each image in the training folder
        """
        self._update_os_directory()
        for name, path in self.images.iteritems():
            command = "tesseract %s %s batch.nochop makebox" % (path, name)
            if remove_output:
                print "Creating box file for image: %s " % name
                command += "  >/dev/null 2>&1"
            os.system(command)

    def _check_boxes_exists(self):
        """
        Check to see if there is one box for each image
        if this is the case, the references to both the images and boxes 
        are put into self.images and self.boxes
        """
        # Gather all the training images in the folder
        # These images should all be in uncompressed tif format
        for (dirpath, _, filenames) in os.walk(os.getcwd()):
    
            for full_name in filenames:
                name, extension = os.path.splitext(full_name)
                if extension == ".box":
                   self.box_files[name] = full_name

        # Check that there is a corresponding box file for each image
        # If this is not the case, the program halts, and demands that the user
        # provides the missing box files
        for name in self.images.keys():
            if not self.box_files.has_key(name):
                raise NotImplementedError("There needs to be a box file for each training image.. Please provide box file for image: %s" % name)

    def _check_font_properties(self):
        # Make sure the user has the font property file which is mandatory
        if not os.path.exists("font_properties"):
            raise ValueError("You need to create a font_properties file")
        
    def generate_training_files(self, remove_output=False):
        """
        Create all the training files from the box files

        Output:
                1 training file for each image with a matching name
        """
        # Move to training folder
        self.update_os_directory()
        self._check_boxes_exists()

        # Create training files for each image 
        # and add them to training_files dictionary
        for name, path in self.images.iteritems():
            command = "tesseract %s %s box.train" % (path, name)
            if remove_output:
                print "Generating training for file: %s" % name
                command += "  >/dev/null 2>&1"
            os.system(command)

            training_file = "%s.tr" % name
            if not os.path.exists(training_file):
                raise ValueError("No training file was generated for: %s" % name)
            self.training_files[name] = training_file
   
    def extract_unicharset(self, remove_output=False):
        """
        Extract the unicharset from the box_files

        Output:
                @unicharset : file
        """
        # Move to training folder
        self.update_os_directory()
        self._check_boxes_exists()
        
        # Create one string with all the boxes
        box_paths = ""
        for _, path in self.box_files.iteritems():
            box_paths +=  (path + " ")
        
        command = "unicharset_extractor %s" % box_paths
        if remove_output:
            print "Extracting unicharset"
            command += " >/dev/null 2>&1"
        os.system(command)

    def _check_unicharset(self):
        if not os.path.isfile("unicharset"):
            raise ValueError("You have to extract unicharset from box files")

    def run_mftraining(self, remove_output=False):
        """
        Create some of the files mandatory for tesseract to work

        Output:
                @lang.unicharset : file
                @lang.inttemp : file
                @lang.pffmtable : file
                @lang.shapetable : file
        """
        # Move to training folder
        self.update_os_directory()
        # Make sure all training files have been created
        if len(self.training_files.items()) < len(self.images):
            raise ValueError("You have not created training files for all images")
       
        # Check the necessary files exist
        self._check_font_properties()
        self._check_unicharset()

        # Create one string with the names of all the training files
        training_paths = ""
        for _, path in self.training_files.iteritems():
            training_paths += (path + " ")

        # Start with mf training
        command = "mftraining "
        command += "-F font_properties " # We have already checked this file exits
        command += "-U unicharset " # We have already checked this file exists
        command += "-O %s.unicharset %s " % (self.language, training_paths)
        if remove_output:
            print "Starting mftraining"
            command += " >/dev/null 2>&1"
        os.system(command)
        
        # mf training creates inttemp, pffmtable and shapetable
        # these need to be renamed 
        os.system("mv inttemp %s.inttemp" % self.language)
        os.system("mv pffmtable %s.pffmtable" % self.language)
        os.system("mv shapetable %s.shapetable" % self.language)

    def run_cntraining(self, remove_output=False):
        """
        Create the normproto file mandatory for tesseract to work

        Output:
                @lang.normproto : file
        """
        # Moce to training folder
        self.update_os_directory()
        
        # Make sure all training files have been created
        if len(self.training_files.items()) < len(self.images):
            raise ValueError("You have not created training files for all images")

        # Create one string with the names of all the training files
        training_paths = ""
        for _, path in self.training_files.iteritems():
            training_paths += (path + " ")

        # then run cntraining to get the normproto file
        command = "cntraining %s" %training_paths
        if remove_output:
            print "Starting cntraining"
            command += " >/dev/null 2>&1"
        os.system(command) 

        # Rename the normproto so it is included in the training data
        os.system("mv normproto %s.normproto" % self.language)

    def combine_tessdata(self, output_dir=None):
        """
        Create the final data file used by tesseract to read images

        Params:
                @output_dir : str   
                The folder to put the lang.traineddata file

        Output:
                @lang.traineddata : file 
        """
        # Move to training folder
        self.update_os_directory()
       
        # Check to see if there is a word list
        if not os.path.isfile("words_list"):
            print "You might want to include a list of word in you chosen language"
        else:
            command = "wordlist2dawg words_list "
            command += "%s.word_dawg " % self.language
            command += "%s.unicharset " % self.language
            os.system(command)

        # Check to see if there is a frequent words list
        if not os.path.isfile("frequent_words_list"):
            print "You might want to include a list of the most frequent words"
        else:
            command = "wordlist2dawg frequent_words_list "
            command += "%s.freq-dawg " % self.language
            command += "%s.unicharset " % self.language
            os.system(command)

        # Combine all the above mentioned files into one training set 
        os.system("combine_tessdata %s." % self.language)
        
        if output_dir is not None:
            output = "%s.traineddata" % self.language
            print "moving %s to %s" % (output, output_dir)
            os.system("sudo mv -f %s %s" % (output, output_dir))

