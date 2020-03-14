'''
Created on 14/mar/2020
This module parses SWFDump basing on the SWF Specifications.

@author: Davide
'''
from c_log import Log 
from collections import OrderedDict
class DumpAnalyzer(object):
    '''
    This class parses SWFDump basing on the SWF Specifications.
    '''


    def __init__(self):
        '''
        Constructor for the analyzer.
        Parameters:
        sample_filename: file object related to the file to be parsed
        '''
        self.keys = ['frames', 'shapes', 'sounds', 'binary_data', 'scripts', 'fonts', \
                'sprites', 'morph_shapes', 'texts', 'images', 'buttons', 'videos', \
                'errorTag', 'unknown']
        self.log = Log()
        self.func_names = ['_update_' + str(x) for x in self.keys]
        self.tags = OrderedDict()
        self.is_empty = True
        self.structural_occurrences = []
        
    
    def _iniatilize_dict(self):
        """Initialize dictionary."""
        for key in self.keys:
            self.tags[key] = 0
    
    def _update_tag(self, tag, line):
        '''Update tag values.'''
        tag['count'] += 1
        tag['lengths'].append(self._get_tag_length(line))
    
    def _update_frames(self, line):
        '''Update frames number.'''
        if "ShowFrame" in line:
            self.tags['frames'] += 1
    
    def _update_shapes(self, line):
        '''Update shapes number.'''
        if "DefineShape" in line or "DefineShape2" in line \
        or "DefineShape3" in line or "DefineShape4" in line:
            self.tags['shapes'] += 1
    
    def _update_sounds(self, line):
        '''Update sounds number.'''
        if "DefineSound" in line or "SoundStreamHead1" in line \
        or "SoundStreamHead-2" in line or "SoundStreamBlock" in line:
            self.tags['sounds'] += 1
    
    def _update_binary_data(self, line):
        '''Update binary data number.'''
        if "DefineBinaryData" in line:
            self.tags['binary_data'] += 1
    
    def _update_scripts(self, line):
        '''Update scripts number.'''
        if "DoABC" in line or "DoABCDefine" in line \
        or "DoInitAction" in line or "DoAction" in line \
        or "DefineButton" in line:
            self.tags['scripts'] += 1
    
    def _update_fonts(self, line):
        '''Update fonts number.'''
        if "DefineFont" in line or "DefineFont2" in line \
        or "DefineFont3" in line or "DefineCompactedFont" in line \
        or "DefineFontInfo" in line or "DefineFontInfo2" in line \
        or "DefineFontName" in line:
            self.tags['fonts'] += 1
    
    def _update_sprites(self, line):
        '''Update sprites number.'''
        if "DefineSprite" in line:
            self.tags['sprites'] += 1
    
    def _update_morph_shapes(self, line):
        '''Update Morph Shapes number.'''
        if "DefineMorphShape" in line or "DefineMorphShape2" in line:
            self.tags['morph_shapes'] += 1
            
    def _update_texts(self, line):
        '''Update Texts number.'''
        if "DefineText" in line or "DefineText2" in line \
        or "DefineEditText" in line:
            self.tags['texts'] += 1
    
    def _update_images(self, line):
        '''Update Images number.'''
        if "DefineBits" in line or "JPEGTables" in line \
        or "DefineBitsJPEG2" in line or "DefineBitsJPEG3" in line \
        or "DefineBitsJPEG4" in line or "DefineBitsLossless1" in line \
        or "DefineBitsLossless2" in line:
            self.tags['images'] += 1
    
    def _update_videos(self, line):
        '''Update Videos number.'''
        if "DefineVideoStream" in line or "VideoFrame" in line:
            self.tags['videos'] += 1
        
    def _update_buttons(self, line):
        '''Update Buttons number.'''
        if "DefineButton" in line or "DefineButton2" in line:
            self.tags['buttons'] += 1
    
    def _update_errorTag(self, line):
        '''Update ErrorTag number.'''
        if "ErrorTag" in line:
            print "Found errorTag in file: " + self.name
            self.tags['errorTag'] += 1
    
    def _update_unknown(self, line):
        '''Update Unknown number.'''
        if "Unknown" in line:
            self.tags['unknown'] += 1
    
    def _get_tag_length(self, line):
        '''Get lengths of a tag.'''
        mydata = ' '.join(line.split())   
        my_data = mydata.split('len=') 
        data = [int(s) for s in my_data[1].split() if s.isdigit()]
        return data[0]                         
    
    def count_occurrences(self, filename):
        '''Count structural occurrences.'''
        m = globals()['DumpAnalyzer']
        for line in filename.readlines():
            if ("len=") not in line:
                continue
            for func_name in self.func_names:
                self.is_empty = False
                func = getattr(m, func_name)
                func(self, line)

         
    def print_occurrences(self):
        '''Print structural occurrences.'''
        self.log.logger.info(self.structural_occurrences)
    
    def create_occurrences(self, filename):
        '''Creates a list of occurrences for a .dump file.'''
        self.name = filename
        self._iniatilize_dict()
        self.structural_occurrences = self.tags.values() #In case the dump analysis fails, every feature will be set to zero 
        input_file = open(filename, "r")
        self.count_occurrences(input_file)
        self.structural_occurrences = self.tags.values()
        input_file.close()


if __name__ == '__main__':
    analyzer = DumpAnalyzer()
    analyzer.create_occurrences('/home/dmaiorca/Documenti/shared_vm/flash/flashbuster/src/data_analysis/outputs/dumps/965e91c46b76c47537009c72e1ececd052d246de43f2943751cbb4d77763320f.dump')
    analyzer.print_occurrences()
    #analyzer.write_occurrences(out)
    inp.close()
    out.close()
            
    
    
    

    
    
    
