import sys
import random
import math
import glob
import os

def main():
    random.seed(0)
    gentype = sys.argv[1]
    
    if gentype == 'industrial_train':
        random.seed(42)
        for i in range(1, 31):
            generate_instance(3, range(5, 50), 'L', str(i))
        for i in range(31, 61):
            generate_instance(3, range(5, 50), 'H', str(i))
        for i in range(61, 91):
            generate_instance(5, range(10, 50), 'L', str(i))
        for i in range(91, 121):
            generate_instance(5, range(10, 50), 'H', str(i))
        for i in range(121, 151):
            generate_instance(10, range(50, 200), 'L', str(i))
        for i in range(151, 181):
            generate_instance(10, range(50, 200), 'H', str(i))
        for i in range(181, 211):
            generate_instance(15, range(100, 200), 'L', str(i))
        for i in range(211, 241):
            generate_instance(15, range(100, 200), 'H', str(i))
        for i in range(241, 271):
            generate_instance(20, range(150, 200), 'L', str(i))
        for i in range(271, 301):
            generate_instance(20, range(150, 200), 'H', str(i))	
    elif gentype == 'industrial_test':
        random.seed(44)
        generate_instance(3, range(5, 50), 'L', str(1))
        generate_instance(3, range(5, 50), 'H', str(2))
        generate_instance(5, range(10, 50), 'L', str(3))
        generate_instance(5, range(10, 50), 'H', str(4))
        generate_instance(10, range(50, 200), 'L', str(5))
        generate_instance(10, range(50, 200), 'H', str(6))
        generate_instance(15, range(100, 200), 'L', str(7))
        generate_instance(15, range(100, 200), 'H', str(8))
        generate_instance(20, range(150, 200), 'L', str(9))
        generate_instance(20, range(150, 200), 'H', str(10))	
    elif gentype == 'simple':
        random.seed(45)
        for i in range(1, 5):
            generate_instance(random.randrange(2, 4), range(18, 25), 'L', str(i), minSetupTime=0, maxSetupTime=5, minReleaseDate=0, minDuration=1, maxDuration=3)
        for i in range(5, 10):
            generate_instance(random.randrange(2, 4), range(18, 25), 'H', str(i), minSetupTime=0, maxSetupTime=5, minReleaseDate=0, minDuration=1, maxDuration=3)
    else:
        print('gentype parameter missing or not valid!', file=sys.stderr)
        sys.exit(1)


def build_fact(name, *args):
    return '{}({}).'.format(name, ','.join(str(arg).lower() for arg in args))


def generate_instance(nMachines, jobRange, instanceType, instanceName, directory='./', minSetupTime=0, maxSetupTime=100, minReleaseDate=0, minDuration=10, maxDuration=500):

    if not instanceType in ['L', 'H']:
        raise Exception('instanceType should be L or H. The value was: {}'.format(instanceType))

    nJobs = random.choice(jobRange)

    capableMachines = {}
    durations = {}
    releaseDates = {}
    setupTimes = {}

    eightyPercentJobs = random.sample(range(0, nJobs), int(math.ceil(0.8 * nJobs)))
    twentyPercentMachines = random.sample(range(0, nMachines), int(math.ceil(0.2 * nMachines)))

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
        avgSetup = round(avgSetup / (1 if nSetups == 0 else nSetups))
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


    filename = instanceName + '_%i_%i_%c.lp' % (nMachines, nJobs, instanceType)
    with open(os.path.join(directory, filename), "w") as asp_file:
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

    return filename
    

if __name__ == "__main__":
    main()
