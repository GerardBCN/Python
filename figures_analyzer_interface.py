# figures_analizer.py - makes figure recognition through an HTM Cortical Learning Algorithm and a Bayesian analysis.
# NOTE 1: To run this tool you will need to have the following module installed: easygui.			
# NOTE 2: before to start you need to have as many directories as kind of images to learn, each one called with the kind of image name.			
# usage: python figures_analizer.
# copyright 2013 Adria Aterido Ballonga, Gerard Martinez Rossell and Bernardo Rodriguez Martin this software is distributed under the same terms as python.




###----------------------------------------------------------LOADING MODULES-----------------------------------------------------------------###
import sys
import random
import glob
import math
import easygui as eg

###------------------------------------------------------DEFINING GLOBAL VARIABLES-----------------------------------------------------------###
global connectedPerm, minOverlap, window_size, overlapping, len_side, columns, desiredLocalActivity, permanenceInc, permanenceDec, sliding_average, boostInc, learning_cycle


###-----------------------------LOADING FOLDERS WITH IMAGES TO LEARN AND PART 1 OF THE GRAPHICAL INTERFACE-----------------------------------###
folders=[]
columns=[]

eg.msgbox("FIGURE ANALYZER makes figure predictions\nthrough an HTM Cortical Learning Algorithm  \nand a Bayesian analysis.", title="FIGURE ANALYZER")
eg.msgbox("You must follow the next steps carefully in order to get a good prediction:\n\nSTEP 1: Choose the number of learning cycles.\nSTEP 2: Choose directories of learning files.\nSTEP 3: Choose your query figure.\nSTEP 4: Display the ouput you like the most.\n\n\nNOTE: Before to start you need to have as many directories as kind of images to learn, each one called with the kind of image name.", title="FIGURE ANALYZER")
reply1=eg.integerbox(msg='How many learning cicles do you want to carry out?', title='STEP 1', default='', lowerbound=0, upperbound=500)
reply=eg.integerbox(msg='How many shapes are you going to use for learning?', title='STEP 2', default='', lowerbound=0, upperbound=10)

for i in range (0,int(reply)):
	directory=eg.diropenbox(msg=None, title="STEP 2: First learning files directory", default=None)
	folders.append(directory)

choices1=["Yes","No"]
choice1=eg.choicebox("FIGURE ANALYZER has learned.\nDo you want to start the analysis?","START ANALYSIS", choices1)

if choice1=='Yes':
	query=eg.fileopenbox(msg="Introduce your query figure:", title="STEP 2", default='*', filetypes=None)

	choices=["\nImage recognition","\nResults file"]
	choice=eg.choicebox('Which output would you like to display?','STEP 3', choices)

	if choice == "\nResults file":
		a=eg.filesavebox(msg="Save matrices with activated, non-activated and inhibited matrices", title="STEP 4", default="FA_resultsfile.txt")		
		a=a.split("/")
		saving_name=a[len(a)-1]

												
	
	if choice == "\nResults file":
		output_file= open(saving_name, "w")
		output_file.write("This file contains the sparse distributed representation generated as an output by the HTM algorithm after processing input image. Two matrixes are shown for each kind of training figure and for each learning cycle: \n\tA) Matrix with active (1) and not activated columns(0).\n\tB) Matrix with active (1), inhibited (2)  and not activated columns(0).\n\n")


###------------------------------------------------------SETTING WORKING CONTITION------------------------------------------------------------###
window_size=5
overlapping=2
len_side=20
connectedPerm=0.3
minOverlap=3
desiredLocalActivity=3
permanenceInc=0.1
permanenceDec=0.025
sliding_average=100
boostInc=0.05
learning_cycle=int(reply1)

###-------------------------------------------------------------SUBROUTINES-------------------------------------------------------------------###

## == SUBROUTINE 1. BUILDS COLUMN OBJECTS UNTILL THE WHOLE IMAGE AREA IS COVERED  == ##			
def create_columns():
	n=int(((len_side-overlapping)/(window_size-overlapping))**2)
	for i in range (0, n):
		name="column"+str(i)
		name=column(name)									
		columns.append(name)


## == SUBROUTINE 2. READS AN IMAGE FROM A TEXT FILE AND STORE THE IMAGE INTO A MATRIX == ##
def get_matrix(filename):
	matrix=[]
	f=open(filename, "r")
	for line in f:
		line=line.strip()
		a=line.split()
		matrix.append(a)
	return matrix
	

## == SUBROUTINE 3. SPLITS THE MATRIX INTO SUBMATRIXES EACH ONE CORRESPONDING TO THE RECEPTORY FIELD OF A COLUMN == ##
def new_input(matrix):
	count=0
	for i in range(0,len(matrix[0]), window_size-overlapping):
		for j in range(0, len(matrix), window_size-overlapping):
			try:
				endx=i+window_size
				endy=j+window_size
				read_matrix(i, endx, j, endy, count, matrix)				# CALLING FUNCTION 4
				count+=1
			except:
				pass


