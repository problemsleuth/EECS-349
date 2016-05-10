from __future__ import division
import math
from node import Node
import sys
from collections import Counter
from math import log

def ID3(data_set, attribute_metadata, numerical_splits_count, depth):
	'''
	See Textbook for algorithm.
	Make sure to handle unknown values, some suggested approaches were
	given in lecture.
	========================================================================================================
	Input:  A data_set, attribute_metadata, maximum number of splits to consider for numerical attributes,
	maximum depth to search to (depth = 0 indicates that this node should output a label)
	========================================================================================================
	Output: The node representing the decision tree learned over the given data set
	========================================================================================================

	'''
	
	root = Node()
	root.label = None 
	
	# if examples is empty, return default (0 I guess?)
	if (len(data_set) == 0):
		root.label = 0
		return root
	# if examples are all classified the same, return that classification 
	elif (check_homogenous(data_set) != None):
		root.label = check_homogenous(data_set)
		return root
	# if we have no attributes or if we've reached the maximum depth, return mode of the examples
	elif (len(data_set[0]) < 2) or (depth <= 0):
		root.label = mode(data_set)
		return root
	# otherwise, perform the entire algorithm 
	else:
		# get the best attribute 
		attribute = pick_best_attribute(data_set, attribute_metadata, numerical_splits_count)
		
		# if we can't get any more information by splitting, just set the mode as the label 
		if (attribute[0] == False):
			root.label = mode(data_set)
			return root 
		
		# read the data into node
		root.is_nominal = attribute_metadata[attribute[0]]['is_nominal'] 
		root.decision_attribute = attribute[0] 
		root.name = attribute_metadata[attribute[0]]['name']
		
		# next step depends on whether attribute is nominal 
		if (root.is_nominal):
			# if the attribute we're splitting on is nominal, create a dictionary with all possibilities 
			root.children = {} 
			
			# get possible values 
			values = split_on_nominal(data_set, root.decision_attribute)
			
			for key in values.keys():
				depth -= 1 
				root.children[key] = ID3(values[key], attribute_metadata, numerical_splits_count, depth)
		else:
			# if the attribute we're splitting on is numeric, we know the best split from pick_best_attribute
			root.splitting_value = attribute[1]
			
			# now split the data properly
			values = split_on_numerical(data_set, root.decision_attribute, root.splitting_value)
			
			# now create the two children
			root.children = []
			numerical_splits_count[root.decision_attribute] -= 1 
			depth -= 1
			root.children.append(ID3(values[0], attribute_metadata, numerical_splits_count, depth))
			root.children.append(ID3(values[1], attribute_metadata, numerical_splits_count, depth))
	
	return root

def check_homogenous(data_set):
	'''
	========================================================================================================
	Input:  A data_set
	========================================================================================================
	Job:    Checks if the output value (index 0) is the same for all examples in the the data_set, if so return that output value, otherwise return None.
	========================================================================================================
	Output: Return either the homogenous attribute or None
	========================================================================================================
	 '''
	
	output = data_set[0][0]
	
	for value in data_set:
		if output != value[0]:
			return None
	
	return output
	
# ======== Test Cases =============================
# data_set = [[0],[1],[1],[1],[1],[1]]
# check_homogenous(data_set) ==  None
# data_set = [[0],[1],[None],[0]]
# check_homogenous(data_set) ==  None
# data_set = [[1],[1],[1],[1],[1],[1]]
# check_homogenous(data_set) ==  1

