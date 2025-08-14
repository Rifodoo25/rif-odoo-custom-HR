# controllers/main.py - FIXED VERSION
from odoo import http
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
import logging
import base64

_logger = logging.getLogger(__name__)

class CustomWebsiteHrRecruitment(WebsiteHrRecruitment):

    @http.route([
        '/jobs/apply/<int:job_id>',
        '/jobs/apply/<model("hr.job"):job>'
    ], type='http', auth="public", website=True, sitemap=False)
    def jobs_apply(self, job_id=None, job=None, **kwargs):
        """Override the job application route to handle different job types"""
        
        # Handle both integer ID and slug-based routes
        if job:
            job_id = job.id
        else:
            job = request.env['hr.job'].browse(job_id)
            
        _logger.info(f"Job apply request for job {job_id}")
        
        # Get job type using sudo() to avoid permission issues
        try:
            job_sudo = job.sudo()
            job_type_name = None
            
            if job_sudo.contract_type_id:
                job_type_name = job_sudo.contract_type_id.name
                _logger.info(f"Job contract type: {job_type_name}")
            else:
                _logger.info("No contract type set for this job")
                
        except Exception as e:
            _logger.error(f"Error accessing job contract type: {str(e)}")
            job_type_name = None
        
        _logger.info(f"User: {request.env.user}")
        _logger.info(f"Is public user: {request.env.user._is_public()}")
        
        # Check job type - if it's "Stagiaire", use custom form and require authentication
        is_stagiaire = (job_type_name and job_type_name.lower() == 'stagiaire')
        
        if is_stagiaire:
            _logger.info("Job type is Stagiaire - using custom form")
            
            # Check if user is authenticated for stagiaire positions
            if request.env.user._is_public():
                # User is not logged in, redirect to login page
                current_url = request.httprequest.url
                redirect_url = f'/web/login?redirect={current_url}'
                _logger.info(f"Redirecting unauthenticated user to: {redirect_url}")
                return request.redirect(redirect_url)
            
            # User is authenticated, proceed with custom form rendering
            _logger.info("User is authenticated, proceeding with custom stagiaire application form")
            
            # Handle form submission
            if request.httprequest.method == 'POST':
                return self._handle_job_application_submission(job, **kwargs)
            
            # Render custom application form for stagiaire
            return self._render_custom_application_form(job, **kwargs)
        
        else:
            # Job type is NOT Stagiaire - use default Odoo form
            _logger.info("Job type is not Stagiaire - using default Odoo form")
            return super().jobs_apply(job_id=job_id, job=job, **kwargs)

    def _render_custom_application_form(self, job, **kwargs):
        """Render the custom application form for stagiaire positions"""
        
        # Get form data for pre-filling if any
        form_data = kwargs.get('form_data', {})
        
        values = {
            'job': job,
            'form_data': form_data,
            'error': kwargs.get('error', {}),
            'success': kwargs.get('success', False),
        }
        
        return request.render('custom_job_redirect.custom_job_application_form', values)

    def _handle_job_application_submission(self, job, **kwargs):
        """Handle the custom job application form submission for stagiaire positions"""
        
        post = kwargs
        error = {}
        
        # Validate required fields
        required_fields = ['partner_name', 'email_from', 'phone', 'university', 
                          'education_level', 'speciality', 'stage_type', 
                          'stage_agreement', 'start_date', 'end_date', 'duration']
        
        for field in required_fields:
            if not post.get(field):
                error[field] = 'Ce champ est requis'
        
        # Validate email format
        if post.get('email_from'):
            import re
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, post.get('email_from')):
                error['email_from'] = 'Format d\'email invalide'
        
        # Validate that either CV file or LinkedIn profile is provided
        cv_file = None
        has_cv = False
        has_linkedin = bool(post.get('linkedin_profile', '').strip())
        
        if 'cv_file' in request.httprequest.files:
            cv_file = request.httprequest.files['cv_file']
            if cv_file.filename:
                has_cv = True
                # Validate file type and size
                allowed_extensions = ['.pdf', '.doc', '.docx']
                file_ext = '.' + cv_file.filename.split('.')[-1].lower()
                if file_ext not in allowed_extensions:
                    error['cv_file'] = 'Format de fichier non autorisé. Utilisez PDF, DOC ou DOCX'
                elif cv_file.content_length > 5 * 1024 * 1024:  # 5MB limit
                    error['cv_file'] = 'Fichier trop volumineux (max 5MB)'
        
        # Check if either CV or LinkedIn is provided
        if not has_cv and not has_linkedin:
            error['cv_file'] = 'Veuillez fournir un CV ou un profil LinkedIn'
        
        if error:
            return self._render_custom_application_form(job, form_data=post, error=error)
        
        # Create the applicant record
        try:
            # Prepare attachment data for CV
            attachment_ids = []
            if cv_file and cv_file.filename:
                attachment_data = {
                    'name': cv_file.filename,
                    'datas': base64.b64encode(cv_file.read()),
                    'res_model': 'hr.applicant',
                    'res_id': False,  # Will be set after creating applicant
                }
                attachment = request.env['ir.attachment'].sudo().create(attachment_data)
                attachment_ids.append(attachment.id)
            
            # Create applicant
            applicant_data = {
                'partner_name': post.get('partner_name'),
                'email_from': post.get('email_from'),
                'partner_phone': post.get('phone'),
                'job_id': job.id,
                'university': post.get('university'),
                'education_level': post.get('education_level'),
                'speciality': post.get('speciality'),
                'stage_type': post.get('stage_type'),
                'stage_agreement': post.get('stage_agreement') == 'Oui',
                'start_date': post.get('start_date'),
                'end_date': post.get('end_date'),
                'duration': post.get('duration'),
                'linkedin_profile': post.get('linkedin_profile'),
                'description': f"""
Université: {post.get('university')}
Niveau d'études: {post.get('education_level')}
Spécialité: {post.get('speciality')}
Type de stage: {post.get('stage_type')}
Convention de stage: {post.get('stage_agreement')}
Date de début: {post.get('start_date')}
Date de fin: {post.get('end_date')}
Durée: {post.get('duration')}
Profil LinkedIn: {post.get('linkedin_profile', 'Non fourni')}
                """.strip(),
            }
            
            if attachment_ids:
                applicant_data['attachment_ids'] = [(6, 0, attachment_ids)]
            
            applicant = request.env['hr.applicant'].sudo().create(applicant_data)
            
            # Update attachment to link to created applicant
            if attachment_ids:
                request.env['ir.attachment'].sudo().browse(attachment_ids).write({
                    'res_id': applicant.id
                })
            
            _logger.info(f"Created stagiaire applicant {applicant.id} for job {job.id}")
            
            # Redirect to success page
            return request.render('custom_job_redirect.application_success', {
                'job': job,
                'applicant': applicant
            })
            
        except Exception as e:
            _logger.error(f"Error creating applicant: {str(e)}")
            error['general'] = 'Une erreur est survenue lors de l\'envoi de votre candidature. Veuillez réessayer.'
            return self._render_custom_application_form(job, form_data=post, error=error)

    @http.route(['/jobs/detail/<model("hr.job"):job>'], type='http', auth="public", website=True, sitemap=True)
    def jobs_detail(self, job, **kwargs):
        """Override job detail page to ensure proper handling"""
        return super().jobs_detail(job, **kwargs)