'''

14/02/2020
FlashBuster - Path Generation
@author Davide Maiorca

This code takes the Flash samples related to a folder and saves their path,
together with their label. Samples with the same label should go to the same
folder. 
Labels can be either 0 (Malicious) or 1 (Benign)

Paths are saved in a file called paths.txt

Usage: path_generation.py MY_FOLDER LABEL

MY_FOLDER should be the full path of the folder
'''

import sys
import os

def check_label(label):
    """Check if the input label is either 0 or 1, quits otherwise."""
    try:
        if int(label) == 0 or int(label) == 1:
            return True
        else:
            return False
    except:
        return False

def check_input_path(input_path):
    """Checks if the given folder exists. You must give the full path"""
    try:
        input_path = os.listdir(input_path)
        return input_path
    except:
        return False

def save_paths(input_path, label, out_path):
    """Saves the paths and the related label on a list of paths.
       The output is structured in this way:
       LABEL FULL_PATH FILE_NAME
    """

    with open(out_path, "a") as outp: # Paths are appeneded and not overwritten
        try:
            for fname in os.listdir(input_path):
                full_path = os.path.join(input_path, fname)
                if os.path.isdir(full_path):
                    print "Found folder: " + full_path + " Skipping..."
                else:
                    outp.write(str(label) + " " + str(full_path) + " " + str(fname) + "\n")
        except:
            print "Unexpected error in writing the file."
            sys.exit(-3)



if __name__ == '__main__':

    if len(sys.argv) != 3:
        print "Usage: path_generation.py FOLDER_NAME LABEL"
        sys.exit(0)
    input_path = sys.argv[1] # Folder name (give the full path)
    label = sys.argv[2]
    out_path = "paths.txt"


    if check_label(label) is not True:
        print "Error: labels must either be 0 or 1. Quitting..."
        sys.exit(-1)

    if check_input_path(input_path) is True:
        print "Error: folder path does not exist. Quitting..."
        sys.exit(-2)

    save_paths(input_path, label, out_path)



    