def pick_best_attribute(data_set, attribute_metadata, numerical_splits_count):
	'''
	========================================================================================================
	Input:  A data_set, attribute_metadata, splits counts for numeric
	========================================================================================================
	Job:    Find the attribute that maximizes the gain ratio. If attribute is numeric return best split value.
			If nominal, then split value is False.
			If gain ratio of all the attributes is 0, then return False, False
			Only consider numeric splits for which numerical_splits_count is greater than zero
	========================================================================================================
	Output: best attribute, split value if numeric
	========================================================================================================
	'''
    
	best_attribute = -1 
	split_value = -1 
	
	# loop through non-winner attributes
	index = 1 
	best_ratio = 0 
	while (index < len(attribute_metadata)):
		# check whether the attribute is nominal or numeric
		if (attribute_metadata[index]['is_nominal'] == False):
			# data is numeric
			
			# make sure we're allowed to split on this attribute
			if numerical_splits_count[index] != 0:
				new_values = gain_ratio_numeric(data_set, index, 1000)
				
				if new_values[0] > best_ratio:
					best_ratio = new_values[0]
					best_attribute = index
					split_value = new_values[1]
		else:
			# data is nominal
			new_ratio = gain_ratio_nominal(data_set, index)
			
			if new_ratio > best_ratio:
				best_ratio = new_ratio
				best_attribute = index
				split_value = -1
		
		index += 1 
				
	# if we have a split_value, return it, otherwise return false
	if (best_attribute == -1):
		return (False, False)
	elif (split_value == -1):
		return (best_attribute, False)
	else:
		return (best_attribute, split_value)
			

# # ======== Test Cases =============================
# numerical_splits_count = [20,20]
# attribute_metadata = [{'name': "winner",'is_nominal': True},{'name': "opprundifferential",'is_nominal': False}]
# data_set = [[1, 0.27], [0, 0.42], [0, 0.86], [0, 0.68], [0, 0.04], [1, 0.01], [1, 0.33], [1, 0.42], [0, 0.51], [1, 0.4]]
# pick_best_attribute(data_set, attribute_metadata, numerical_splits_count) == (1, 0.51)
# attribute_metadata = [{'name': "winner",'is_nominal': True},{'name': "weather",'is_nominal': True}]
# data_set = [[0, 0], [1, 0], [0, 2], [0, 2], [0, 3], [1, 1], [0, 4], [0, 2], [1, 2], [1, 5]]
# pick_best_attribute(data_set, attribute_metadata, numerical_splits_count) == (1, False)

# Uses gain_ratio_nominal or gain_ratio_numeric to calculate gain ratio.

def mode(data_set):
	'''
	========================================================================================================
	Input:  A data_set
	========================================================================================================
	Job:    Takes a data_set and finds mode of index 0.
	========================================================================================================
	Output: mode of index 0.
	========================================================================================================
	'''
    
	c = Counter()
	
	for item in data_set:
		c[item[0]] += 1 
		
	return c.most_common(1)[0][0]
		
# ======== Test case =============================
# data_set = [[0],[1],[1],[1],[1],[1]]
# mode(data_set) == 1
# data_set = [[0],[1],[0],[0]]
# mode(data_set) == 0

def entropy(data_set):
	'''
	========================================================================================================
	Input:  A data_set
	========================================================================================================
	Job:    Calculates the entropy of the attribute at the 0th index, the value we want to predict.
	========================================================================================================
	Output: Returns entropy. See Textbook for formula
	========================================================================================================
	'''
	
	c = Counter()
	
	for item in data_set:
		c[item[0]] += 1 
		
	total = sum(c.values())
	
	to_return = 0
	
	for tup in c.most_common():
		to_return += (tup[1]/total) * log((tup[1]/total), 2)
		
	return -to_return

# ======== Test case =============================
# data_set = [[0],[1],[1],[1],[0],[1],[1],[1]]
# entropy(data_set) == 0.811
# data_set = [[0],[0],[1],[1],[0],[1],[1],[0]]
# entropy(data_set) == 1.0
# data_set = [[0],[0],[0],[0],[0],[0],[0],[0]]
# entropy(data_set) == 0


