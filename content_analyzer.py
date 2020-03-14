'''
Created on 25/02/2020

@author Davide Maiorca

Counts the occurrence 
@author: Davide
'''
import re
import os
from collections import OrderedDict
import sys
import glob
from c_log import Log

class ContentAnalyzer(object):
    '''
    classdocs
    '''


    def __init__(self, api_list_name):
        '''
        Constructor for the content analyzer. Loads the essential apis
        '''
        self.stringhe = OrderedDict()
        self.log = Log()
        self.api_base = self._load_classes(api_list_name)
        self.key_base = self.api_base.keys()
        #print self.key_base
        self.dizionari = {}
        

    def _load_classes(self, api_list_name):
        '''Puts all the api classes in a list.'''
        api = OrderedDict()
        with open(api_list_name, "r") as api_list: 
            for x in api_list.readlines():
                x.strip()
                x = x[:-1]
                api[x] = 0 
        return api
    
    def _get_bytecode_api(self, group):
        """Given a list obtained from a name structure, extract the correct api that might be used"""
        if len(group) == 1: # associated to push string
            return [group[0]]
        if len(group) == 2:  # Associated to a standard Qname:
            if (group[0] == "" or group[0]== " "):
                return [group[1]]
            else:
                return [group[0] + "." + group[1]]
        else:
            cands = [re.sub(':', ".", element) for element in group if ":" in element]
            return cands
    
    def fast_string_get(self, line):
        """Gets package and class information from a bytecode string"""
        
        cands_i = line.split()
        if len(cands_i) > 1:
            cand_instr = cands_i[0]
        else:
            cand_instr = ""
        # if cand_instr in self.instr_base:
        #     self.file_instr[cand_instr] += 1
            
        if ("Qname" not in line) and ("RTQname" not in line) and ("Multiname" not in line) and ("pushstring" not in line):
            return
        else:
            group = re.findall(r'\"(.*?)\"', line)
            for api in self._get_bytecode_api(group):
                if api in self.key_base:
                    self.file_api[api] += 1

    def _get_string_occurrences(self, filename):
        '''Find all name properties / method calls / attributes'''
        bytecode = open(filename, "r")
        lines = bytecode.readlines()
        map(self.fast_string_get, lines)
        bytecode.close()
    
    def _sample_analysis(self, folder_path):
        '''Gets api occurrences for each script contained in a folder related to a sample.'''
        try:
            for target in os.listdir(folder_path):
                sub_path = os.path.join(folder_path, target)
                if os.path.isdir(sub_path):
                    self._sample_analysis(sub_path)
                else:
                    if target == '.DS_Store': # Skip default MacOs file
                        continue
                    self._get_string_occurrences(sub_path)
        except:
            self.log.logger.warning("No scripts for file: " + folder_path)
    
    def extract_script_information(self, folder_path):
        self.file_api = self.api_base.copy()  # Reset api information
        self.feature_vector = []
        self.statistica_file = {}
        self._sample_analysis(folder_path)
        self.feature_vector = self.file_api.values()
            

            
