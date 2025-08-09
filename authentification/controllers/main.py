from odoo import http
from odoo.http import request

class WebsiteAuthController(http.Controller):

    @http.route('/contactus', type='http', auth='public', website=True)
    def contactus(self, **kwargs):
        # Check if the user is logged in
        if request.env.user._is_public():
            # Not logged in, redirect to login page with redirect param to come back after login
            return request.redirect('/web/login?redirect=/contactus')
        # User logged in: render the contactus page
        return request.render('website.contactus')
