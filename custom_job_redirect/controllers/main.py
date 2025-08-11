# controllers/main.py
from odoo import http
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
import logging

_logger = logging.getLogger(__name__)


class CustomWebsiteHrRecruitment(WebsiteHrRecruitment):

    @http.route([
        '/jobs/apply/<int:job_id>',
        '/jobs/apply/<model("hr.job"):job>'
    ], type='http', auth="public", website=True, sitemap=False)
    def jobs_apply(self, job_id=None, job=None, **kwargs):
        """Override the job application route to handle unauthenticated users"""
        
        # Handle both integer ID and slug-based routes
        if job:
            job_id = job.id
            job_slug = job.website_url.split('/')[-1] if job.website_url else str(job.id)
        else:
            job_slug = str(job_id)
        
        _logger.info(f"Job apply request for job {job_id} (slug: {job_slug})")
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
        return super().jobs_apply(job_id=job_id, job=job, **kwargs)

    @http.route(['/jobs/detail/<model("hr.job"):job>'], type='http', auth="public", website=True, sitemap=True)
    def jobs_detail(self, job, **kwargs):
        """Override job detail page to ensure proper handling"""
        return super().jobs_detail(job, **kwargs)