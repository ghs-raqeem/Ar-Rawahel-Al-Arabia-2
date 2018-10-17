# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo RTL support
#    Copyright (C) 2014 Mohammed Barsi.
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


from odoo import models, api, fields
import odoo


class Language(models.Model):
    _inherit = 'res.lang'

    lang_font = fields.Selection([
        ('font1','Stc'),
        ('font2','GE SS'),
        ('font3','GE SS Two'),
        ('font4','Kufi'),
        ('font5','Jazeera'),
        ('font6','GE SS Unique'),
        ('font7','JF Flat'),
        ('font8','Frutiger LT Arabic'),
        ('font9','DIN Next LT W23'),
        ('font10','Boutros Asma'),
        ('font11','Ara ES Nawar'),
    ]
        ,string='Font', default='font1')

    @api.model
    @odoo.tools.ormcache(skiparg=1)
    def _get_languages_dir(self):
        langs = self.search([('active', '=', True)])
        return dict([(lg.code, lg.direction) for lg in langs])

    @api.multi
    def get_languages_dir(self):
        return self._get_languages_dir()

    @api.multi
    def write(self, vals):
        self._get_languages_dir.clear_cache(self)
        return super(Language, self).write(vals)