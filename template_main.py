# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
from database import ProjectedData,ModelData
from PDmodels import *
import ast

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

projected_data=ProjectedData('data.csv')
models_data=ModelData('model.csv')

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True 

app.layout = html.Div(children=[
				
				# empty Div to trigger javascript file for graph resizing
				html.Div(id="output-clientside"),

				html.Div([
					html.Div([
						dcc.Dropdown(id='dd-countries',
									options=[{'label': i, 'value': i} for i in list(projected_data.get_dropdown()['country'].unique())],
									value=list(projected_data.get_dropdown()['country'].unique())[0]),
						dcc.Dropdown(id='dd-entities'),
						dcc.Dropdown(id='dd-segments'),
						dcc.Dropdown(id='dd-models')
					],className='two columns'),
					html.Div([
						html.H5('<to be replaced by model formula>',id='txt-formula'),
						html.H5('Baseline'),
						dcc.Loading(children=html.Div(id='container-model-macro-baseline')),
						html.H5('Adverse'),
						dcc.Loading(children=html.Div(id='container-model-macro-adverse'))
					],className='six columns'),
					html.Div([
						dcc.Graph(id='graph-impact-pd')
					],className='four columns')
				],className="row flex-display"),

				html.Div([
					html.Div([
						dcc.Graph(id='graph-impact-outstanding')
					],className='six columns'),
					html.Div([
						dcc.Graph(id='graph-impact-provision')
					],className='six columns')
				],className="row flex-display"),

				html.Div([
					html.Div([
						dcc.Graph(id='graph-matrix-base-1')
					],className='four columns'),
					html.Div([
						dcc.Graph(id='graph-matrix-base-2')
					],className='four columns'),
					html.Div([
						dcc.Graph(id='graph-matrix-base-3')
					],className='four columns')
				],className='row flex-display'),

				html.Div([
					html.Div([
						dcc.Graph(id='graph-matrix-adverse-1')
					],className='four columns'),
					html.Div([
						dcc.Graph(id='graph-matrix-adverse-2')
					],className='four columns'),
					html.Div([
						dcc.Graph(id='graph-matrix-adverse-3')
					],className='four columns')
				],className='row flex-display')
			])

#callback dropdowns
@app.callback(
	Output('dd-entities', 'options'),
	[Input('dd-countries', 'value')])
def set_entities_options(selected_country):
	tmp=projected_data.dropdown
	tmp1=list(tmp[tmp['country']==selected_country]['entity'].unique())
	return [{'label': i, 'value': i} for i in tmp1]

@app.callback(
	Output('dd-entities', 'value'),
	[Input('dd-entities', 'options')])
def set_entities_value(available_options):
	return available_options[0]['value']

@app.callback(
	Output('dd-segments', 'options'),
	[Input('dd-entities', 'value')],
	[State('dd-countries', 'value')])
def set_segments_options(selected_entity,selected_country):
	tmp=projected_data.dropdown
	tmp1=list(tmp[(tmp['country']==selected_country)&(tmp['entity']==selected_entity)]['segment'].unique())
	return [{'label': i, 'value': i} for i in tmp1]

@app.callback(
	Output('dd-segments', 'value'),
	[Input('dd-segments', 'options')])
def set_segments_value(available_options):
	return available_options[0]['value']

#callback dropdowns for the models
@app.callback(
	Output('dd-models', 'options'),
	[Input('dd-segments', 'value')],
	[State('dd-countries', 'value'),
	State('dd-entities', 'value')])
def set_models_options(selected_segment,selected_country,selected_entity):
	tmp=models_data.df
	tmp1=list(tmp[(tmp['country']==selected_country)&(tmp['entity']==selected_entity)&(tmp['segment']==selected_segment)]['modelID'])
	tmp1.append('Standard')
	return [{'label': i, 'value': i} for i in tmp1]

@app.callback(
	Output('dd-models', 'value'),
	[Input('dd-models', 'options')])
def set_segments_value(available_options):
	return available_options[0]['value']

#Afficher la formule du modèle utilisé
@app.callback(
	Output('txt-formula', 'children'),
	[Input('dd-models', 'value')],
	[State('dd-countries', 'value'),
	State('dd-entities', 'value'),
	State('dd-segments', 'value')])