def gain_ratio_nominal(data_set, attribute):
	'''
	========================================================================================================
	Input:  Subset of data_set, index for a nominal attribute
	========================================================================================================
	Job:    Finds the gain ratio of a nominal attribute in relation to the variable we are training on.
	========================================================================================================
	Output: Returns gain_ratio. See https://en.wikipedia.org/wiki/Information_gain_ratio
	========================================================================================================
	'''
	
	ent = entropy(data_set)
	
	# calculate information gain
	sets = []
	total = 0 
	
	# split list
	for item in data_set:
		appended = False
		for s in sets:
			if (item[attribute] == s[0][attribute]):
				s.append(item)
				appended = True
		if appended == False:
			sets.append([item])
		total += 1 
	
	# for each sub-list, calculate fractional entropy and subtract it from total
	info_gain = ent
	
	for item in sets:
		info_gain -= ((len(item)/total)  * entropy(item))
	
	
	# calculate intrinsic value
	int_value = 0
	
	for item in sets:
		int_value -= ((len(item)/total) * log(len(item)/total, 2))
		
	# return ratio
	if (int_value == 0):
		return 0
	return (info_gain/int_value)
# ======== Test case =============================
# data_set, attr = [[1, 2], [1, 0], [1, 0], [0, 2], [0, 2], [0, 0], [1, 3], [0, 4], [0, 3], [1, 1]], 1
# gain_ratio_nominal(data_set,attr) == 0.11470666361703151
# data_set, attr = [[1, 2], [1, 2], [0, 4], [0, 0], [0, 1], [0, 3], [0, 0], [0, 0], [0, 4], [0, 2]], 1
# gain_ratio_nominal(data_set,attr) == 0.2056423328155741
# data_set, attr = [[0, 3], [0, 3], [0, 3], [0, 4], [0, 4], [0, 4], [0, 0], [0, 2], [1, 4], [0, 4]], 1
# gain_ratio_nominal(data_set,attr) == 0.06409559743967516

def gain_ratio_numeric(data_set, attribute, steps):
	'''
	========================================================================================================
	Input:  Subset of data set, the index for a numeric attribute, and a step size for normalizing the data.
	========================================================================================================
	Job:    Calculate the gain_ratio_numeric and find the best single threshold value
			The threshold will be used to split examples into two sets
				 those with attribute value GREATER THAN OR EQUAL TO threshold
				 those with attribute value LESS THAN threshold
			Use the equation here: https://en.wikipedia.org/wiki/Information_gain_ratio
			And restrict your search for possible thresholds to examples with array index mod(step) == 0
	========================================================================================================
	Output: This function returns the gain ratio and threshold value
	========================================================================================================
	'''
	# get total entropy 
	ent = entropy(data_set)
	
	# try multiple different splits
	split_index = 0 
	best_threshold = 0
	best_ratio = 0
	
	while (split_index < len(data_set)):
		new_split = split_on_numerical(data_set, attribute, data_set[split_index][attribute])
		
		if (len(new_split[0]) != 0 and len(new_split[1]) != 0):
			# calculate information gain 
			total = len(new_split[0]) + len(new_split[1])
			info_gain = ent - ((len(new_split[0])/total) * entropy(new_split[0])) - (((len(new_split[1])/total)) * entropy(new_split[1]))
			
			# calculate intrinsic value 
			int_value = - ((len(new_split[0])/total) * log(len(new_split[0])/total, 2)) - ((len(new_split[1])/total) * log(len(new_split[1])/total, 2))
			
			# calculate ratio
			new_ratio = info_gain / int_value
		else:
			new_ratio = 0 
		
		# see if this ratio is better
		if new_ratio > best_ratio:
			best_ratio = new_ratio
			best_threshold = data_set[split_index][attribute]
			
		split_index += steps
	
	return (best_ratio, best_threshold)
	