## == SUBROUTINE 4. COMPUTES THE OVERLAP OF EACH COLUMN IN ITS CONRRESPONDING RECEPTORY FIELD AND REDIFINES THE OVERLAP ATRIBUTE OF COLUMNS == ##
def read_matrix(x1, x2 ,y1, y2, count, matrix):
	k=count
	l=0
	sum_overlap=0
	for i in range(x1, x2):
		for j in range(y1, y2):
			columns[k].synapses[l].activation_state=int(matrix[i][j])
			if (columns[k].synapses[l].connected_state() and columns[k].synapses[l].activation_state):
				sum_overlap+=1
			l+=1	
	columns[k].overlap=sum_overlap


## == SUBROUTINE 5. SET THE ACTIVATION STATE OF EACH COLUMN ACCORDING ITS OVERLAP == ##
def check_column_activation():
	for column in columns:
		column.activation_state()


## == SUBROUTINE 6. COMPUTES THE STATE OF EACH COLUMN AFTER THE INHIBITION PROCESS. THREE POSSIBLE STATES: ACTIVE, INHIBITED AND NOT ACTIVATED == ##
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


## == SUBROUTINE 7. REDEFINES THE ACTIVY STATE FOR EACH COLUMN ACORDING TO THE STATES PREVIOUSLY COMPUTED IN THE FUNCTION 6 == ##
def update_activity_state(activeColumns, inhibitedColumns, notActiveColumns, folder):
	for column in activeColumns:
		column.activity_state=1
		column.folder+=1
	for column in inhibitedColumns:
		column.activity_state=2
	for column in notActiveColumns:
		column.activity_state=0


## == SUBROUTINE 8. DISPLAYS INTO THE TERMINAL TWO KIND OF MATRIXES: A) MATRIX 1. CONTAINS ACTIVE AND NOT ACTIVATED COLUMNS            == ##
#								     B) MATRIX 2. CONTAINS ACTIVE, INHIBITED AND NOT ACTIVATED COLUMNS 
def print_activity_state(display,output_file):
	'''Display must have 1 to display inhibitions and 0 not to display inhibitions'''
	n=int(((len_side-overlapping)/(window_size-overlapping)))
	if display==1:
		output_file.write("\n")
		for i in range(0, n):
			for j in range(i, len(columns), n):
				output=0
				if columns[j].activity_state==2:
					output=0
				if columns[j].activity_state==1:
					output=1
				output_file.write(str(output))
			output_file.write("\n")
		output_file.write("\n")
	else:
		for i in range(0, n):
			for j in range(i, len(columns), n):
				output_file.write(str(columns[j].activity_state))
			output_file.write("\n")
		output_file.write("\n")

## == SUBROUTINE 9. UPDATES THE PERMANCENCE VALUE OF EACH SYNAPSE. == ##
def update_permanence(activeColumns):
	for column in activeColumns:
		for i in range(0, len(column.synapses)):
			if column.synapses[i].activation_state == 1:
				column.synapses[i].perm+=permanenceInc
				if column.synapses[i].perm > 1:
					column.synapses[i].perm=1
			else:
				column.synapses[i].perm-=permanenceDec
				if column.synapses[i].perm < 0:
					column.synapses[i].perm=0


## == SUBROUTINE 10. COMPUTES A MOVING AVERAGE OF HOW OFTEN EACH COLUMN HAS BEEN ACTIVE AFTER INHIBITION == ##
def update_duty(activeColumns, inhibitedColumns, notActivatedColumns):
	for column in activeColumns:
		column.activeDutyCycle.append(1.)
	for column in inhibitedColumns:
		column.activeDutyCycle.append(0.)
	for column in notActivatedColumns:
		column.activeDutyCycle.append(0.)	
	if len(columns[0].activeDutyCycle)==sliding_average:
		for i in range(0, len(columns)):
			neighbors=get_neighbors(i)							# CALLING FUNCTION 11
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


## == SUBROUTINE 11. GET THE NEIGHBOURS COLUMNS TO EACH COLUMN == ##
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



## == SUBROUTINE 12. COMPUTE THE FREQUENCE OF EACH COLUMN TO BE ACTIVATED AND NON ACTIVATED == ##
def compute_frecuencies(folder):
	for column in columns:
		one_frecuency=(float(column.folder)+1)/(learning_cycle+1)
		zero_frecuency=1-one_frecuency
		if zero_frecuency==0:
			zero_frecuency=float(1)/(5*learning_cycle+1)
		one_frecuency=math.log(one_frecuency)
		zero_frecuency=math.log(zero_frecuency)
		column.figures_hash[folder]=[zero_frecuency, one_frecuency]	