def set_segments_value(selected_model,selected_country,selected_entity,selected_segment):
	if selected_model=='Standard':
		tmp='CF benchmark'
	else:
		df_tmp=models_data.df
		try:
			df_tmp=list(df_tmp[(df_tmp['country']==selected_country)&(df_tmp['entity']==selected_entity)&(df_tmp['segment']==selected_segment)]['coef'])[0]
			coef=ast.literal_eval(df_tmp)
			tmp=globals()[selected_model+'_global'](coef)
		except:
			tmp=globals()[selected_model+'_global']()
		tmp=tmp.formula
	return tmp

#Afficher la table des paramètres macroeconomiques baseline
@app.callback(
	Output('container-model-macro-baseline', 'children'),
	[Input('dd-models', 'value')],
	[State('dd-countries', 'value'),
	State('dd-entities', 'value'),
	State('dd-segments', 'value')])
def set_macro_table_baseline(selected_model,selected_country,selected_entity,selected_segment):
	if selected_model!='Standard':
		model=globals()[selected_model](country=selected_country,entity=selected_entity,segment=selected_segment)
		dfm=model.df_macro
	else:
		dfm=pd.DataFrame({'pd':[1.0,1.0,1.0]})
	
	dt=dash_table.DataTable(
			id='table-model-macro-baseline',
			columns=[{"name": i, "id": i} for i in dfm.columns],
			data=dfm.to_dict('records'),
			editable=True)
	return dt

#Afficher la table des paramètres macroeconomiques adverse
@app.callback(
	Output('container-model-macro-adverse', 'children'),
	[Input('dd-models', 'value')],
	[State('dd-countries', 'value'),
	State('dd-entities', 'value'),
	State('dd-segments', 'value')])
def set_macro_table_adverse(selected_model,selected_country,selected_entity,selected_segment):
	if selected_model!='Standard':
		model=globals()[selected_model](country=selected_country,entity=selected_entity,segment=selected_segment)
		dfm=model.df_macro
	else:
		dfm=pd.DataFrame({'pd':[1.15,1.15,1.15]})
	
	dt=dash_table.DataTable(
			id='table-model-macro-adverse',
			columns=[{"name": i, "id": i} for i in dfm.columns],
			data=dfm.to_dict('records'),
			editable=True)
	return dt

#Afficher la graphe des projections de PD
@app.callback(
	Output('graph-impact-pd', 'figure'),
	[Input('table-model-macro-baseline', 'data'),
	Input('table-model-macro-adverse', 'data')],
	[State('dd-models', 'value'),
	State('dd-countries', 'value'),
	State('dd-entities', 'value'),
	State('dd-segments', 'value')])
def set_pd_projection(rows_baseline,rows_adverse,selected_model,selected_country,selected_entity,selected_segment):
	if selected_model=='Standard':
		# macro=pd.DataFrame(rows)
		baseline=[1.0,1.0,1.0]
		adverse=[1.15,1.15,1.15]
		return ({
		        'data': [{'x': np.arange(len(baseline)),'y': baseline},{'x': np.arange(len(adverse)),'y': adverse}],
		    	'layout':{'showlegend':False,'height':200,'margin':{'t':0,'b':20,'l':25,'r':0}}
		    	})
	else:
		df_tmp=models_data.df
		macro_baseline=pd.DataFrame(rows_baseline)
		macro_adverse=pd.DataFrame(rows_adverse)

		macro_baseline=[list(macro_baseline.loc[:,col]) for col in macro_baseline.columns]
		macro_adverse=[list(macro_adverse.loc[:,col]) for col in macro_adverse.columns]
		
		coef=list(df_tmp[(df_tmp['country']==selected_country)&(df_tmp['entity']==selected_entity)&(df_tmp['segment']==selected_segment)]['coef'])[0]
		coef=ast.literal_eval(coef)
		
		baseline=globals()[selected_model](
			country=selected_country,
			entity=selected_entity,
			segment=selected_segment,
			coef=coef,
			macro=[macro_baseline[0],macro_baseline[1]])
		adverse=globals()[selected_model](
			country=selected_country,
			entity=selected_entity,
			segment=selected_segment,
			coef=coef,
			macro=[macro_adverse[0],macro_adverse[1]])
		return ({
		        'data': [{'x': np.arange(len(baseline.pd_projected)),'y': baseline.pd_projected},{'x': np.arange(len(adverse.pd_projected)),'y': adverse.pd_projected}],
		    	'layout':{'showlegend':False,'height':200,'margin':{'t':0,'b':20,'l':25,'r':0}}
		    	})

if __name__ == '__main__':
    app.run_server(debug=True)