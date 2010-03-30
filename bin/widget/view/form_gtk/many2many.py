# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import gobject
import gtk

import gettext

import copy

import wid_common
import common

from widget.screen import Screen
import interface
import service
import rpc

from modules.gui.window.win_search import win_search
from widget.view.form_gtk.many2one import dialog

class many2many(interface.widget_interface):
    def __init__(self, window, parent, model, attrs={}):
        interface.widget_interface.__init__(self, window, parent, model, attrs)

        self.widget = gtk.VBox(homogeneous=False, spacing=1)

        hb = gtk.HBox(homogeneous=False, spacing=3)
        self.wid_text = gtk.Entry()
        self.wid_text.set_property('width_chars', 13)
        self.wid_text.connect('activate', self._sig_activate)
        self.wid_text.connect('button_press_event', self._menu_open)
        hb.pack_start(self.wid_text, expand=True, fill=True)

        hb.pack_start(gtk.VSeparator(), padding=2, expand=False, fill=False)

        self.wid_but_add = gtk.Button(stock='gtk-add')
        self.wid_but_add.set_relief(gtk.RELIEF_HALF)
        self.wid_but_add.set_focus_on_click(True)
        self.wid_but_add.connect('clicked', self._sig_add)
        hb.pack_start(self.wid_but_add, padding=3, expand=False, fill=False)

        self.wid_but_remove = gtk.Button(stock='gtk-remove')
        self.wid_but_remove.set_relief(gtk.RELIEF_HALF)
        self.wid_but_remove.set_focus_on_click(True)
        self.wid_but_remove.connect('clicked', self._sig_remove)
        hb.pack_start(self.wid_but_remove, expand=False, fill=False)

        self.widget.pack_start(hb, expand=False, fill=False)
        self.widget.pack_start(gtk.HSeparator(), expand=False, fill=True)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_placement(gtk.CORNER_TOP_LEFT)
        scroll.set_shadow_type(gtk.SHADOW_NONE)

        self.screen = Screen(attrs['relation'], view_type=['tree'],
                views_preload=attrs.get('views', {}),row_activate=self.row_activate)
        self.screen.type = 'many2many'
        scroll.add_with_viewport(self.screen.widget)
        self.widget.pack_start(scroll, expand=True, fill=True)

    def row_activate(self, screen):
        gui_window = service.LocalService('gui.window')
        domain = self._view.modelfield.domain_get(self._view.model)
        dia = dialog(screen.name, id=screen.id_get(), attrs=self.attrs, domain=domain, window=screen.window,context=screen.context,target=False, view_type=['form'])
        if dia.dia.get_has_separator():
            dia.dia.set_has_separator(False)
        ok, value = dia.run()
        if ok:
            screen.current_model.validate_set()
            screen.current_view.set_value()
        dia.destroy()

    def destroy(self):
        self.screen.destroy()
        self.widget.destroy()
        del self.widget

    def _menu_sig_default(self, obj):
        res = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['model'], 'default_get', [self.attrs['name']])
        self.value = res.get(self.attrs['name'], False)

    def _sig_add(self, *args):
        flag=False
        newids=[]
        domain = self._view.modelfield.domain_get(self._view.model)
        context = self._view.modelfield.context_get(self._view.model)

        ids = rpc.session.rpc_exec_auth('/object', 'execute', self.attrs['relation'], 'name_search', self.wid_text.get_text(), domain, 'ilike', context)
        ids = map(lambda x: x[0], ids)
        win = win_search(self.attrs['relation'], sel_multi=True, ids=ids, context=context, domain=domain, parent=self._window)
        ids = win.go()
        if ids == None:
            ids = []
        old_ids = map(lambda y:y.id,self.screen.models.models)
        new_ids = [id for id in ids if id not in old_ids]
        self.screen.load(new_ids)
        self.screen.display()
        self.wid_text.set_text('')
        self._focus_out()

    def _sig_remove(self, *args):
        self.screen.remove()
        self.screen.display()
        self._focus_out()

    def _sig_activate(self, *args):
        self._sig_add()

    def _readonly_set(self, ro):
        self.wid_text.set_editable(not ro)
        self.wid_text.set_sensitive(not ro)
        self.wid_but_remove.set_sensitive(not ro)
        self.wid_but_add.set_sensitive(not ro)

    def display(self, model, model_field):
        super(many2many, self).display(model, model_field)
        ids = []
        if model_field:
            ids = model_field.get_client(model)
        self.screen.clear()
        self.screen.load(ids)
        self.screen.display()
        return True

    def set_value(self, model, model_field):
        model_field.set_client(model, [x.id for x in self.screen.models.models])

    def grab_focus(self):
        return self.wid_text.grab_focus()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

