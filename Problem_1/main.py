from __future__ import print_function # to allow for \r
import os
import sys
import random
import bisect
from copy import copy
from time import time

import Cython
import subprocess

subprocess.Popen('python setup.py build_ext --inplace',shell=True).wait()

from helpers import cnf_t,data_t,init_population,test_individual_on_clause
from helpers import evaluate_fitness,choose_parent,flip_heuristic,mutate 
from helpers import get_child,get_two_best_individuals,get_next_generation
from helpers import init_data_log,log_data,train 

def main():
	# load data from all .cnf files
	d = data_t() 
	# the var counts to train on
	var_types = ["var_20","var_50","var_75","var_100"] 
	# train on the variables counts specified above
	train(d,var_types,population_size=10) 

if __name__ == '__main__':
	main()








