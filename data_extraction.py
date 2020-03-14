'''
Created on 14/feb/2020
@author Davide Maiorca

Flash Buster - Data Extraction

This code runs FFDEC on a number of files and automatically extracts all the required data for the
analysis with the feature extractor.
This code implements a Java-To-Python interface by loading the Java Virtual Machine at runtime. It runs a modified version
of ffdec with which it is possible to automatically extract multiple files without shutting down the VM. 

Use the contained ffdec.jar and all the libraries in the lib folder.
Note that the employed version of ffdec_lib.jar is 7.0.1 and requires some
updates (known issue).

Before executing the program, create a folder called "outputs" and, inside this folder, another one called "dumps".

The data extraction must be executed from inside the data_analysis folder.


'''
import jpype as jp
import os, sys
from c_log import Log


class Extractor(object):

    def __init__(self, jvm_path = None, log_obj = None):
        self.jvm_path = jvm_path
        self.log_obj = log_obj
        self.path_list = []
        self.fname_list = []
        self.labels = []
        self.base_output = os.path.join(os.path.abspath("."), "outputs")
        self.log_obj.logger.info("Obtaining file paths...")
        self.get_file_paths()


    def run_analysis(self):
        jp.startJVM(jp.getDefaultJVMPath(), "-Djava.class.path=%s/lib/" %os.path.abspath("."), "-Djava.class.path=%s/ffdec.jar" %os.path.abspath("."))
        self.parser = jp.JClass('com.jpexs.decompiler.flash.gui.Main')
        self.log_obj.logger.info("Analyzing files...")
        self.analyze_paths()
        self.log_obj.logger.info("Analysis complete.")
        jp.shutdownJVM()


    def get_file_paths(self):
	not_found_count = 0
        try:
            with open("paths.txt", "r") as pth:
                for line in pth.readlines():
                    full_path = line.split(" ")[1] # Paths should not have any spaces
                    fname = line.split(" ")[2]
                    if os.path.exists(full_path):
                        self.path_list.append(full_path)
                        fname = fname.replace(".swf","")[:-1] # remove extensions from files
                        print fname
                        self.fname_list.append(fname)
                        self.labels.append(line.split(" ")[0])
                    else:
                        self.log_obj.logger.warning("File " + full_path + " not found!")
                        not_found_count+=1
            print(not_found_count)
        except:
            self.log_obj.logger.error("Error in parsing file paths.txt or file not found. Quitting...")
            sys.exit(-1)

    def check_folder(self, folder):
        """Check if folder exists."""
        if os.path.isdir(folder):
            return True
        else:
            return False


    def analyze_paths(self):
        """Performs the analysis of each file. Saves the results in the folder
        outputs, where a folder with the name of each file is created,
        containing
        """
        for i in range (0, len(self.path_list)):
            try:
                pth = self.path_list[i]
                fname = self.fname_list[i]
                self.log_obj.logger.info("Analyzing " + pth)
                dumps_folder = os.path.join(self.base_output, "dumps")
                if self.check_folder(dumps_folder) is False:
                    print "Error: dumps folder missing. Quitting..."
                    sys.exit(-2)

                dumps_path = os.path.join(dumps_folder, fname + ".dump") #TODO: make the dumps folder internal to each folder with a filename

                scripts_path = os.path.join(self.base_output, fname)
                prtstream = jp.java.io.PrintStream("/dev/null") # redirects to null the stdout output, as we are only extracting the scripts now - #FIXME in windows
                jp.java.lang.System.setOut(prtstream)
                arr = jp.JArray(jp.JString)([str("-onerror"), str("abort"), str("-format"), str("script:pcode"), str("-export"), str("script"), str(scripts_path), str(pth)])
                self.parser.main(arr)
                prtstream = jp.java.io.PrintStream(dumps_path) # structural information is printed to stdout, so we can redirect it to the dump file
                jp.java.lang.System.setOut(prtstream)
                arr = jp.JArray(jp.JString)([str("-dumpSWF"), str(pth), str("stdout"), str(dumps_path)])
                self.parser.main(arr)
            except:
                print("Cannot analyze file {}".format(pth))
 
if __name__ == '__main__':
    
    log_obj = Log() 
    log_obj.logger.info("FlashBuster V 1.0 (Feb. 2020) - Data Extraction")
    jvm_path = "/usr/lib/jvm/java-8-openjdk-amd64/jre/lib/amd64/libjava.so" # This should be .dll for windows
    extractor = Extractor(jvm_path, log_obj)
    extractor.run_analysis()
