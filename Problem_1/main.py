from __future__ import print_function # to allow for \r
import os
import sys
import random
import bisect
from copy import copy

log = open("debug.log","w")

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
	log.write("Initializing population\n")
	
	population = [] # will be filled with initialized population members
	for _ in range(population_size):
		print("Initializing var "+str(variable_count)+" population... "+str(len(population)+1),end="\r")
		individual = [] # to hold a single individual
		for _ in range(variable_count):
			# choose 0 or 1 randomly
			if bool(random.getrandbits(1))==True: individual.append(1)
			else: individual.append(0)
		# add individual to population
		population.append(individual) 
	print("\n",end="\r")
	return population

# checks if the individual suceeds in a single clause, returns True if so, False o.w.
# To check for success we will iterate over each item in the clause (which will be an
# integer item) and check if this item relates to a positive value in the individual,
# for example, if the clause input was [1,-2,3] and the individual was [1,1,1] then we
# would evaluate the output of 1 AND 0 AND 1 (outputs False)
def test_individual_on_clause(individual,clause):
	#individual_str = ''.join(str(e) for e in individual)
	#clause_str = ''.join(str(e)+" " for e in clause)
	#log.write("Testing "+individual_str+" on clause "+clause_str+"\n")

	for item in clause:
		var_index = abs(item)-1 # index of the variable in the individual
		result = individual[var_index] # get the item at said index
		if item>0: # if not negated, need a 0 to prove False
			if result==0: 
				#log.write("FAILURE\n")
				return False
		else: # if negated, need a 1 to prove False
			if result==1: 
				#log.write("FAILURE\n")
				return False
	#log.write("SUCCESS\n")
	return True # True if never proven False

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
	#fitnesses_str = ''.join(str(e)+" " for e in fitnesses)
	#log.write("Choosing parent from "+fitnesses_str+"\n")

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

	#log.write("Chose index = "+str(idx)+"\n")
	return idx

# applies the flip heuristic
def flip_heuristic(child,environment):
	
	while True:

		initial_fitness = evaluate_fitness(child,environment)
		scanned = [False] * len(child)
		orig_child = copy(child)

		while True:
			#random.seed() # re-seed the random function
			
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

			current_fitness = evaluate_fitness(child,environment) # evaluate fitness before bit flip
			if child[bit]==1: child[bit]=0
			else: child[bit]=1
			new_fitness = evaluate_fitness(child,environment) # evaluate new fitness
			
			# if this has not increased our fitness, re-flip back to original
			if new_fitness<current_fitness: child[bit] = 0 if child[bit]==1 else 1

		# check if this round of flip_heuristic has increased the fitness of the child
		if evaluate_fitness(child,environment) > initial_fitness: continue

		# if we get here then this round has not increased the fitness of the child
		# so we should return the current state of the child
		return orig_child

def normalize_fitnesses(fitnesses):
	total_fitness = float(sum(fitnesses))
	new_fitnesses = [float(e)/total_fitness for e in fitnesses]
	return new_fitnesses

def mutate(individual):
	new_individual = []
	for item in individual:
		if bool(random.getrandbits(1))==True: # flip the bit
			if item==0: new_individual.append(1)
			else: new_individual.append(0)
		else:
			new_individual.append(item)
	return new_individual

def get_child(p1,p2):
	child = []
	for p1_trait,p2_trait in zip(p1,p2):
		if bool(random.getrandbits(1))==True: child.append(p1_trait)
		else: child.append(p2_trait)
	# mutation stage
	should_mutate = random.randint(1,10)
	if should_mutate!=10: child = mutate(child)
	return flip_heuristic(child)

# assembles the next generation based on the results of testing in the prior
def get_next_generation(individuals,fitnesses,environment):
	new_population = []

	best_value = -1
	second_best_value = -1
	best_index = -1
	second_best_index = -1

	# calculate the two best individuals
	for i in range(len(fitnesses)):

		if fitnesses[i]>best_value:
			best_value = fitnesses[i]
			best_index = i 
			continue 
		if fitnesses[i]>second_best_value:
			second_best_value = fitnesses[i]
			second_best_index = i 

	# append the two best individuals onto the next generation
	new_population.append(individuals[best_index])
	new_population.append(individuals[second_best_index])

	pop_size = len(individuals)

	fitnesses = normalize_fitnesses(fitnesses)

	while len(new_population)<pop_size:

		# probabilistic selection
		p1 = individuals[choose_parent(fitnesses)]
		p2 = individuals[choose_parent(fitnesses)]

		# Uniform crossover reproduction, mutation, and flip heuristic
		child = get_child(p1,p2)

		# add new child to new population
		new_population.append(child)

	return new_population

# Takes in a list of cnf_t objects (all must have the same number of variables)
def train(environments):
	MAX_GENERATIONS = 100000

	for current_environment in environments:
		print("Fitting to "+current_environment.filename+"...")

		num_vars 		= current_environment.num_vars 
		num_clauses 	= current_environment.num_clauses 
		population_size = 10

		perfect_fitness = num_clauses
		print("Perfect fitness: "+str(perfect_fitness))

		best_fitness = -1 # to hold the best fitness found on each generation

		# get population_size randomized solutions of length num_vars
		pop = init_population(num_vars,population_size)

		generation = 0 # current generation number

		while best_fitness<perfect_fitness:
			fitnesses 	= [] # to hold the evaluated fitness for each individual

			highest_fitness = -1

			for individual in pop: # evaluate fitness for each individual
				fitness = evaluate_fitness(individual,current_environment)
				fitnesses.append(fitness)
				if fitness > highest_fitness: highest_fitness = fitness

			if highest_fitness>best_fitness: best_fitness = highest_fitness

			average_fitness = sum(fitnesses) / len(fitnesses)

			print("gen "+str(generation)+", highest = "+str(highest_fitness)+", avg = "+str(average_fitness)+", overall best = "+str(best_fitness),end="\r")
			sys.stdout.flush()

			if best_fitness==perfect_fitness: break

			pop = get_next_generation(pop,fitnesses,current_environment)

			generation+=1
			if generation>MAX_GENERATIONS: break

		print("\n",end="\r")


def main():
	d = data_t() # load data from all .cnf files
	train(d.var_20) # train on the 20 variable equations



if __name__ == '__main__':
	main()








