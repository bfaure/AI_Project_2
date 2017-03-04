from __future__ import print_function # to allow for \r
import os
import sys
import random
import bisect
from copy import copy
from time import time

# class to hold all all information required about a .cnf file
class cnf_t(object):
	def __init__(self,filename):
		self.filename = filename
		self.clauses = [] # list of integer lists (1 per clause)
		self.num_vars = -1 # number of variables in equation
		self.num_clauses = -1 # number of clauses in equation
		self.read_file() # load .cnf file

	# parses a single .cnf file
	def read_file(self):
		f = open(self.filename,"r")
		text = f.read()
		lines = text.split("\n")

		self.clauses = [] # each element is a single clause (list of integers)
		current_clause = [] # buffer to hold current clause being parsed

		for line in lines:
			if line[0]=="%": break # denotes the eof
			if line[0]=="p": # get the header data
				elems = line.split(" ")
				self.num_vars = int(elems[2]) # save the number of variables in equation
				continue
			if line[0]!="c": # skip all comment lines
				elems = line.split(" ") # split line on spaces
				for elem in elems: # iterate over each element
					if elem=="0":
						self.clauses.append(current_clause) # append the full clause
						current_clause = [] # empty the read buffer
						continue
					if elem!="": # if there is a clause element
						val = int(elem)
						current_clause.append(val) # add to current read buffer
		self.num_clauses = len(self.clauses) # save the number of clauses read

	# prints out a representation of the .cnf file to terminal
	def print_cnf(self):
		print("-------------------------------------------")
		print("Filename: "+self.filename+", Clauses: "+str(self.num_clauses)+", Variables: "+str(self.num_vars))
		for c in self.clauses:
			print(c)
		print("-------------------------------------------")

# class to handle loading/accessing of .cnf data
class data_t(object):

	# num_equations is the maximum number of .cnf files to parse per var ct level
	def __init__(self,num_equations=100):
		self.num_equations = num_equations # max num .cnf files per var level

		self.var_20 = [] # to hold all .cnf with 20 var
		self.var_50 = [] # to hold all .cnf with 50 var
		self.var_75 = [] # to hold all .cnf with 75 var
		self.var_100 = [] # to hold all .cnf with 100 var

		self.load_data() # load in up to num_equations .cnf files per var count level

	def load_data(self):
		
		parent_dir = "data/"
		child_dirs = ["20/","50/","75/","100/"]
		num_read_total = 0 # total number of .cnf files read
		max_to_read = self.num_equations*4

		progress_bar_length = 25
		progress_bar_item = "-"
		progress_bar_empty_item = " "
		print("\n",end="\r")

		for d in child_dirs: # iterate over all data directories
			if d == "20/": cur_type = "var_20"
			if d == "50/": cur_type = "var_50"
			if d == "75/": cur_type = "var_75"
			if d == "100/": cur_type = "var_100"

			path = parent_dir+d
			items = os.listdir(path)

			for f in items:

				progress = int (float(num_read_total) / float(max_to_read) * progress_bar_length)
				progress_string = "["
				for prog_index in range(progress_bar_length):
					if prog_index <= progress: progress_string += progress_bar_item
					else: progress_string += progress_bar_empty_item
				progress_string += "]"
				print("Loading .cnf files... "+progress_string,end="\r")

				if f.find(".cnf")!=-1:
					filename = path+f 
					cur = cnf_t(filename)
					self.__dict__[cur_type].append(cur) # add to appropriate member item
					num_read_total+=1
					if len(self.__dict__[cur_type])>=self.num_equations: break
		print("\n",end="\r")

# creates 'population_size' 'variable_count' ramdomized inviduals
def init_population(variable_count,population_size):
	#log.write("Initializing population\n")
	
	population = [] # will be filled with initialized population members
	for _ in range(population_size):
		#print("Initializing var "+str(variable_count)+" population... "+str(len(population)+1),end="\r")
		individual = [] # to hold a single individual
		for _ in range(variable_count):
			# choose 0 or 1 randomly
			if bool(random.getrandbits(1))==True: individual.append(1)
			else: individual.append(0)
		# add individual to population
		population.append(individual) 
	#print("\n",end="\r")
	return population

