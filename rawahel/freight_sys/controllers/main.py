# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.



from odoo import fields, http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request


class WebsiteTracking(http.Controller):

    @http.route(['/tracking'], type='http', auth="public", website=True)
    def track(self, **kw):
        print ('********')
        return request.env['ir.ui.view'].render_template("freight_sys.tracking", {})


    

    @http.route(['/result'], type='http', auth='public', website=True)
    def navigate_to_result_page(self, **kwargs):
        print (kwargs)
        code = request.params.get('code')
        if code:
            policies = request.env['freight_sys.policy'].sudo().search([('code_track','=',code)])
            print (request.params.get('code'))
            print (policies)
            return request.env['ir.ui.view'].render_template("freight_sys.result", {'policies': policies})
        
 

    
            
            