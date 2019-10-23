#####################################################################################
#
#
# 	Operator Converter for Airflow Transformation
#  
#	Author: Sam Showalter
#	Date: October 3, 2018
#
#####################################################################################


#####################################################################################
# External Library and Module Imports
#####################################################################################

# System and OS
import os
import sys

#Operator converter
import pandas as pd

#Time 
from datetime import datetime, timedelta

#String conversion for dictionaries
import json
import inspect

#####################################################################################
# Class and Constructor
#####################################################################################


def evaluation_operation(params, dag, **kwargs):

	ti = kwargs['ti']

	preds = ti.xcom_pull(task_ids = params['model_id'])
	y_test = ti.xcom_pull(key = 'y_test')

	return params['func'](y_test, preds, **params['params'])

def merge_metrics_operation(params, dag, context, **kwargs):

	ti = kwargs['ti']

	metrics_dict = {params['model']: {}}

	for task_id in params['merge_ids']:
		metric = ti.xcom_pull(task_ids = task_id)
		metrics_dict[params['model']][task_id] = metric
		
	return metrics_dict

def merge_data_operation(params, dag, context, **kwargs):

	ti = kwargs['ti']
	data = ti.xcom_pull(key = params['split'])

	persist_cols = []

	for task_id in params['merge_ids']:
		task_data = ti.xcom_pull(task_ids = task_id)

		if isinstance(task_data, pd.DataFrame):
			persist_cols += list(task_data.columns)
			data = pd.concat([data, task_data], axis = 1)
		elif isinstance(task_data, pd.Series):
			persist_cols.append(task_data.name)
			data[task_data.name] = task_data


	print()
	print(data.isnull().sum())
	print()

	#Only persist mentioned
	data = data.loc[:,persist_cols]

	ti.xcom_push(key = params['split'], value = data)

def bulk_data_operation(params, dag, **kwargs):
	ti = kwargs['ti']

	data = ti.xcom_pull(key = params['split'])

	if params['split'] == 'train':
		data = params['func'](data, **params['params'])

	elif params['split'] == 'test':
		train_artifacts = ti.xcom_pull(key = 'artifact', task_id = kwargs['task']\
																.task_id\
																.replace('test','train'))
		return params['func'](data, 
								**train_artifacts, 
								**params['params'])

	else:
		raise ValueError("Invalid data source: {}. Check your inputs".format(params['split']))
	
	#Push the data out using specific key
	ti.xcom_push(key = params['split'], value = data)


def col_data_operation(params, dag, **kwargs):
	ti = kwargs['ti']
	data = None

	#Get data based on inheritance or not
	#Data pulled in is either train or test slice
	if not params['inherits']:
		data = ti.xcom_pull(key = params['split'])
		data = data.loc[:, params['column_data_id']]
	else:
		data = ti.xcom_pull(task_ids = params['column_data_id']) 

	if params['split'] == 'train':
		return params['func'](data, **params['params'])

	elif params['split'] == 'test':
		train_artifacts = ti.xcom_pull(key = 'artifact', task_id = kwargs['task']\
																.task_id\
																.replace('test','train'))
		return params['func'](data, 
								**train_artifacts, 
								**params['params'])

	else:
		raise ValueError("Invalid data source: {}. Check your inputs".format(params['split']))
	

def fit_operation(params, dag, **kwargs):
	#if not _is_fitted(params['model']):
	ti = kwargs['ti']

	X_train = ti.xcom_pull(key = "X_train")
	y_train = ti.xcom_pull(key = "y_train")

	model = params['model'](**params['params'])
	model.fit(X_train, y_train)

	return model

def read_data_operation(params, dag, **kwargs):

	ti = kwargs['ti']

	data = params['func'](params['filepath'], **params['params'])

	ti.xcom_push(key = 'data', value = data)


def predict_operation(params, dag, **kwargs):
	ti = kwargs['ti']

	X_test = ti.xcom_pull(key = "X_test")

	model = ti.xcom_pull(task_ids = params['model'])
	
	predictions = model.predict(X_test)

	return predictions


def split_operation(params, dag, **kwargs):

	ti = kwargs['ti']

	data = ti.xcom_pull(key = 'data')

	train, test, target = params['func'](data, **params['params'])

	ti.xcom_push(key = 'train', value = train)
	ti.xcom_push(key = 'test', value = test)
	ti.xcom_push(key = 'target', value = target)
	ti.xcom_push(key = 'split_method', value = params['func'].__name__)

def model_split_operation(params, dag, **kwargs):
	"""
	splits model based on target later
	"""
	ti = kwargs['ti']

	train = ti.xcom_pull(key = 'train')
	test = ti.xcom_pull(key = 'test')
	target = ti.xcom_pull(key = 'target')

	X_train = train.loc[,train.columns != target]
	X_train = train.loc[,train.columns != target]

	ti.xcom_push(key = 'X_train', value = X_train)
	ti.xcom_push(key = 'y_train', value = y_train)
	ti.xcom_push(key = 'X_test', value = X_test)
	ti.xcom_push(key = 'y_test', value = y_test)

def k_fold_operation(func, params, dag, **kwargs):
	pass

def void_operation(func, params, dag, **kwargs):

	return func(data, **params)

def _is_fitted(model):
    """Checks if model object has any attributes ending with an underscore"""
    return 0 < len( [k for k,v in inspect.getmembers(model) 
    				if k.endswith('_') 
    				and not k.startswith('__')] )