# checks if the individual suceeds in a single clause, returns True if so, False o.w.
def test_individual_on_clause(individual,clause):
	for item in clause:
		if item>0 and individual[abs(item)-1]==1: return True # need a 1 to prove success
		if item<0 and individual[abs(item)-1]==0: return True # need a 0 to prove success
	return False # True if never proven False

# evaluates the fitness of 'individual' on all cnf_t instances in 'environments' list
def evaluate_fitness(individual,environment):
	overall_fitness = 0
	# iterate over all clauses in cnf_t environment
	for clause in environment.clauses:
		if test_individual_on_clause(individual,clause): overall_fitness+=1
	return overall_fitness

# choose a parent from the list of individuals based on the probabilities transferred over
# from the list of fitnesses, using cumulative distribution function (cdf)
def choose_parent(fitnesses):
	def cdf(weights):
		total = sum(weights)
		result = []
		cumsum = 0
		for w in weights:
			cumsum += float(w)
			result.append(cumsum/total)
		return result

	cdf_vals = cdf(fitnesses)
	x = random.random()
	idx = bisect.bisect(cdf_vals,x)
	return idx

# applies the flip heuristic
def flip_heuristic(child,environment):
	bit_flips = 0
	while True:
		initial_fitness = evaluate_fitness(child,environment)
		scanned = [False] * len(child)
		orig_child = copy(child)

		current_fitness = initial_fitness 

		while True:
			# check if we have already scanned all bits
			scanned_all = True 
			for did_scan in scanned:
				if did_scan==False:
					scanned_all = False 
					break
			if scanned_all: break

			while True: # find a bit to scan that we haven't checked yet
				bit = random.randint(0,len(child)-1)
				if scanned[bit]==False: break

			# mark that we have scanned this bit
			scanned[bit] = True 

			#current_fitness = evaluate_fitness(child,environment) # evaluate fitness before bit flip
			child[bit]=0 if child[bit]==1 else 1
			bit_flips += 1
			new_fitness = evaluate_fitness(child,environment) # evaluate new fitness
			
			# if this has not increased our fitness, re-flip back to original
			if new_fitness<current_fitness: 
				child[bit] = 0 if child[bit]==1 else 1
				bit_flips += 1
			# otherwise, leave the change and update the current fitness
			else:
				current_fitness = new_fitness

		# check if this round of flip_heuristic has increased the fitness of the child
		if current_fitness > initial_fitness: continue
		
		# if we get here then this round has not increased the fitness of the child
		# so we should return the current state of the child
		else: return orig_child,bit_flips

# applies the mutation to a single individual, returns mutated version
def mutate(individual):
	new_individual = []
	bit_flips = 0

	for item in individual:
		if bool(random.getrandbits(1))==True: # flip the bit
			bit_flips+=1
			if item==0: new_individual.append(1)
			else: new_individual.append(0)
		else:
			new_individual.append(item)
	return new_individual,bit_flips

# Returns the child of parents p1 and p2
def get_child(p1,p2,environment):
	
	child = [] 
	bit_flips = 0
	
	for p1_trait,p2_trait in zip(p1,p2):
		if bool(random.getrandbits(1))==True: child.append(p1_trait)
		else: child.append(p2_trait)
	
	# mutation stage
	should_mutate = random.randint(1,10)
	if should_mutate!=10: 
		child,flips = mutate(child)
		bit_flips+=flips
	
	child,flips = flip_heuristic(child,environment)
	bit_flips+=flips

	return child,bit_flips

# Scans the fitnesses list for the two best items, returns their indices
def get_two_best_individuals(fitnesses):
	# calculate the two best individuals
	best_value = -1
	second_best_value = -1
	best_index = -1
	second_best_index = -1
	for i in range(len(fitnesses)):
		if fitnesses[i]>best_value:
			best_value = fitnesses[i]
			best_index = i 
		elif fitnesses[i]>second_best_value:
			second_best_value = fitnesses[i]
			second_best_index = i 
	return best_index,second_best_index

