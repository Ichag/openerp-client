##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: char.py 5730 2007-02-25 18:08:18Z pinky $
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

import re
import gettext
import gtk
from gtk import glade

import common
import interface
from mx.DateTime import DateTimeDelta

class float_time(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		self.win_gl = glade.XML(common.terp_path("terp.glade"), "widget_char", 
								gettext.textdomain())
		self.widget = self.win_gl.get_widget('widget_char')
		self.widget.set_max_length(int(attrs.get('size',11)))
		self.widget.set_visibility(not attrs.get('invisible', False))
		self.widget.set_width_chars(5)

		self.widget.connect('button_press_event', self._menu_open)
		self.widget.connect('activate', self.sig_activate)
		self.widget.connect('focus-in-event', lambda x,y: self._focus_in())
		self.widget.connect('focus-out-event', lambda x,y: self._focus_out())
		interface.widget_interface.__init__(self, window, parent=parent, attrs=attrs)

	def text_to_float(self, text):
		try:
			if text and ':' in text:
				rec = re.compile('([\-0-9]+)d +([0-9]+):([0-9]+)')
				res = rec.match(text)
				if res:
					return round(DateTimeDelta(int(res.group(1)),int(res.group(2)), int(res.group(3))).hours + 0.004, 2)
				return round(DateTimeDelta(0,int(text.split(':')[0]), int(text.split(':')[1])).hours + 0.004, 2)
			else:
				return locale.atof(text)
		except:
			pass
		return 0.0

	def set_value(self, model, model_field):
		v = self.widget.get_text()
		if not v:
			return model_field.set_client(model, 0.0)
		return model_field.set_client(model, self.text_to_float(v))

	def display(self, model, model_field):
		if not model_field:
			self.widget.set_text('00:00')
			return False
		super(float_time, self).display(model, model_field)
		if abs(model_field.get(model) or 0.0) >=24:
			t = DateTimeDelta(0, model_field.get(model) or 0.0).strftime('%dd %H:%M')
		else:
			t = DateTimeDelta(0, model_field.get(model) or 0.0).strftime('%H:%M')
		if  model_field.get(model)<0:
			t = '-'+t
		self.widget.set_text(t)

	def _readonly_set(self, value):
		self.widget.set_editable(not value)
		self.widget.set_sensitive(not value)

