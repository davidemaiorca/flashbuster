'''
Created on 14/feb/2020

@author: Davide Maiorca
davide.maiorca@unica.it

Flash Buster - A system to detect malicious SWF Files

In order to analyze an swf file:

- There must be a path that contains malicious and benign swf files. To do so, create a folder (e.g., "samples") and
create two subfolders with MANDATORY names: "Malicious" and "Benign". Inside one of these two folders, you have to put
the swf file to analyze (e.g., test.swf). The "samples" path must be assigned to the samples_path variable.

- You need to store the output of the FFDec Extraction in a folder that will be assigned to the output_path variable.
The output must be stored in this way. 

For a file called test.swf:
1) Create a folder called, for example, "outputs". Inside this folder, there must be two subfolders called (MANDATORY):
"Malicious" and "Benign". Inside each of this folder, there must be two subfolders (MANDATORY) called "script" and "dump".
2) The folder "script" MUST contain a subfolder with the same name of the swf file (in our case: test.swf). Such subfolder
will cont
ain all the bytecode-based scripts extracted by FFDEC
3) The folder "dump" must contain a .dump file with the same name of the swf file. Hence, in our example, test.swf.dump
Obviously, the FFDEC must be stored under the Malicious or Benign folder, depending on the type of the sample. 

'''

        
import os
import random
from c_log import Log
from content_analyzer import ContentAnalyzer
from structural_analyzer import DumpAnalyzer


class FeatureExtractor(object):
    
    def __init__(self):
        self.content_analyzer = ContentAnalyzer("complete_api_list")
        self.outp_file = "features.libsvm"
        self.structural_analyzer = DumpAnalyzer()
        self.jvm_path = jvm_path
        self.log_obj = log_obj
        self.path_list = []
        self.fname_list = []
        self.labels = []
        self.base_output = os.path.join(os.path.abspath("."), "outputs")
        self.log_obj.logger.info("Obtaining file paths...")
        self.get_file_paths()


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
        
    def write_libsvm_line(self, sample_name, label):
        '''Create line for libsvm dataset.'''
        with open(self.outp_file, "a") as outp:
            data_cont = self.content_analyzer.feature_vector
            data_struc = self.structural_analyzer.structural_occurrences
            outp.write(str(label) + " ")
            for i in xrange(0, len(data_cont)):
                if data_cont[i] != 0:
                    outp.write("%s:%s " % (i + 1, data_cont[i]))
            for i in xrange(len(data_cont), len(data_cont) + len(data_struc)):
                if data_struc[i - len(data_cont)] != 0:
                    outp.write("%s:%s " % (i + 1, data_struc[i - len(data_cont)]))
            outp.write("# " + sample_name)
            outp.write("\n")
            outp.close()
    
    def content_analysis(self, sample_path, sample_name):
        '''Extracts the content of the swf file in terms of strings.'''
        target_path = os.path.join(sample_path, sample_name) # The scripts are in a folder with the same name of the file
        self.content_analyzer.extract_script_information(target_path)

    def structural_analysis(self, dump_folder, sample):
        '''Runs structural analysis.'''
        path = os.path.join(self.base_output, dump_folder, sample + ".dump")
        try:
            self.structural_analyzer.create_occurrences(path)
        except:
            self.log_obj.logger.error("Error in file " + sample)

    
    def _sample_analysis(self, sample_path, sample_name, label):
        """Internals that, in order: 
        1) Run analysis of the content 
        2) Analyze the structure 
        3) Write a libsvm output
        
        """
        self.content_analysis(sample_path, sample_name)
        self.structural_analysis("dumps", sample_name)
        self.write_libsvm_line(sample_name, label)
    
    def run_extraction(self):
        """Extracts the features for a set of data.
        Parameters:
        - script_folder: the folder containing the bytecode for each sample (string)
        - dump_folder: the folder containing the structural information (string)
        - output: a string containing the name of the libsvm file
        - data: a list containing the file names to be parsed
        - label: the sample label to be written
        
        """

        file_count = 0
        self.log_obj.logger.info("Starting Feature Extraction...")
        for i in range(0, len(self.fname_list)):
            self.log_obj.logger.info("Analyzing file " + self.fname_list[i])
            file_count += 1
            self._sample_analysis(self.base_output, self.fname_list[i], self.labels[i])
            self.log_obj.logger.info("Number of files analyzed: " + str(file_count))


        
if __name__ == '__main__':
    
    log_obj = Log() 
    log_obj.logger.info("FlashBuster V 1.0 (Feb. 2020) - Data Extraction")
    jvm_path = "/usr/lib/jvm/java-8-openjdk-amd64/jre/lib/amd64/libjava.so" # This should be .dll for windows
    extractor = FeatureExtractor()
    extractor.run_extraction()