## == SUBROUTINE 13. PERFORMS A BAYESIAN ANALYSIS TO PREDICT WHAT KIND OF FIGURE IS THE QUERY IMAGE == ##
def guess_figure():
	global output	
	probabilities={}
	absolute_freq=0
	max_prob=""
	
	#-Compute for each column the number of times that it is activated throught the learning cycles-#
	for figure in sorted(columns[0].figures_hash.iterkeys()):
		for column in columns:
			activation=column.activity_state
			if activation ==2:
				activation=0
			absolute_freq=absolute_freq+column.figures_hash[figure][activation]
	
		probabilities[figure]=absolute_freq
		absolute_freq=0
	output=[]	
	for key in probabilities:
		key1=key
		key=key.split("/")
		key=key[len(key)-1]
		output.append(str(key)+":\t")
		output.append(str(probabilities[key1])+"\n")	
	
	#-Find the most probable shape for the query picture-#
	best_figure=""
	prob_sum=0
	for figure in sorted(columns[0].figures_hash.iterkeys()):
		prob_sum+=float(math.e**(probabilities[figure]))
		if not max_prob:
			max_prob=probabilities[figure]
		if probabilities[figure]>=max_prob:
			max_prob=probabilities[figure]
			best_figure=str(figure)
			best_figure=best_figure.split("/")
			best_figure=best_figure[len(best_figure)-1]
	n=int(((len_side-overlapping)/(window_size-overlapping))**2)
	percent_prob= ((math.e**max_prob)/prob_sum)*100
	threshold_of_randomness=(math.log(0.5**n))/2
	if (max_prob > threshold_of_randomness):
		print_guessed=str("The best guess is that the figure is a "+best_figure)#+" with a conditionated probability of "+str(percent_prob)+"%"
	else:
		print_guessed= str("No good prediction has been done")			
	
	output.append(print_guessed)

###---------------------------------------------------------CLASSES-----------------------------------------------------------###

## == CLASS 1. SYNAPSE CLASS == ##
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


## == CLASS 2. COLUMN CLASS == ##
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


###----------------------------------------------------CORE OF THE PROGRAM-------------------------------------------------------###

create_columns()											# CALLING FUNCTION 1. Builds column objects
count=0

## == ITERATE TAKING ONE OF THE INPUT FOLDERS IN EACH ITERATION == ##
for folder in folders:											
	images=[]
	images=glob.glob(folder+"/*")									# Loads the name of each image file inside the folder and save 
	images2=[]											# it into an array
	for i in images:										
		i=i.split("/")
		image=i[len(i)-1]
		images2.append(image)

	for column in columns:
		column.folder=0
	matrixes=[]
	for image in images:										# Builds matrixes to store the information of each image 
		matrix=get_matrix(image)								# CALLING FUNCTION 2. Reads the image and store it into a matrix
		matrixes.append(matrix)
	x=0
	cycle_counter=0
	for i in range (0, learning_cycle):
		if choice == "\nResults file":								
			output_file.write("Learning cycle "+str(cycle_counter)+" "+images2[x]+"\n")		
		new_input(matrixes[x])									# CALLING FUNCTION 4. Gets the receptory fields of each column 																      and its overlap value
		check_column_activation()								# CALLING FUNCTION 5. Sets the activation state of each column 																      according its overlap
		activeColumns, inhibitedColumns, notActiveColumns=make_inhibition()			# CALLING FUNCTION 6. Computes the active, inhibited and active 														              columns after inhibition
		update_activity_state(activeColumns, inhibitedColumns, notActiveColumns, folder) 	# CALLING FUNCTION 7. Redifines the activity state of each column
		if choice == "\nResults file":								
			print_activity_state(1,output_file)						# CALLING FUNCTION 8. Saves matrix 1 into a file
			print_activity_state(2,output_file)						# CALLING FUNCTION 8. Saves matrix 2 into the same file
		
		update_permanence(activeColumns)							# CALLING FUNCTION 9. Uptates the permanence value of the 														synapses
		update_duty(activeColumns, inhibitedColumns, notActiveColumns)				# CALLING FUNCTION 10. Updates duty value of each column.  												       
		x+=1
		if x>=(len(matrixes)):									
			x=0
			cycle_counter+=1

	compute_frecuencies(folder)									# CALLING FUNCTION 12. Computing the weight matrix with the pro 
	matrix=get_matrix(query) 									# probabilities of each column to be active or not active
	new_input(matrix)
	check_column_activation()
	activeColumns, inhibitedColumns, notActiveColumns=make_inhibition()
	update_activity_state(activeColumns, inhibitedColumns, notActiveColumns, folder)
	
	#-Figure recognition-#											 
	guess_figure()											# CALLING FUNCTION 13. Performs the Bayesian analysis to predict 														# what is the most likely shape for the query image
												
## == PART 2 OF THE GRAPHICAL INTERFACE == ##
if choice == "\nImage recognition":									# Displays into the graphical interface the results of the 														  Bayesian analysis
     eg.textbox("Recognition results:", "STEP 4", output)

if choice == "\nResults file":										# Closes filehandle after saving the results into 
	output_file.close()

