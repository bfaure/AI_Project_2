from __future__ import print_function # to allow for \r
import os
import sys

# class to hold all all information required about a .cnf file
class cnf_t(object):
	def __init__(self,filename):
		self.filename = filename
		self.clauses = []
		self.num_vars = -1
		self.read_file()

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
				if elems[-1]!="": self.num_vars = int(elems[-1])
				else: self.num_vars = int(elems[-2])
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

# class to handle loading/accessing of .cnf data
class data_t(object):

	# num_equations is the maximum number of .cnf files to parse per var ct level
	def __init__(self,num_equations=100):
		self.num_equations = num_equations # max num .cnf files per var level

		self.var_20 = [] # to hold all .cnf with 20 variables
		self.var_50 = [] # to hold all .cnf with 50 variables
		self.var_75 = [] # to hold all .cnf with 75 variables
		self.var_100 = [] # to hold all .cnf with 100 variables

		self.load_data() # load in up to num_equations .cnf files per var count level

	def load_data(self):
		print("Loading data...")

		parent_dir = "data/"
		child_dirs = ["20/","50/","75/","100/"]

		num_read_total = 0

		for d in child_dirs: # iterate over all data directories

			if d == "20/": cur_type = "var_20"
			if d == "50/": cur_type = "var_50"
			if d == "75/": cur_type = "var_75"
			if d == "100/": cur_type = "var_100"

			path = parent_dir+d
			items = os.listdir(path)

			for f in items:
				print("Reading... "+str(num_read_total),end="\r")

				if f.find(".cnf")!=-1:
					filename = path+f 
					cur = cnf_t(filename)
					self.__dict__[cur_type].append(cur) # add to appropriate member item
					num_read_total+=1
					
					if len(self.__dict__[cur_type])>=self.num_equations: break

		print("20 Variable Equations: "+str(len(self.var_20)))
		print("50 Variable Equations: "+str(len(self.var_50)))
		print("75 Variable Equations: "+str(len(self.var_75)))
		print("100 Variable Equations: "+str(len(self.var_100)))


def train(data,num_vars):
	pop = init_population(num_vars)



def main():
	d = data_t() # load data from all .cnf files



if __name__ == '__main__':
	main()








