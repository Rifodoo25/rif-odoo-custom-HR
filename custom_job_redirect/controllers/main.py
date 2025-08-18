# controllers/main.py
from odoo import http
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from odoo.exceptions import ValidationError
from werkzeug.exceptions import NotFound
import logging

_logger = logging.getLogger(__name__)


class CustomWebsiteHrRecruitment(WebsiteHrRecruitment):
    
    def _get_job_from_params(self, job_id=None, job=None):
        """
        Helper method to get job record from parameters
        Returns tuple: (job_record, job_id, job_slug)
        """
        if job:
            return job, job.id, job.website_url.split('/')[-1] if job.website_url else str(job.id)
        
        if job_id:
            # Cache job lookup to avoid repeated database calls
            job_record = request.env['hr.job'].sudo().browse(job_id)
            if not job_record.exists():
                raise NotFound("Job not found")
            return job_record, job_id, str(job_id)
        
        raise ValidationError("No job specified")
    
    def _is_user_authenticated(self):
        """Check if current user is authenticated (not public)"""
        return not request.env.user._is_public()
    
    def _build_login_redirect_url(self, current_url):
        """Build login redirect URL with proper encoding"""
        from werkzeug.urls import url_encode
        return f'/web/login?{url_encode({"redirect": current_url})}'
    
    def _log_application_attempt(self, job_id, job_slug, user, is_authenticated):
        """Centralized logging for application attempts"""
        if _logger.isEnabledFor(logging.INFO):
            _logger.info(
                "Job application attempt - Job: %s (slug: %s), User: %s, Authenticated: %s",
                job_id, job_slug, user.name or user.login, is_authenticated
            )

    @http.route([
        '/jobs/apply/<int:job_id>',
        '/jobs/apply/<model("hr.job"):job>'
    ], type='http', auth="public", website=True, sitemap=False, csrf=False)
    def jobs_apply(self, job_id=None, job=None, **kwargs):
        """
        Override the job application route to handle unauthenticated users
        Optimized with better error handling and performance
        """
        try:
            # Get job information efficiently
            job_record, resolved_job_id, job_slug = self._get_job_from_params(job_id, job)
            
            # Check authentication status
            is_authenticated = self._is_user_authenticated()
            current_user = request.env.user
            
            # Log the attempt
            self._log_application_attempt(resolved_job_id, job_slug, current_user, is_authenticated)
            
            # Handle unauthenticated users
            if not is_authenticated:
                current_url = request.httprequest.url
                redirect_url = self._build_login_redirect_url(current_url)
                
                _logger.info("Redirecting unauthenticated user to: %s", redirect_url)
                return request.redirect(redirect_url)
            
            # Additional business logic checks
            if not job_record.website_published:
                _logger.warning("Attempt to apply for unpublished job %s by user %s", 
                              resolved_job_id, current_user.login)
                return request.not_found()
            
            if job_record.state == 'close':
                # You might want to show a custom message for closed positions
                _logger.info("Application attempt for closed job %s", resolved_job_id)
                # Could redirect to a "position closed" page or show message
            
            # User is authenticated and job is valid, proceed with normal flow
            _logger.info("Processing authenticated application for job %s", resolved_job_id)
            
            # Ensure we pass the correct parameters to parent method
            return super().jobs_apply(job_id=resolved_job_id, job=job_record, **kwargs)
            
        except NotFound:
            _logger.error("Job not found: job_id=%s", job_id)
            return request.not_found()
        except ValidationError as e:
            _logger.error("Validation error in job application: %s", str(e))
            return request.redirect('/jobs')
        except Exception as e:
            _logger.error("Unexpected error in jobs_apply: %s", str(e), exc_info=True)
            # Graceful fallback
            return request.redirect('/jobs')

    @http.route(['/jobs/detail/<model("hr.job"):job>'], 
                type='http', auth="public", website=True, sitemap=True)
    def jobs_detail(self, job, **kwargs):
        """
        Override job detail page with additional checks
        """
        try:
            # Check if job exists and is published
            if not job.exists() or not job.website_published:
                return request.not_found()
            
            # Optional: Add view tracking
            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug("Job detail view for job %s by user %s", 
                            job.id, request.env.user.login)
            
            return super().jobs_detail(job, **kwargs)
            
        except Exception as e:
            _logger.error("Error in jobs_detail: %s", str(e), exc_info=True)
            return request.not_found()

    @http.route(['/jobs'], type='http', auth="public", website=True, sitemap=True)
    def jobs_index(self, **kwargs):
        """
        Optional: Override jobs listing page for additional functionality
        """
        try:
            # Add any custom logic here (filtering, analytics, etc.)
            return super().jobs_index(**kwargs)
        except Exception as e:
            _logger.error("Error in jobs_index: %s", str(e), exc_info=True)
            # Fallback to basic page
            return request.render('website_hr_recruitment.index', {})

    # Additional utility methods for extensibility
    
    def _check_application_permissions(self, job, user):
        """
        Hook for additional permission checks
        Override this method to add custom business rules
        """
        return True
    
    def _get_application_context(self, job, user, **kwargs):
        """
        Prepare additional context for application form
        Override this method to add custom data
        """
        return {
            'job': job,
            'user': user,
            'can_apply': self._check_application_permissions(job, user),
            **kwargs
        }