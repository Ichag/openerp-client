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

import gtk
from gtk import glade
import gettext
import copy

import service
import rpc
import common

from widget.screen import Screen


class dialog(object):
	def __init__(self, arch, fields, state, name):
		buttons = []
		self.states=[]
		self.dia = gtk.Dialog('Tiny ERP', None,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
		for x in state:
			#buttons.append(x[1])
			#buttons.append(gtk.RESPONSE_CANCEL)#len(self.states))

			but = gtk.Button(x[1])
			if len(x)==3:
				icon = gtk.Image()
				icon.set_from_stock(x[2], gtk.ICON_SIZE_BUTTON)
				but.set_image(icon)
			self.dia.add_action_widget(but,len(self.states))
			self.states.append(x[0])

		val = {}
		for f in fields:
			if 'value' in fields[f]:
				val[f] = fields[f]['value']

		self.screen = Screen('wizard.'+name, view_type=[])
		self.screen.new(default=False)
		self.screen.add_view_custom(arch, fields, display=True)
		self.screen.current_model.set(val)

		x,y = self.screen.screen_container.size_get()
		self.screen.widget.set_size_request(x + 20, min(750, y+25))

		self.dia.vbox.pack_start(self.screen.widget)
		self.dia.set_title(self.screen.current_view.title)
		self.dia.show_all()

	def run(self, datas={}):
		while True:
			res = self.dia.run()
			self.screen.current_view.set_value()
			if self.screen.current_model.validate() or (res<0) or (self.states[res]=='end'):
				break
			self.screen.display()
		if res<len(self.states) and res>=0:
			datas.update(self.screen.get())
			self.dia.destroy()
			return (self.states[res], datas)
		else:
			self.dia.destroy()
			return False
	

def execute(action, datas, state='init'):
	if not 'form' in datas:
		datas['form'] = {}
	wiz_id = rpc.session.rpc_exec_auth('/wizard', 'create', action)
	while state!='end':
		thread_progress=common.progress()
		thread_progress.start()
		try:
			res = rpc.session.rpc_exec_auth('/wizard', 'execute', wiz_id, datas, state, rpc.session.context)
		finally:
			thread_progress.stop()

		if 'datas' in res:
			datas['form'].update( res['datas'] )
		if res['type']=='form':
			dia = dialog(res['arch'], res['fields'], res['state'], action)
			dia.screen.current_model.set( datas['form'] )
			res = dia.run(datas['form'])
			if not res:
				break
			(state, new_data) = res
			for d in new_data:
				if new_data[d]==None:
					del new_data[d]
			datas['form'].update(new_data)
			del new_data
		elif res['type']=='action':
			obj = service.LocalService('action.main')
			obj._exec_action(res['action'],datas)
			state = res['state']
		elif res['type']=='print':
			obj = service.LocalService('action.main')
			datas['report_id'] = res.get('report_id', False)
			if res.get('get_id_from_action', False):
				backup_ids = datas['ids']
				datas['ids'] = datas['form']['ids']
				win = obj.exec_report(res['report'], datas)
				datas['ids'] = backup_ids
			else:
				win = obj.exec_report(res['report'], datas)
			state = res['state']
		elif res['type']=='state':
			state = res['state']
		#common.error('Wizard Error:'+ str(e.type), e.message, e.data)
		#state = 'end'

