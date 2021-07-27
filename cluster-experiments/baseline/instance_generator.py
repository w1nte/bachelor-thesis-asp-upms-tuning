
import random
import math
import glob

def build_fact(name, *args):
    return '%(name)s(%(args)s).' % {
            'name': name,
            'args': ','.join(str(arg).lower() for arg in args),
        }

def generate_instance(nMachines, jobRange, instanceType, instanceName):

	if not instanceType in ['L', 'H']:
		raise Exception('instanceType should be L or H. The value was: {}'.format(instanceType))

	nJobs = random.choice(jobRange)
	minSetupTime = 0
	maxSetupTime = 100
	minReleaseDate = 0
	minDuration = 10
	maxDuration = 500

	capableMachines = {}
	durations = {}
	releaseDates = {}
	setupTimes = {}

	eightyPercentJobs = random.sample(range(0, nJobs), math.ceil(0.8 * nJobs))
	twentyPercentMachines = random.sample(range(0, nMachines), math.ceil(0.2 * nMachines))

	for j in range(0, nJobs):
		if instanceType == 'L' or not j in eightyPercentJobs:
			n = random.randint(1, nMachines)
			capableMachines[j] = random.sample(range(0, nMachines), n)
		else:
			n = random.randint(1, len(twentyPercentMachines))
			capableMachines[j] = random.sample(twentyPercentMachines, n)
	
		for m in range(0, nMachines):
			durations[(j,m)] = random.randint(minDuration, maxDuration)

			for k in range(0, nJobs):
				if j == k:
					setupTimes[(k,j,m)] = 0
				else:
					setupTimes[(k,j,m)] = random.randint(0, maxSetupTime)
	maxReleaseDate = 0
	for j in range(0, nJobs):
		avgDuration = 0
		avgSetup = 0
		nSetups = 0
		for m in capableMachines[j]:
			avgDuration += durations[(j,m)]
			for k in range(1, nJobs):
				if m in capableMachines[k]:
					avgSetup += setupTimes[(k,j,m)]
					nSetups += 1
		
		avgDuration = round(avgDuration / len(capableMachines[j]))
		avgSetup = round(avgSetup / nSetups)
		maxReleaseDate += avgDuration + avgSetup
	
	maxReleaseDate = int(maxReleaseDate / nMachines)	

	for j in range(0, nJobs):
		for m in range(0, nMachines):
			releaseDates[(j,m)] = random.randint(minReleaseDate, maxReleaseDate)
			

	horizon = 0
	for m in range(0, nMachines):
		maxRelease = 0
		for j in range(0, nJobs):
			if m in capableMachines[j] and releaseDates[(j,m)] > maxRelease:
				maxRelease = releaseDates[(j,m)]
		
		load = 0
		for j in range(0, nJobs):
			if m in capableMachines[j]:
				load += durations[(j,m)]
				setup = 0
				for k in range(0, nJobs):
					if m in capableMachines[k] and setupTimes[(k,j,m)] > setup:
						setup = setupTimes[(k,j,m)] 
					
				load += setup
			
		if horizon < maxRelease + load:
			horizon = maxRelease + load	


	with open(instanceName + '_%i_%i_%c.lp' % (nMachines, nJobs, instanceType), "w") as asp_file:
		facts = []

		for j in range(1, nJobs + 1):
			facts += [ build_fact('job', 'j' + str(j)) ]
    
		for m in range(1, nMachines + 1):
			facts += [ build_fact('machine', 'm' + str(m)) ]   
	
		for j in range(0, nJobs):
			for k in range(0, nJobs):
				if j != k:
					for m in range(0, nMachines):
						facts += [ build_fact('setup', 'j' + str(j + 1),
								      'j' + str(k + 1), 
								      'm' + str(m + 1), setupTimes[(j,k,m)]) ]
 
		for j in range(0, nJobs):
			for m in range(0, nMachines):                                          
				facts += [ build_fact('duration', 'j' + str(j + 1), 'm' + str(m + 1), durations[(j,m)]) ]
				facts += [ build_fact('release', 'j' + str(j + 1), 'm' + str(m + 1), releaseDates[(j,m)]) ]
				if m in capableMachines[j]:
					facts += [ build_fact('capable', 'm' + str(m + 1), 'j' + str(j + 1)) ]
				
		facts += [ build_fact('horizon', str(horizon)) ]			
            
		asp_file.write(''.join(facts))            



def main():

	random.seed(6840578295)
	
	for i in range(1, 51):
		generate_instance(3, range(5, 50), 'L', str(i))
		
	for i in range(51, 101):
		generate_instance(3, range(5, 50), 'H', str(i))
		
	for i in range(101, 151):
		generate_instance(5, range(10, 50), 'L', str(i))
		
	for i in range(151, 201):
		generate_instance(5, range(10, 50), 'H', str(i))
		
	for i in range(201, 251):
		generate_instance(10, range(50, 200), 'L', str(i))
		
	for i in range(251, 301):
		generate_instance(10, range(50, 200), 'H', str(i))
		
	for i in range(301, 351):
		generate_instance(15, range(100, 200), 'L', str(i))
		
	for i in range(351, 401):
		generate_instance(15, range(100, 200), 'H', str(i))
		
	for i in range(401, 451):
		generate_instance(20, range(150, 200), 'L', str(i))
		
	for i in range(451, 501):
		generate_instance(20, range(150, 200), 'H', str(i))	
        
	



if __name__ == "__main__":
	main()
