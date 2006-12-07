##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import pygtk
pygtk.require('2.0')

import gtk
from gtk import glade
from xml.parsers import expat

import sys
import wid_int
import gettext

class _container(object):
	def __init__(self, max_width):
		self.cont = []
		self.max_width = max_width	
		self.width = {}
	def new(self, col=2):
		self.col = col
		table = gtk.Table(1, col)
		#table.set_homogeneous(True)
		table.set_row_spacings(3)
		table.set_col_spacings(5)
		table.set_border_width(5)
		self.cont.append( (table, 0, 0) )
	def get(self):
		return self.cont[-1][0]
	def pop(self):
		(table, x, y) = self.cont.pop()
		return table
	def newline(self):
		(table, x, y) = self.cont[-1]
		if x>0:
			self.cont[-1] = (table, 0, y+1)
		table.resize(y+1,self.col)
	def wid_add(self, widget, l=1, name=None, expand=False, ypadding=0):
		(table, x, y) = self.cont[-1]
		if l>self.col:
			l=self.col
		if l+x>self.col:
			self.newline()
			(table, x, y) = self.cont[-1]
		if name:
			vbox = gtk.VBox(homogeneous=False, spacing=1)
			label = gtk.Label(name)
			label.set_alignment(0.0, 0.5)
			vbox.pack_start(label, expand=False)
			vbox.pack_start(widget, expand=expand, fill=expand)
			wid = vbox
		else:
			wid = widget
		yopt = 0
		if expand:
			yopt = yopt | gtk.EXPAND
		table.attach(wid, x, x+l, y, y+1) #DISABLED DUE TO GTK UPGADE: , yoptions=yopt, ypadding=ypadding)
		self.cont[-1] = (table, x+l, y)
		(width, height) = widget.size_request()
		self.width[('%d.%d') % (x,y)] = width

class parse(object):
	def __init__(self, parent, fields, model=''):
		self.fields = fields
		self.parent = parent
		self.model = model
		self.col = 8
		self.focusable = None
		
	def _psr_start(self, name, attrs):
		if name in ('form','tree'):
			self.title = attrs.get('string','Form')
			self.container.new(self.col)
		elif name=='field':
			if attrs.get('select', False) or self.fields[attrs['name']].get('select', False):
				type = attrs.get('widget', self.fields[attrs['name']]['type'])
				self.fields[attrs['name']].update(attrs)
				self.fields[attrs['name']]['model']=self.model
				widget_act = widgets_type[ type ][0](attrs['name'], self.parent, self.fields[attrs['name']])
				if 'string' in self.fields[attrs['name']]:
					label = self.fields[attrs['name']]['string']+' :'
				else:
					label = None
				self.dict_widget[str(attrs['name'])] = widget_act
				size = widgets_type[ type ][1]
				if not self.focusable:
					self.focusable = widget_act.widget
				self.container.wid_add(widget_act.widget, size, label, int(self.fields[attrs['name']].get('expand',0)))

	def _psr_end(self, name):
		pass
	def _psr_char(self, char):
		pass
	def parse(self, xml_data, max_width):
		psr = expat.ParserCreate()
		psr.StartElementHandler = self._psr_start
		psr.EndElementHandler = self._psr_end
		psr.CharacterDataHandler = self._psr_char
		self.notebooks=[]
		self.container=_container(max_width)
		self.dict_widget={}
		psr.Parse(xml_data)
		self.widget = self.container.pop()
		self.widget.show_all()
		return self.dict_widget

class form(wid_int.wid_int):
	def __init__(self, xml, fields, model=None, parent=None):
		wid_int.wid_int.__init__(self, 'Form', parent)
		parser = parse(self, fields, model=model)
		self.model = model
		#get the size of the window and the limite / decalage Hbox element
		ww, hw = self.parent.size_request()
		self.widgets = parser.parse(xml, ww)
		self.widget = parser.widget
		self.focusable = parser.focusable
		self.id=None
		self.name=parser.title

	def clear(self):
		self.id=None
		for x in self.widgets.values():
			x.clear()

	def _value_get(self):
		res = []
		for x in self.widgets:
			res+=self.widgets[x].value
		return res

	def _value_set(self, value):
		for x in value:
			if x in self.widgets:
				self.widgets[x].value = value[x]

	value = property(_value_get, _value_set, None,
	  'The content of the form or excpetion if not valid')

import calendar
import spinbutton
import spinint
import selection
import char
import checkbox
import reference
import many2one

widgets_type = {
	'date': (calendar.calendar, 3),
	'datetime': (calendar.calendar, 3),
	'float': (spinbutton.spinbutton, 2),
	'integer': (spinint.spinint, 2),
	'selection': (selection.selection, 2),
	'many2one_selection': (selection.selection, 2),
	'char': (char.char, 2),
	'boolean': (checkbox.checkbox, 2),
	'reference': (reference.reference, 2),
	'text': (char.char, 2),
	'email': (char.char, 2),
	'url': (char.char, 2),
	'many2one': (char.char, 2),
	'one2many': (char.char, 2),
	'one2many_form': (char.char, 2),
	'one2many_list': (char.char, 2),
	'many2many_edit': (char.char, 2),
	'many2many': (char.char, 2),
}
