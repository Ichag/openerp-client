# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
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
import gobject
import gettext
import pprint

#from view_tree import parse
import rpc


fields_list_type = {
    'checkbox': gobject.TYPE_BOOLEAN,
    'integer': gobject.TYPE_INT,
    'float': gobject.TYPE_FLOAT
}

class win_list(object):
    def __init__(self, model, sel_multi=True, context={}, search=False):
        self.sel_multi = sel_multi
        self.context = context
        self.context.update(rpc.session.context)

        self.model_name = model
        view = rpc.session.rpc_exec_auth('/object', 'execute', model, 'fields_view_get', False, 'tree', context)
        self.view_data = view

        self.tree = widget.tree(view['arch'], view['fields'], model, sel_multi=sel_multi, search=search)
        self.tree.context = context
        self.fields = view['fields']
        self.widget = self.tree.widget
        self.view = self.tree.widget
        self.fields_order = self.tree.fields_order

    def destroy(self):
        self.tree.destroy()
        del self.fields_order
        del self.widget
        del self.view

    def reload(self, ids):
        res = rpc.session.rpc_exec_auth('/object', 'execute', self.model_name, 'read', ids, self.fields_order, self.context)
        self.tree.value = res

    def sel_pos_set(self, num):
        sel = self.view.get_selection()
        sel.unselect_all()
        sel.select_path((num,))
        self.view.scroll_to_cell((num,))

    def sel_ids_get(self):
        return self.tree.sel_ids_get()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

