#####################################################################################
#
#
# 	Custom ML Airflow Feature Engineering
#  
#	Author: Sam Showalter
#	Date: October 6, 2018
#
#####################################################################################


#####################################################################################
# External Library and Module Imports
#####################################################################################

#Helper packages
from itertools import chain
import sys
import copy

#Data packages
import pytest

#Airbender
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../")))
import airbender
from airbender.dag.generator import DagGenerator
from airbender.dag.layers import DagLayer


#####################################################################################
# Test Class: Dynamic Import Validation
#####################################################################################

class TestDynamicImportCompleteness:

	## Imports for TestDynamicImportCompleteness
	import pandas as pd
	from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score
	from sklearn.linear_model import LogisticRegression
	from sklearn.ensemble import RandomForestClassifier
	from sklearn.svm import SVC
	from airbender.static.feature_engineering import normalize_values, winsorize, encode_labels
	from airbender.static.preprocessing import impute
	from airbender.static.splitting import train_test_split

	data_sources = {'iris':         #Tag
   		DagLayer(
            {
             'https://raw.githubusercontent.com/SamShowalter/WMP_training/master/airbender_iris_demo.csv': \
             {pd.read_csv: {'sep': ','}},
            }
           )
               }

	splitting = {'split':

	                DagLayer({'sklearn': {train_test_split: {"target": "flower_label",
	                                                        "test_ratio": 0.25,
	                                                        "random_state": 42}
	                                     }
	                        })
	            }

	preprocessing = {'missing_data':

	                        DagLayer({
	                                    # tag name             # Operator Family
	                                    'median_impute':       {impute: {'method': 'median'}}
	                                })
	            }


	feature_engineering = {'cols': 

                        DagLayer({
                                    # Column name             # Operator Family

                                    'sepal_width':            {normalize_values: None},
                                    'sepal_length':           None,
                                    'petal_length':           {winsorize:            {'limits': [0.05, 0.05]},
                                                               normalize_values:     None},
                                    #Pass-through
                                    'petal_width':            None,
                                    'flower_label':           {encode_labels: None}
                                })
                        }

	modeling = {'modeling': 
	            
	            DagLayer({
	                        'LOG': {LogisticRegression:         {'solver':'lbfgs'}},           
	                        'RF':  {RandomForestClassifier:     {'n_estimators': 10}},
	                        'SVM': {SVC:                        {'kernel': 'linear'}}
	                    })  
	       }


	evaluation = {'metrics':
	                
	                 DagLayer({
	                            'acc':            {accuracy_score: None},
	                            'recall':         {precision_score: {'average': 'weighted'}},
	                            'precision':      {recall_score: {'average': 'weighted'}},
	                            'f1':             {f1_score: {'average': 'weighted'}}
	                         })
	         }

	input_config = {
	            'data_sources':            data_sources,
	            'splitting':               splitting,
	            'preprocessing':           preprocessing,
	            'feature_engineering':     feature_engineering,
	            'modeling':                modeling,
	            'evaluation':              evaluation
	          }


	correct_imports = set({'from airbender.static.feature_engineering import encode_labels\n',
						 'from airbender.static.feature_engineering import normalize_values\n',
						 'from airbender.static.feature_engineering import winsorize\n',
						 'from airbender.static.preprocessing import impute\n',
						 'from airbender.static.splitting import train_test_split\n',
						 'from pandas.io.parsers import read_csv\n',
						 'from sklearn.ensemble.forest import RandomForestClassifier\n',
						 'from sklearn.linear_model.logistic import LogisticRegression\n',
						 'from sklearn.metrics.classification import accuracy_score\n',
						 'from sklearn.metrics.classification import f1_score\n',
						 'from sklearn.metrics.classification import precision_score\n',
						 'from sklearn.metrics.classification import recall_score\n',
						 'from sklearn.svm.classes import SVC\n'})

	

	@pytest.mark.parametrize("input_config,correct_imports", 
		                     [(input_config,correct_imports)], 
		                     ids = ["baseline"])
	@pytest.mark.usefixtures("obtain_correct_import_validation")
	def test_import_completeness(self, obtain_correct_import_validation, 
								 input_config, correct_imports):
		airbender_config = { 
                'dag_name': "Airbender_Import_Tests",
                
                'dag':      {
                                'owner': 'airbender',
                            },
                            
                #DAG configuration we just created
                'config' : input_config
           }

		assert obtain_correct_import_validation(airbender_config) ==\
			   correct_imports

		# #Wrap in a set object
		# input_config['feature_engineering']['cols'] = {input_config['feature_engineering']['cols']}

		# assert obtain_correct_import_validation(airbender_config) ==\
		# 	   correct_imports

		# #Add nested list to configuration
		# input_config['feature_engineering']['cols'] = [[[input_config['feature_engineering']['cols']]]]

		# assert obtain_correct_import_validation(airbender_config) ==\
		# 	   correct_imports

		#Add nested dictionaries
		input_config['feature_engineering']['cols'] = {1:
														{2: 
						input_config['feature_engineering']['cols']}}
		