# ======== Test case =============================
# data_set,attr,step = [[0,0.05], [1,0.17], [1,0.64], [0,0.38], [0,0.19], [1,0.68], [1,0.69], [1,0.17], [1,0.4], [0,0.53]], 1, 2
# gain_ratio_numeric(data_set,attr,step) == (0.31918053332474033, 0.64)
# data_set,attr,step = [[1, 0.35], [1, 0.24], [0, 0.67], [0, 0.36], [1, 0.94], [1, 0.4], [1, 0.15], [0, 0.1], [1, 0.61], [1, 0.17]], 1, 4
# gain_ratio_numeric(data_set,attr,step) == (0.11689800358692547, 0.94)
# data_set,attr,step = [[1, 0.1], [0, 0.29], [1, 0.03], [0, 0.47], [1, 0.25], [1, 0.12], [1, 0.67], [1, 0.73], [1, 0.85], [1, 0.25]], 1, 1
# gain_ratio_numeric(data_set,attr,step) == (0.23645279766002802, 0.29)

def split_on_nominal(data_set, attribute):
	'''
	========================================================================================================
	Input:  subset of data set, the index for a nominal attribute.
	========================================================================================================
	Job:    Creates a dictionary of all values of the attribute.
	========================================================================================================
	Output: Dictionary of all values pointing to a list of all the data with that attribute
	========================================================================================================
	'''
	
	d = {}
	
	for item in data_set:
		if item[attribute] not in d:
			d[item[attribute]] = [item]
		else:
			d[item[attribute]].append(item)
			
	return d
	
# ======== Test case =============================
# data_set, attr = [[0, 4], [1, 3], [1, 2], [0, 0], [0, 0], [0, 4], [1, 4], [0, 2], [1, 2], [0, 1]], 1
# split_on_nominal(data_set, attr) == {0: [[0, 0], [0, 0]], 1: [[0, 1]], 2: [[1, 2], [0, 2], [1, 2]], 3: [[1, 3]], 4: [[0, 4], [0, 4], [1, 4]]}
# data_set, attr = [[1, 2], [1, 0], [0, 0], [1, 3], [0, 2], [0, 3], [0, 4], [0, 4], [1, 2], [0, 1]], 1
# split on_nominal(data_set, attr) == {0: [[1, 0], [0, 0]], 1: [[0, 1]], 2: [[1, 2], [0, 2], [1, 2]], 3: [[1, 3], [0, 3]], 4: [[0, 4], [0, 4]]}

def split_on_numerical(data_set, attribute, splitting_value):
	'''
	========================================================================================================
	Input:  Subset of data set, the index for a numeric attribute, threshold (splitting) value
	========================================================================================================
	Job:    Splits data_set into a tuple of two lists, the first list contains the examples where the given
	attribute has value less than the splitting value, the second list contains the other examples
	========================================================================================================
	Output: Tuple of two lists as described above
	========================================================================================================
	'''
	
	less_than = []
	greater_than = []
	
	for item in data_set:
		if (item[attribute] < splitting_value):
			less_than.append(item)
		else:
			greater_than.append(item)
			
	return (less_than, greater_than)
		
# ======== Test case =============================
# d_set,a,sval = [[1, 0.25], [1, 0.89], [0, 0.93], [0, 0.48], [1, 0.19], [1, 0.49], [0, 0.6], [0, 0.6], [1, 0.34], [1, 0.19]],1,0.48
# split_on_numerical(d_set,a,sval) == ([[1, 0.25], [1, 0.19], [1, 0.34], [1, 0.19]],[[1, 0.89], [0, 0.93], [0, 0.48], [1, 0.49], [0, 0.6], [0, 0.6]])
# d_set,a,sval = [[0, 0.91], [0, 0.84], [1, 0.82], [1, 0.07], [0, 0.82],[0, 0.59], [0, 0.87], [0, 0.17], [1, 0.05], [1, 0.76]],1,0.17
# split_on_numerical(d_set,a,sval) == ([[1, 0.07], [1, 0.05]],[[0, 0.91],[0, 0.84], [1, 0.82], [0, 0.82], [0, 0.59], [0, 0.87], [0, 0.17], [1, 0.76]]))