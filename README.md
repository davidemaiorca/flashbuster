FlashBuster V. 1.0

FlashBuster is an automatic, static analyzer for SWF files. Given an ensemble of SWF files, the system produces a .libsvm file that can be used on
machine learning-based classifiers for classification.

The system is based on a modified version of the JPEXS library (https://github.com/jindrapetrik/jpexs-decompiler)

The system is composed of three modules:

A. Path Generation
B. Data Extraction
C. Feature Extraction

The two modules must be run sequencially to obtain the file of the features. 

Installation Notes

1. Install miniconda (https://docs.conda.io/en/latest/miniconda.html) and create a virtual environment with Python 2.7.

conda create -n envname python=2.7
conda activate envname

Be sure to see (envname) before the command prompt to continue

2. Install JPype

pip install JPype1

3. Install java 1.8 (FlashBuster will NOT work with more recent versions of Java)

sudo apt install openjdk-8-jdk openjdk-8-jre

4. Run path_generation.py on a folder that contains files of the same type (all malicious/all benign)

python path_generation.py [FOLDER (FULL PATH)] [LABEL] 

LABEL must either be 0 (for benign) or 1 (for malicious)

The output of this extraction is a file named "paths.txt" that should be in the same folder of the other python files.

5. Create a folder named outputs, and inside this folder one called "dumps". The folders should not contain other data.

6. Run the data extractor and saves the extracted dumps in the outputs folder.

python data_extraction.py

7. Run the feature extractor, which outputs the file features.libsvm

python feature_extraction.py
