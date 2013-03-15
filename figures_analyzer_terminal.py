import sys
import random
import glob
import math

global connectedPerm, minOverlap, window_size, overlapping, len_side, columns, desiredLocalActivity, permanenceInc, permanenceDec, sliding_average, boostInc, iterations

#_______________ initial variables


window_size=5
overlapping=2
len_side=20
connectedPerm=0.3
minOverlap=3
desiredLocalActivity=3
permanenceInc=0.1
permanenceDec=0.025
sliding_average=10
boostInc=0.05
iterations=25

#_____________internal variables

folders=[]
for i in range(1, len(sys.argv)):
	folders.append(sys.argv[i])
	
columns=[]

#_______________ functions

def get_matrix(filename):
	matrix=[]
	f=open(filename, "r")
	for line in f:
		line=line.strip()
		a=line.split()
		matrix.append(a)
	return matrix
	
def read_matrix(x1, x2 ,y1, y2, count, matrix):
	k=count
	l=0
	sum_overlap=0
	for i in range(x1, x2):
		for j in range(y1, y2):
			columns[k].synapses[l].activation_state=int(matrix[i][j])
			if (columns[k].synapses[l].connected_state() and columns[k].synapses[l].activation_state):
				sum_overlap+=1
				#print columns[k].synapses[l].activation_state
			l+=1	
	columns[k].overlap=sum_overlap
	#print columns[k].overlap
	

def new_input(matrix):
	count=0
	for i in range(0,len(matrix[0]), window_size-overlapping):
		for j in range(0, len(matrix), window_size-overlapping):
			try:
				endx=i+window_size
				endy=j+window_size
				#print i,endx,j,endy 
				read_matrix(i, endx, j, endy, count, matrix)
				#name="column"+str(i)+str(j)
				count+=1
			except:
				pass
			
def create_columns():
	n=int(((len_side-overlapping)/(window_size-overlapping))**2)
	for i in range (0, n):
		name="column"+str(i)
		name=column(name)
		columns.append(name)

def check_column_activation():
	for column in columns:
		column.activation_state()
		#print column.overlap,

def make_inhibition():
	activeColumns=[]
	inhibitedColumns=[]
	notActivatedColumns=[]
	for i in range(0, len(columns)):
		column=columns[i]
		neighbors=get_neighbors(i)
		sorted_list = sorted(neighbors, key=lambda x: x.overlap, reverse=True)
		minLocalActivity=sorted_list[desiredLocalActivity-1].overlap
		if column.overlap > 0 and column.overlap >= minLocalActivity:
			activeColumns.append(column)
		if column.overlap > 0 and column.overlap <= minLocalActivity:
			inhibitedColumns.append(column)
		if column.overlap ==0:
			notActivatedColumns.append(column)
	
	return (activeColumns, inhibitedColumns, notActivatedColumns)

def get_neighbors(i):
	i=int(i)
	neighbors=[]
	n=int(((len_side-overlapping)/(window_size-overlapping)))
	if i-n>=0:
		neighbors.append(columns[i-n])
	if (i+1)-n>=0 and ((i+1)%n) !=0:
		neighbors.append(columns[i-n+1])
	if (i-1)-n>=0 and ((i)%n) !=0:
		neighbors.append(columns[i-n-1])
	if i+n<n**2:
		neighbors.append(columns[i+n])
	if (i-1)+n<n**2 and ((i)%n) !=0:
		neighbors.append(columns[i+n-1])
	if (i+1)+n<n**2 and ((i+1)%n) !=0:
		neighbors.append(columns[i+n+1])
	if ((i+1)%n) !=0:
		neighbors.append(columns[i+1])
	if ((i)%n) !=0:
		neighbors.append(columns[i-1])
	return neighbors

def update_permanence(activeColumns):
	for column in activeColumns:
		for i in range(0, len(column.synapses)):
			if column.synapses[i].activation_state == 1:
				#print column.synapses[i].perm
				column.synapses[i].perm+=permanenceInc
				#print column.synapses[i].perm
				if column.synapses[i].perm > 1:
					column.synapses[i].perm=1
			else:
				column.synapses[i].perm-=permanenceDec
				if column.synapses[i].perm < 0:
					column.synapses[i].perm=0


def update_duty(activeColumns, inhibitedColumns, notActivatedColumns):

	for column in activeColumns:
		column.activeDutyCycle.append(1.)
	for column in inhibitedColumns:
		column.activeDutyCycle.append(0.)
	for column in notActivatedColumns:
		column.activeDutyCycle.append(0.)	
	
	if len(columns[0].activeDutyCycle)==sliding_average:
		for i in range(0, len(columns)):
			neighbors=get_neighbors(i)
			maxDutyCycle=0
			for neighbor in neighbors:
				average=sum(neighbor.activeDutyCycle)/sliding_average
				if average>maxDutyCycle:
					maxDutyCycle=float(average)
			minDutyCycle=maxDutyCycle*0.01
			ownAverage=sum(columns[i].activeDutyCycle)/sliding_average
			if ownAverage<minDutyCycle:
				columns[i].boost+=boostInc
		for column in columns:
			column.activeDutyCycle.pop(0)	
			
