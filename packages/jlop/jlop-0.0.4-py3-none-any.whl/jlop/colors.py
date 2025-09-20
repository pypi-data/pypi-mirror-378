import matplotlib as mpl

# Note: Some of these colormaps are taken from:
#		https://carto.com/carto-colors/
#

COLOR_DICTIONARY = {
	'default'	: [ '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
	'ibm'    	: [ "#648FFF", "#785EF0", "#DC267F", "#FE6100", "#FFB000", "#000000", "#DBDBDB" ],
	'prism'  	: [ '#5F4690', '#1D6996', '#38A6A5', '#0F8554', '#73AF48', '#EDAD08', '#E17C05', '#CC503E', '#94346E', '#6F4070', '#994E95','#666666'],
	'sunset' 	: [ '#f3e79b', '#fac484', '#f8a07e', '#eb7f86', '#ce6693', '#a059a0', '#5c53a5'],
	'hoyce'  	: [ '#4e79a7', '#f28e2b', '#800080', '#59a14f', '#ff0000', '#a9a9a9', '#000000'],
	'lupsasca' 	: [ '#d53e4f', '#fc8d59', '#fee08b', '#e6f598', '#99d594', '#3288bd', '#000000']
}

def set_colorcycle(name='default'):

	if name not in COLOR_DICTIONARY:
		raise ValueError(f'No color scheme named {name}. Avaliable styles are {COLOR_DICTIONARY.keys()}')

	#Set color cycle
	mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=COLOR_DICTIONARY[name]) 

	return COLOR_DICTIONARY[name]
