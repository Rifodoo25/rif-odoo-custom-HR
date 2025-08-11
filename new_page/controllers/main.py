# controllers/main.py
from odoo import http
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
import logging

_logger = logging.getLogger(__name__)

class CustomWebsiteHrRecruitment(WebsiteHrRecruitment):
    
    @http.route([
        '/jobs/apply/<model("hr.job"):job>',
        '/jobs/apply/<model("hr.job"):job>/<string:slug>'
    ], type='http', auth="public", website=True, sitemap=False)
    def jobs_apply(self, job, **kwargs):
        """Override the job application route to handle unauthenticated users"""
        
        _logger.info(f"Job apply request for job {job.id} - {job.name}")
        _logger.info(f"User: {request.env.user}")
        _logger.info(f"Is public user: {request.env.user._is_public()}")
        
        # Check if user is authenticated (not a public/anonymous user)
        if request.env.user._is_public():
            # User is not logged in, redirect to login page
            current_url = request.httprequest.url
            redirect_url = f'/web/login?redirect={current_url}'
            _logger.info(f"Redirecting unauthenticated user to: {redirect_url}")
            return request.redirect(redirect_url)
        
        # User is authenticated, proceed with normal flow
        _logger.info("User is authenticated, proceeding with application")
        return super().jobs_apply(job=job, **kwargs)
    
    @http.route(['/jobs/detail/<model("hr.job"):job>'], type='http', auth="public", website=True, sitemap=True)
    def jobs_detail(self, job, **kwargs):
        """Override job detail page to ensure proper handling"""
        return super().jobs_detail(job, **kwargs)
    
    @http.route(['/candidate/applications'], type='http', auth='user', website=True, sitemap=False)
    def candidate_applications(self, **kwargs):
        user = request.env.user
        partner = user.partner_id
        
        # Find all applications linked to this partner
        applicants = request.env['hr.applicant'].sudo().search([
            ('partner_id', '=', partner.id)
        ])
        
        return request.render('new_page.candidate_applications_template', {
            'applicants': applicants,
            'user': user,
            'partner': partner,
        })