class TestDynamicPartialImportCompleteness:

	## Imports for TestDynamicImportCompleteness
	import pandas as pd
	from sklearn.metrics import precision_score
	from sklearn.metrics import f1_score as abc
	from sklearn.metrics import recall_score, accuracy_score, f1_score
	from sklearn.linear_model import LogisticRegression
	from sklearn.ensemble import RandomForestClassifier
	from sklearn import svm
	from airbender.static.feature_engineering import normalize_values as norm_vals
	from airbender.static.feature_engineering import normalize_values, winsorize, encode_labels
	from airbender.static.preprocessing import impute
	from airbender.static.splitting import train_test_split

	data_sources = {'iris':         #Tag
   		DagLayer(
            {
             'https://raw.githubusercontent.com/SamShowalter/WMP_training/master/airbender_iris_demo.csv': \
             {pd.read_csv: {'sep': ','}},
            }
           )
               }

	splitting = {'split':

	                DagLayer({'sklearn': {train_test_split: {"target": "flower_label",
	                                                        "test_ratio": 0.25,
	                                                        "random_state": 42}
	                                     }
	                        })
	            }

	preprocessing = {'missing_data':

	                        DagLayer({
	                                    # tag name             # Operator Family
	                                    'median_impute':       {impute: {'method': 'median'}}
	                                })
	            }


	feature_engineering = {'cols': 

                        DagLayer({
                                    # Column name             # Operator Family

                                    'sepal_width':            {norm_vals: None},
                                    'sepal_length':           None,
                                    'petal_length':           {winsorize:            {'limits': [0.05, 0.05]},
                                                               normalize_values:     None},
                                    #Pass-through
                                    'petal_width':            None,
                                    'flower_label':           {encode_labels: None}
                                })
                        }

	modeling = {'modeling': 
	            
	            DagLayer({
	                        'LOG': {LogisticRegression:         {'solver':'lbfgs'}},           
	                        'RF':  {RandomForestClassifier:     {'n_estimators': 10}},
	                        'SVM': {svm.SVC:                        {'kernel': 'linear'}}
	                    })  
	       }


	evaluation = {'metrics':
	                
	                 DagLayer({
	                            'acc':            {accuracy_score: None},
	                            'recall':         {precision_score: {'average': 'weighted'}},
	                            'precision':      {recall_score: {'average': 'weighted'}},
	                            'f1':             {abc: {'average': 'weighted'}}
	                         })
	         }

	input_config = {
	            'data_sources':            data_sources,
	            'splitting':               splitting,
	            'preprocessing':           preprocessing,
	            'feature_engineering':     feature_engineering,
	            'modeling':                modeling,
	            'evaluation':              evaluation
	          }


	correct_imports = set({'from airbender.static.feature_engineering import encode_labels\n',
						 'from airbender.static.feature_engineering import normalize_values\n',
						 'from airbender.static.feature_engineering import winsorize\n',
						 'from airbender.static.preprocessing import impute\n',
						 'from airbender.static.splitting import train_test_split\n',
						 'from pandas.io.parsers import read_csv\n',
						 'from sklearn.ensemble.forest import RandomForestClassifier\n',
						 'from sklearn.linear_model.logistic import LogisticRegression\n',
						 'from sklearn.metrics.classification import accuracy_score\n',
						 'from sklearn.metrics.classification import f1_score\n',
						 'from sklearn.metrics.classification import precision_score\n',
						 'from sklearn.metrics.classification import recall_score\n',
						 'from sklearn.svm.classes import SVC\n'}) 	


	@pytest.mark.parametrize("input_config,correct_imports", 
		                     [(input_config,correct_imports)], 
		                     ids = ["baseline"])
	@pytest.mark.usefixtures("obtain_correct_import_validation")
	def test_partial_import_completeness(self, obtain_correct_import_validation, 
								 input_config, correct_imports):
		airbender_config = { 
                'dag_name': "Airbender_Import_Tests",
                
                'dag':      {
                                'owner': 'airbender',
                            },
                            
                #DAG configuration we just created
                'config' : input_config
           }

		assert obtain_correct_import_validation(airbender_config) ==\
			   correct_imports

		#Wrap in a set object
		input_config['feature_engineering']['cols'] = {input_config['feature_engineering']['cols']}

		