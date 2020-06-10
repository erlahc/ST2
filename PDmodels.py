import numpy as np
import pandas as pd

class Model1:
	def __init__(self,pd_init=0.05,
					coef=[2,2],
					macro={'gdp':{'baseline':[0.1,0.15,0.2],'adverse':[0.1,0.15,0.2]},
							'unemployment':{'baseline':[0.1,0.15,0.2],'adverse':[0.1,0.15,0.2]}}):
		self.pd_init=pd_init
		self.macro=macro
		self.coef=coef
		self.horizon=len(self.macro['gdp']['baseline'])

		self.formula=self.get_formula()
		self.projection=self.get_projected()



	def get_formula(self):
		formula='PD(t)=PD(t-1) + {} * GDP(t) + {} * Unemployment(t)'
		return formula.format(self.coef[0],self.coef[1])

	def projection(self,pd,macro):
		pd=pd+self.coef[0]*macro[0]+self.coef[1]*macro[1]
		return pd

	def get_projected(self):
		baseline=[]
		adverse=[]
		for i in range(self.horizon):
			if i ==0:
				baseline.append(self.projection(self.pd_init,
												[self.macro['gdp']['baseline'][i],
												self.macro['unemployment']['baseline'][i]]))
				adverse.append(self.projection(self.pd_init,
												[self.macro['gdp']['adverse'][i],
												self.macro['unemployment']['adverse'][i]]))
			else:
				baseline.append(self.projection(baseline[i-1],
												[self.macro['gdp']['baseline'][i],
												self.macro['unemployment']['baseline'][i]]))
				adverse.append(self.projection(adverse[i-1],
												[self.macro['gdp']['adverse'][i],
												self.macro['unemployment']['adverse'][i]]))
		return [baseline,adverse]

class PDModel2_global:
	def __init__(self,coef=[1.0,1.0],macro_lib=['gdp','unemployment']):
		self.coef=coef
		self.macro_lib=macro_lib
		self.formula=self.get_formula()

	def get_formula(self):
		formula='PD(t)={} * GDP(t) + {} * Unemployment(t)'
		return formula.format(self.coef[0],self.coef[1])

class PDModel2(PDModel2_global):
	#Model de projection de PD sans AR à partir de GDP et du chomage
	def __init__(self,country,entity,segment,coef=[1.0,1.0],macro=[[-0.1,-0.2,-0.3],[0.4,0.7,0.9]]):
		super().__init__(coef)
		self.country=country
		self.entity=entity
		self.segment=segment

		self.macro=macro
		self.horizon=len(self.macro[0])

		self.df_macro=self.set_df_macro()
		self.pd_projected=self.projection()

	def projection(self):
		pdp=np.array(self.coef[0]).astype(float)*np.array(self.macro[0]).astype(float)+np.array(self.coef[1]).astype(float)*np.array(self.macro[1]).astype(float)
		return pdp

	def set_df_macro(self):
		df_macro=pd.DataFrame({self.macro_lib[0]:self.macro[0],
							   self.macro_lib[1	]:self.macro[1]})
		return df_macro

if __name__=='__main__':
	Model1(0.05)
