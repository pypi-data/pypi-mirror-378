## Importing required Python packages
import numpy as np
import pandas as pd
import os, random, warnings

## Importing key functions from our gpal package.
## These three functions must be utilized to conduct GPAL properly.
from gpalexp import GPRInstance, gpal_optimize, argsConstructor
from gpalexp import sequence_with_interval

## Importing key functions from the psychopy package.
## Our number-line task file is implemented based on the psychopy package.
from psychopy import event, logging
## Importing functions for settings of number-line task, from nlt_setup.py file.
from nlt_setup import show_and_get_response, initialize_psychopy

## Managing default settings to ignore warning messages raised by psychopy.
warnings.filterwarnings('ignore')
logging.console.setLevel(logging.ERROR)


## Initializing visual elements for our number-line task code.
## initialize_psychopy(): setting up the psychopy visual elements.
## NOTE: The 'fullscreen mode' is turned off by default.
##       Users can turn on the fullscreen mode by setting fullscr=True.
visuals = initialize_psychopy(fullscr=False)



'''========================================== Step 0 =========================================='''

'''
Defining a Gaussian process regressor (GPR) object.
'''
## argsConstructor() is a function which generates values to create a GPR object.
## argsConsturctor() should take 3 values: num_kernels, kernel_type_list, kernel_arguments_list
## num_kernels indicate the number of kernel objects to be combined,
## which exactly corresponds to what n_kernel argument value represents.
## kernel_type_list should be a list object containing the types (or their indices) of kernel objects to be combined.
## It is already loaded in kernel_types, based on line 55 of this file.
## kernel_arguments_list should be a list object holding the values to be specified to properly create each kernel objects.
## We've loaded that list object in kernel_arguments in line 56.
## Therefore, we can use the argsConsturctor() function in the following way.

## argsConsturctor() has two outputs, which we've named kernel_type and kernel_args.
## We will soon exploit these outputs when generating a GPR object.
## NOTE: It is sufficient to write only the values we are putting to argsConsturctor(),
##       But for guidance, we've specified both the values that argsConstructor() should take
##       and those we've loaded and putting into the function. 
kernel_type, kernel_args = argsConstructor([0,6,8], [[2.5], [1.0], [0.01]])


'''
Initializing a kernel object and a GPR with the kernel.
'''
## For GPAL, we need to create a GPR object.
## In this package, GPRInstance() function takes the role.

## GPRInstance() takes 7 values, but the last one is optional and need not to be specified.
## kernel_types should have a list object holding the types of each kernel objects to be combined,
## which we've just created with argsConstructor() and named kernel_type.
## Therefore, we can just provide kernel_type for kernel_types value.
## Similarly, it is sufficient to provide kernel_args for kernel_arguments value.

## combine_format should be a string object, which specifies the way those individual kernel objects are combined.
## In combine_format, we represent each kernel object as k1, k2, k3, and so on.
## For example, if we have 3 kernels and we want to multiply the first two ones and add the last one,
## we can just feed "k1*k2+k3" as combine_format.

## For alpha, n_restarts_optimizer, normalize_y, and random_state, 
## it is recommended to put the default values, which are automatically fed into.

## There are two outputs, which we've named kernel and gpr.
## kernel is a Gaussian process kernel object created following our specifications.
## gpr is a GPR object associated with that kernel object.
combine_format = "k1*k2+k3"
kernel, gpr = GPRInstance(kernel_type, kernel_args, combine_format)

''' =================================== Step 1 ========================================='''

num_trials=20           # Number of experiment trials for a single subject.
num_features=1          # The number of stimulus feautres to be optimized.

''' 
Initializing a numpy array for recording. 
'''
## The number-line task of our interest is a 1-dimensional task,
## where the 'given number' may vary but 'upper bound' stays still.
## In other words, we have a single stimulus feature, which is the 'given number'.
## We will create a numpy array for recording the experiment results.
## The first row will record the 'given number' for each trial,
## and the second row is for recording the subject's estimation on the 'given number'. 
## This record array will be updated after each trial.
## NOTE: The number of columns of record_array is set to num_features+1. 
##       Here num_features is the number of stimulus features to be optimized.
##       This enables us to record multiple stimulus features and user responses, 
#        in a single data structure, even for arbitrary number of stimulus features.
##       The first num_features columns will record value of each stimulus features,
##       and the last column will record the subject's responses.
data_record = np.zeros((20, 2))   


