import pandas as pd
import numpy as np

class ProjectedData:
	def __init__(self, path):
		self.df=pd.read_csv(path,delimiter=';',decimal='.')
		self.dropdown=self.get_dropdown()

	def get_dropdown(self):
		tmp=self.df.loc[:,['country','entity','segment']].drop_duplicates()
		return tmp

class ModelData:
	def __init__(self,path):
		self.df=pd.read_csv('model.csv',delimiter=';',decimal='.')

if __name__=='__main__':
	path='data.csv'
	df=ProjectedData(path)