def update_activity_state(activeColumns, inhibitedColumns, notActiveColumns, folder):
	for column in activeColumns:
		column.activity_state=1
		column.folder+=1
	for column in inhibitedColumns:
		column.activity_state=2
	for column in notActiveColumns:
		column.activity_state=0

def print_activity_state(display):
	'''Display must have 1 to display inhibitions and 0 not to display inhibitions'''
	n=int(((len_side-overlapping)/(window_size-overlapping)))
	if display==1:
		for i in range(0, n):
			for j in range(i, len(columns), n):
				output=0
				if columns[j].activity_state==2:
					output=0
				if columns[j].activity_state==1:
					output=1
				print output,
			print ""
	else:
		for i in range(0, n):
			for j in range(i, len(columns), n):
				print columns[j].activity_state,
			print ""

def compute_frecuencies(folder):
	for column in columns:
		one_frecuency=(float(column.folder)+1)/(iterations+1)
		zero_frecuency=1-one_frecuency
		if zero_frecuency==0:
			zero_frecuency=float(1)/(5*iterations+1)
		one_frecuency=math.log(one_frecuency)
		zero_frecuency=math.log(zero_frecuency)
		column.figures_hash[folder]=[zero_frecuency, one_frecuency]	
		#print column.figures_hash

def guess_figure():
	probabilities={}
	total_prob=0
	max_prob=""
	#print columns[0].figures_hash

	for figure in sorted(columns[0].figures_hash.iterkeys()):
		for column in columns:
			activation=column.activity_state
			if activation ==2:
				activation=0
			total_prob=total_prob+column.figures_hash[figure][activation]
	
		probabilities[figure]=total_prob
		total_prob=0

	print "_______________SCORES__________________"
	print ""
	for key in probabilities:
		print key+":\t"+str(probabilities[key])	
	
	best_figure=""
	prob_sum=0
	print ""
	print "______________RECOGNITION______________"
	print ""
	for figure in sorted(columns[0].figures_hash.iterkeys()):
		prob_sum+=float(math.e**(probabilities[figure]))
		if not max_prob:
			max_prob=probabilities[figure]
		if probabilities[figure]>=max_prob:
			max_prob=probabilities[figure]
			best_figure=figure	
	#print math.e**max_prob
	#print prob_sum
	n=int(((len_side-overlapping)/(window_size-overlapping))**2)
	percent_prob= ((math.e**max_prob)/prob_sum)*100
	threshold_of_randomness=(math.log(0.5**n))/2
	if (max_prob > threshold_of_randomness):
		print "Recognition: "+best_figure#+" with a conditionated probability of "+str(percent_prob)+"%"
	else:
		print "Recognition: No figure has been recognized"	
	print ""	

#____________________classes

class synapse:
	def __init__(self, column):
		self.column=column
		self.connectedPerm=connectedPerm
		self.perm=random.uniform(connectedPerm-0.05,connectedPerm+0.05)
		self.activation_state=0

	def connected_state(self):
		if self.perm > self.connectedPerm:
			c_state=1
	
		else:
			c_state=0
		return c_state


class column:
	"""Cell column class"""
	def __init__(self, name):
		self.name=name
		self.overlap=0
		self.minOverlap=minOverlap
		self.boost=1
		self.activeDutyCycle=[]
		self.synapses=[]
		self.activity_state=0
		self.figures_hash={}
		for i in range(0,window_size**2):
			nombre="Synapse"+str(i)
			nombre=synapse(self)
			self.synapses.append(nombre)
	def activation_state(self):
		if self.overlap < self.minOverlap:
			self.overlap = 0
		else:
			self.overlap=self.overlap*self.boost


#_____________________ MAIN

create_columns()

count=0
for folder in folders:
	images=[]
	images=glob.glob('./'+str(folder)+'/*')
	#print images
	for column in columns:
		column.folder=0
	matrixes=[]
	for image in images:
		matrix=get_matrix(image)
		matrixes.append(matrix)
	x=0
	for i in range (0, iterations):
		print "Cycle "+str(count)+" "+images[x]
		new_input(matrixes[x])
		check_column_activation()
		activeColumns, inhibitedColumns, notActiveColumns=make_inhibition()
		update_activity_state(activeColumns, inhibitedColumns, notActiveColumns, folder)
		print_activity_state(2)
		#print ""
		#print_activity_state(1)
		update_permanence(activeColumns)
		update_duty(activeColumns, inhibitedColumns, notActiveColumns)
	
		x+=1
		count+=1
		if x>=(len(matrixes)):
			x=0
	compute_frecuencies(folder)

query=raw_input(">Enter matrix to evaluate: ")
print ""
matrix=get_matrix(query)
new_input(matrix)
check_column_activation()
activeColumns, inhibitedColumns, notActiveColumns=make_inhibition()
update_activity_state(activeColumns, inhibitedColumns, notActiveColumns, folder)
#print_activity_state(2)	
guess_figure()