''' 
Defining the number-line task-specific values. 
'''
## 1-dimensional number-line task has a constant 'upper bound' value.
## We've set it to 500, and named it 'max_number'
## to refer to the upper bound value with the name of 'max_number' in the following codes.
max_number = 500


## In our number-line task, there are two types of trials.
## One is a 'fixed-sized' trial, where the size of the presented dots remains a default value.
## The other is a 'variable-sized' trial, where the size of the dots may vary.
## size_control_order determines the order of fixed-size trials and variable-sized ones randomly.
dot_size_flags = [True] * (num_trials//2) + [False] * (num_trials//2)
size_control_order = random.sample(dot_size_flags, num_trials)


'''
Running the first trial.
'''
## This code block is for running the first trial.
## Since we cannot optimize the stimulus feature (i.e. 'given number') in the first trial,
## we just set it as a random number among (5, 10, 15, ... , 495, 500)
## pMean, pStd, lml are GPAL-related statistics, which cannot be calculated in the first trial.
## Therefore we've just initialized them with simple values.
stimulus_list=sequence_with_interval(5, 500, 5)

trial_index=0
initial_stimulus=np.random.choice(stimulus_list, size=1)
gp_mean = 0
gp_std = 1
lml = 0


## Show the dots and get response from participant
## If size_control is True, the function internally adjusts the size of the dots.
## Otherwise, the default-sized dots are provided.
response = show_and_get_response(initial_stimulus, 
                                 visuals, 
                                 max_number, 
                                 size_control_order[0])

'''
Recording the results for the next trial
'''
## The 0-th row records the selected value of the stimulus feature, namely the 'given number' of the number-line task. 
## The 1-th row records the response of the subject for the given_number.
data_record[trial_index,0] = initial_stimulus
data_record[trial_index,1] = response

## Waiting for the user to press the space key, to move on to the next trial
event.waitKeys(keyList=['space'])  


''' Running experimental trials with GPAL. '''
## We will run the following block n_trials times, with trial_idx representing the index of the currently running trial.
for trial_index in range(1, num_trials):

    ## This code block is executed otherwise (i.e. for the second to the last trial).
    ## gpal_optimize() function actually executes GPAL optimization
    ## and yields an optimal feature for the next trial
    ## as well as some GPAL-related statistics.
    ## NOTE: The stimulus feature to be optimized here is the 'given number' of the number-line task.
    
    
    ## Executing the gpal_optimize() function with appropriate input values.
    optimal_design, pMean, pStd, lml = gpal_optimize(gpr,                                  # A GP regressor object to be fitted.
                                                     num_features,                         # Number of feature stimulus to be optimized
                                                     data_record[:trial_index],            # The feature stimulus data for fitting the GP regressor
                                                     stimuli                               # Overall specifications on the design candidate values.
                                                    )                  
    given_number = int(optimal_design)                                                     # Extracting the optimal 'given number' value for the next trial.


    # Show the dots and get response from participant
    # If size_control is enabled, adjust the dot size, else use default size
    response = show_and_get_response(given_number, visuals, max_number=max_number, size_control=size_control_order[trial_index])

    '''
    Recording the results for the next trial
    '''
    ## The 0-th row records the selected value of the stimulus feature, namely the 'given number' of the number-line task. 
    ## The 1-th row records the response of the subject for the given_number.
    data_record[trial_index,0] = given_number
    data_record[trial_index,1] = response

    ## Waiting for the user to press the space key, to move on to the next trial
    event.waitKeys(keyList=['space'])  

'''
Saving experiment results in the .csv format
'''
save_results_dir='results'
if not os.path.exists(save_results_dir):
    os.mkdir(save_results_dir)
results_df = pd.DataFrame(data_record, columns=['given_number', 'response'])
results_df.to_csv(os.path.join(save_results_dir, f'results_trial_{num_trials}.csv'), index=False)

## Closing the psychopy experiment window.
visuals['win'].close() 