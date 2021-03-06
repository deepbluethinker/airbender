#####################################################################################
#
#
# 	Test Script: DAG Input Error Handling
#  
#	Author: Sam Showalter
#	Date: October 6, 2018
#
#####################################################################################


#####################################################################################
# External Library and Module Imports
#####################################################################################

#Helper packages
import os
from itertools import chain
import sys
import copy

#Data packages
import pytest

#Airbender
import os
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, "../../")))
import airbender
from airbender.dag.generator import DagGenerator
from airbender.dag.layers import DagLayer

#####################################################################################
# Test Class: Meta Input Error Handling
#####################################################################################

class TestDAGMetaInputErrorHandling:
	airbender_config = { 
        'dag_name': "Airbender_Import_Tests",
        
        'dag':      {
                        'owner': 'airbender',
                    },
                    
        #DAG configuration we just created
        'config' : {}
    }

	@pytest.mark.parametrize("airbender_config", 
		                     [(airbender_config)], 
		                     ids = ["baseline"])
	@pytest.mark.usefixtures("obtain_correct_import_validation")
	def test_dag_owner_missing(self, obtain_correct_import_validation, airbender_config):

		with pytest.raises(AttributeError) as author_error:
			error_author_test = copy.deepcopy(airbender_config)
			del error_author_test['dag']['owner']
			obtain_correct_import_validation(error_author_test)

		assert "DAG Owner not specified. Please specify an author and try again."\
				 in str(author_error.value)

	@pytest.mark.parametrize("airbender_config", 
		                     [(airbender_config)], 
		                     ids = ["baseline"])
	@pytest.mark.usefixtures("obtain_correct_import_validation")
	def test_dag_name_missing(self, obtain_correct_import_validation, airbender_config):

		with pytest.raises(AttributeError) as author_error:
			error_author_test = copy.deepcopy(airbender_config)
			del error_author_test['dag_name']
			obtain_correct_import_validation(error_author_test)

		assert "DAG Name not specified. Please specify a dag name and try again."\
				 in str(author_error.value)

	@pytest.mark.parametrize("airbender_config", 
		                     [(airbender_config)], 
		                     ids = ["baseline"])
	@pytest.mark.usefixtures("obtain_correct_import_validation")
	def test_dag_config_missing(self, obtain_correct_import_validation, airbender_config):

		with pytest.raises(AttributeError) as author_error:
			error_author_test = copy.deepcopy(airbender_config)
			del error_author_test['config']
			obtain_correct_import_validation(error_author_test)

		assert "DAG Config not specified. Please specify a config and try again."\
				 in str(author_error.value)

#####################################################################################
# Test Class: Input Config Error Handling
#####################################################################################

class TestDAGMetaInputErrorHandling:
	pass