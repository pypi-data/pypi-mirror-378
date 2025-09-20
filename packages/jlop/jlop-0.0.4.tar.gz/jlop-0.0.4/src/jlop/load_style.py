import os
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib as mpl

from .colors import set_colorcycle

REGISTRY_STYLES = {
	'modern': {
		'font'  : 'TexGyreHero/texgyreheros-regular.otf',
		'style' : 'modern.mplstyle',
		'color' : 'ibm',
	},
	'classic': {
		'font'  : 'BaKoMa/cmr10.ttf',
		'style' : 'classic.mplstyle',
		'color' : 'ibm',
	},
	'retro': {
		'font'  : 'Hershey-Noialles/Hershey-Noailles-Times-Simplex-Light.ttf',
		'style' : 'retro.mplstyle',
		'color' : 'hoyce',
	},
	'futuristic':{
		'font'  : 'KulimPark/KulimPark-Regular.ttf',
		'style' : 'default.mplstyle',
		'color' : 'hoyce',
	},
	'handwritten': {
		'font': 'Pecita/Pecita.otf',
		'style' : 'default.mplstyle',
		'color' : 'prism',
	}
}

def set_style(style):

	#Check that style is avaliable
	if style not in REGISTRY_STYLES:
		raise ValueError(f'No style named {style}. Avaliable styles are {REGISTRY_STYLES.keys()}')

	#Reset default values
	set_mplstyle('default.mplstyle')

	#Setup style
	set_font(REGISTRY_STYLES[style]['font'])
	set_mplstyle(REGISTRY_STYLES[style]['style'])
	set_colorcycle(REGISTRY_STYLES[style]['color'])

	return 

def set_font(font_file):

	#Load font file
	dir_src = os.path.dirname(__file__)
	dir_src_fonts  = os.path.join(dir_src, 'fonts')
	font_path = os.path.join(dir_src_fonts, font_file)

	#Add font to matplotlib font manager and set it as the font family
	fm.fontManager.addfont(font_path)
	prop = fm.FontProperties(fname=font_path)
	plt.rcParams['font.family'] = prop.get_name()

	return

def set_mplstyle(mplstyle_file):
	
	#Load mplstyle file
	dir_src = os.path.dirname(__file__)
	dir_src_styles = os.path.join(dir_src, 'styles')
	style_path = os.path.join(dir_src_styles, mplstyle_file)
	
	#Set mplstyle
	plt.style.use(style_path)

	return