#!/usr/bin/env python
import os
import sys
import numpy as np
import random
import shutil
from queue import Queue
from PIL import Image

TEST = True

UNIQUE_DIRNAME    = 'unique'
DUPLICATE_DIRNAME = 'duplicates'

def thread_worker(q, num):
    while not q.empty():
        file_name = q.get()
        print(str(num) + ' ' + file_name)

def create_queue():
    q = Queue()

    for file in os.listdir():
        abspath = os.path.abspath(file)
        if os.path.isfile(abspath):
            q.put(abspath)

    return q
    
def copy_file(source, to):
    print("Creating a copy of file {0:<30} as {1:<30}".format(source, to))
    shutil.copyfile(source, to)


def create_random_image_set():
    # Test file name list
    test_file_names = os.listdir()

    max_file_count = 50

    # Assign a dictionary using
    # Key: file name from directory test_files/
    # Value: a list of files names with a random number with the duplicated file name
    files_to_create = {}

    for _ in range(max_file_count):
        choice = random.choice(test_file_names)
        random_val = random.randint(1, 1000)

        file_name = "{0}_{1}".format(random_val, choice)

        # Create a test set
        copy_file("./" + choice, "../test_files_output/" + file_name)


def cleanup_test_dir():
    # Save the test file directory
    main_dir = os.getcwd()

    # Enter the output file directory
    os.chdir('../test_files_output')

    # Start cleanup
    print("Cleaning the test file output directory.")
    for file in os.listdir():
        print("Removing {0}".format(file))

        try:
            os.remove(file)
        except IsADirectoryError:
            shutil.rmtree(file, ignore_errors=True)
            
    # Return to main directory
    os.chdir(main_dir)


def setup_test_files(dir):
    cleanup_test_dir()
    create_random_image_set()
    os.chdir(dir + '/../test_files_output')


def find_duplicates(dir):
    # Python script directory
    file_dir = os.path.dirname(os.path.realpath(__file__))
    # Create directory string to be sure of format
    abs_dir = os.path.abspath(dir)

    # Check if it is an absolute path and whether the dirname matches script
    # location. If it is the same don't execute.
    if os.path.isabs(dir) and file_dir == abs_dir:
        print("Cannot run file in script location")
        return

    # Go to given directory
    os.chdir(abs_dir)

    if TEST:
        setup_test_files(abs_dir)

    # Create two directories to group the images
    os.mkdir('./' + UNIQUE_DIRNAME)
    os.mkdir('./' + DUPLICATE_DIRNAME)

    queue = create_queue()
    
    while not queue.empty():
        file = queue.get()
        f_abs_path = os.path.abspath(file)
        uniques = os.listdir('./' + UNIQUE_DIRNAME)
        
        if os.path.isfile(f_abs_path):
            with Image.open(f_abs_path) as im_file:
                if len(uniques) == 0:
                    shutil.move(f_abs_path, os.getcwd() + '/' + UNIQUE_DIRNAME)
                else:
                    match_found = False
                    for unique_file in uniques:
                        unique_abs_path = os.path.abspath('./' + UNIQUE_DIRNAME + '/' + unique_file)
                        
                        with Image.open(unique_abs_path) as unique_im:

                            if unique_im.format == im_file.format and unique_im.size[0] == im_file.size[0] and unique_im.size[1] == im_file.size[1]:
                                shutil.move(f_abs_path, os.getcwd() + '/' + DUPLICATE_DIRNAME)
                                print("{:<15} {:<30} -> {:<30}".format("Found match:", os.path.basename(file), unique_file))
                                match_found = True
                                break
                            
                    if not match_found:
                        shutil.move(f_abs_path, os.getcwd() + '/' + UNIQUE_DIRNAME)
                        print("{:<15} {}".format("Found unique:", os.path.basename(file)))    
    

if __name__ == "__main__":

    if not(len(sys.argv) > 1):
        print("No arguments given. Terminating.")
        os._exit(0)

    find_duplicates(sys.argv[1])
