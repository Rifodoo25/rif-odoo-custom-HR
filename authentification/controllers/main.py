from odoo import http
from odoo.http import request

class WebsiteAuthController(http.Controller):

    @http.route('/jobs/apply/auth/<model("hr.job"):job>', type='http', auth='public', website=True)
    def job_application_auth(self, **kwargs):
        # Check if the user is logged in
        if request.env.user._is_public():
            return request.redirect('/web/login?redirect=/jobs')
        
        # User logged in: render the job application page
        return request.render('website.jobs')