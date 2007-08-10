import matplotlib
matplotlib.use('GTKCairo')

from pylab import arange
from matplotlib.font_manager import FontProperties

# 24 RGB values, one for each 15-degree hue incr around the HSV color wheel
wheel = [
	(255,0,0),
	(255,51,0),
	(255,102,0),
	(255,128,0),
	(255,153,0),
	(255,178,0),
	(255,204,0),
	(255,229,0),
	(255,255,0),
	(204,255,0),
	(153,255,0),
	(51,255,0),
	(0,204,0),
	(0,178,102),
	(0,153,153),
	(0,102,178),
	(0,51,204),
	(25,25,178),
	(51,0,153),
	(64,0,153),
	(102,0,153),
	(153,0,153),
	(204,0,153),
	(229,0,102),
]

# Offsets used to yield different color cycling methods
analogicOffsets = [ 0, 12, 18, 6, 1, 13, 19, 7 ]
tetradOffsets = [ 0, 22, 2, 1, 23, 3 ]
triadOffsets = [ 7, 1, 0, 4, 6, 2, 5, 3, ]

# Generate index values (into 'wheel') for each cycling method

analogicSteps = []
for offset in analogicOffsets:
	analogicSteps.append(offset)
	analogicSteps.append((offset + 2) % 24)
	analogicSteps.append((offset + 4) % 24)

tetradSteps = []
for offset in tetradOffsets:
	tetradSteps.append(offset)
	tetradSteps.append((offset + 4) % 24)
	tetradSteps.append((offset + 12) % 24)
	tetradSteps.append((offset + 16) % 24)

triadSteps = []
for offset in triadOffsets:
	triadSteps.append(offset)
	triadSteps.append((offset + 8) % 24)
	triadSteps.append((offset + 16) % 24)

# Generate color cycle values from a given stepping pattern
def cycle(steps):
	for n in xrange(len(wheel)):
		yield wheel[steps[n]]

# Bake color cycles into lists for random access
analogicColors = list(rgb for rgb in cycle(analogicSteps))
tetradColors = list(rgb for rgb in cycle(tetradSteps))
triadColors = list(rgb for rgb in cycle(triadSteps))

def get_color(index, colors=triadColors):
	return '#%02x%02x%02x' % colors[index % len(colors)]


def tinygraph(subplot, type='pie', axis={}, axis_data={}, datas=[], axis_group_field={}, orientation='horizontal', overlap=1.0):
	subplot.clear()
	operators = {
		'+': lambda x,y: x+y,
		'*': lambda x,y: x*y,
		'min': lambda x,y: min(x,y),
		'max': lambda x,y: max(x,y),
		'**': lambda x,y: x**y
	}
	axis_group = {}
	keys = {}
	data_axis = []
	data_all = {}
	for field in axis[1:]:
		data_all = {}
		for d in datas:
			group_eval = ','.join(map(lambda x: d[x], axis_group_field.keys()))
			axis_group[group_eval] = 1

			data_all.setdefault(d[axis[0]], {})
			keys[d[axis[0]]] = 1

			if group_eval in  data_all[d[axis[0]]]:
				oper = operators[axis_data[field].get('operator', '+')]
				data_all[d[axis[0]]][group_eval] = oper(data_all[d[axis[0]]][group_eval], d[field])
			else:
				data_all[d[axis[0]]][group_eval] = d[field]
		data_axis.append(data_all)
	axis_group = axis_group.keys()
	axis_group.sort()
	keys = keys.keys()
	keys.sort()

	if not datas:
		return False
	font_property = FontProperties(size=8)
	if type == 'pie':
		labels = tuple(data_all.keys())
		value = tuple(map(lambda x: reduce(lambda x,y=0: x+y, data_all[x].values(), 0), labels))
		explode = map(lambda x: (x%4==2) and 0.06 or 0.0,range(len(value)))
		colors = map(lambda x: get_color(x), range(len(value)))
		aa = subplot.pie(value, autopct='%1.1f%%', shadow=True, explode=explode, colors=colors)
		labels = map(lambda x: x.split('/')[-1], labels)
		subplot.legend(aa, labels, shadow = True, loc = 'best', prop = font_property)

	elif type == 'bar':
		n = len(axis)-1
		gvalue = []
		gvalue2 = []
		if float(n):
			width =  0.9 / (float(n))
		else:
			width = 0.9
		ind = map(lambda x: x+width*n/2, arange(len(keys)))
		if orientation=='horizontal':
			subplot.set_yticks(ind)
			subplot.set_yticklabels(tuple(keys), visible=True, ha='right', size=8)
			subplot.xaxis.grid(True,'major',linestyle='-',color='gray')
		else:
			subplot.set_xticks(ind)
			subplot.set_xticklabels(tuple(keys), visible=True, ha='right', size=8, rotation='vertical')
			subplot.yaxis.grid(True,'major',linestyle='-',color='gray')

		for i in range(n):
			datas = data_axis[i]
			ind = map(lambda x: x+width*i*overlap+((1.0-overlap)*n*width)/4, arange(len(keys)))
			#ind = map(lambda x: x, arange(len(keys)))
			yoff = map(lambda x:0.0, keys)

			for y in range(len(axis_group)):
				value = [ datas[x].get(axis_group[y],0.0) for x in keys]
				if len(axis_group)>1:
					color = get_color(y)
				else:
					color = get_color(i)
				if orientation=='horizontal':
					aa = subplot.barh(ind, tuple(value), width, left=yoff, color=color, edgecolor="#333333")[0]
				else:
					aa = subplot.bar(ind, tuple(value), width, bottom=yoff, color=color, edgecolor="#333333")[0]
				gvalue2.append(aa)
				for j in range(len(yoff)):
					yoff[j]+=value[j]
			gvalue.append(aa)

		if True:
			if len(axis_group)>1:
				axis_group = map(lambda x: x.split('/')[-1], axis_group)
				subplot.legend(gvalue2,axis_group,shadow=True,loc='best',prop = font_property)
			else:
				t1 = [ axis_data[x]['string'] for x in axis[1:]]
				subplot.legend(gvalue,t1,shadow=True,loc='best',prop = font_property)
		else:
			pass
	else:
		raise Exception, 'Graph type '+type+' does not exist !'