# assembles the next generation based on the results of testing in the prior
def get_next_generation(population,fitnesses,environment):
	# to hold the new popuation
	new_population = [] 

	# get the indices of the two best individuals in the population
	best,runner_up = get_two_best_individuals(fitnesses)

	# append the two best individuals onto the next generation
	new_population.append(population[best])
	new_population.append(population[runner_up])

	# number of bit flips performed
	bit_flips = 0

	while len(new_population)<len(population):

		# probabilistic selection
		p1 = population[choose_parent(fitnesses)]
		p2 = population[choose_parent(fitnesses)]

		# Uniform crossover reproduction, mutation, and flip heuristic
		child,flips = get_child(p1,p2,environment)

		# add bit flips
		bit_flips+=flips

		# add new child to new population
		new_population.append(child)

	return new_population,bit_flips

# puts the header information in a data log file
def init_data_log(file):
	file.write("File        Generations        Bit Flips          Time\n")
	file.write("______________________________________________________\n\n")
	file.flush()

# logs the results after the population has suceeded in solving a .cnf file
def log_data(file,cur_cnf,generation,bit_flips,time):
	file.write(str(cur_cnf)+"\t"+str(generation)+"\t"+str(bit_flips)+"\t"+str(time)+"\n")
	file.flush()

# Takes in a data_t object and splits training into the different variable count .cnf files
def train(data,var_types,population_size=10,logging=True):

	for var_ct in var_types:

		if logging: data_log 	= open(var_ct+".txt","w")
		environments 			= data.__dict__[var_ct] # all environments w/ same var count
		perfect_fitness 		= environments[0].num_clauses # perfect fitness for this environment set
		num_vars 				= environments[0].num_vars # number of vars in this environment set
	
		if logging: 	init_data_log(data_log) # add header to data log file	
		var_start_time 	= time() # start for this set of .cnf files

		for current_environment in environments:

			# create progress bar string
			progress_bar_length = 10
			progress_bar_item = "-"
			progress_bar_empty_item = " "
			progress = int (float(environments.index(current_environment)) / float(len(environments)) * progress_bar_length)
			progress_string = "["
			for prog_index in range(progress_bar_length):
				if prog_index <= progress: progress_string += progress_bar_item
				else: progress_string += progress_bar_empty_item
			progress_string += "]"

			cur_file 		= current_environment.filename.split("/")[2]
			best_fitness 	= -1 # to hold the best fitness found over all generations
			pop 			= init_population(num_vars,population_size) # initialize population
			generation 		= 0 # current generation number
			bit_flips 		= 0 # number of bit flips performed
			start_time		= time() # get start time of algorithm

			# train population on current file
			while best_fitness<perfect_fitness:

				fitnesses 		= [] # to hold the evaluated fitness for each individual
				highest_fitness = -1 # to hold the highest fitness of this generation

				for individual in pop: # evaluate fitness for each individual
					fitness = evaluate_fitness(individual,current_environment) # get fitness of individual
					fitnesses.append(fitness) # add to list of fitnesses
					if fitness > highest_fitness:
						highest_fitness = fitness # set max if applicable

				if highest_fitness>best_fitness: # save this as the best if higher than prev. best
					best_fitness = highest_fitness

				if environments.index(current_environment) % 4 == 0: print("                                                                          ",end="\r")
				print(var_ct+": "+progress_string+" Generation = "+str(generation)+", Fitness = "+str(best_fitness)+"/"+str(perfect_fitness)+", Bit Flips = "+str(bit_flips),end="\r")
				sys.stdout.flush()

				if best_fitness==perfect_fitness: # if we have finished this .cnf file
					if logging: log_data(data_log,cur_file,generation,bit_flips,time()-start_time) # log results to file
					break

				pop,flips = get_next_generation(pop,fitnesses,current_environment)
				bit_flips+=flips
				generation+=1

		if logging: data_log.close() # close the logging file
		print("                                                                                                                   ",end="\r")
		print(var_ct+": Total time "+str(time()-var_start_time)[:6]+" seconds",end="\r")
		print("\n",end="\r")