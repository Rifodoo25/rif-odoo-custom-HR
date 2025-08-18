# controllers/main.py
from odoo import http, fields, _
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from odoo.exceptions import UserError, AccessError, ValidationError
import logging
import base64
from werkzeug.exceptions import NotFound

_logger = logging.getLogger(__name__)

class CandidatePortal(http.Controller):
    
    # Constants for better maintainability
    MODIFIABLE_STAGES = ['New', 'Nouveau', 'Initial', 'Application Received', 'To Review']
   
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt', '.rtf']
    
    def _get_current_user_partner(self):
        """Get current user's partner with validation"""
        user = request.env.user
        if user._is_public():
            raise AccessError(_("Authentication required"))
        return user, user.partner_id
    
    def _get_user_applicant(self, applicant_id, partner_id):
        """Get applicant ensuring it belongs to current user"""
        applicant = request.env['hr.applicant'].sudo().search([
            ('id', '=', applicant_id),
            ('partner_id', '=', partner_id)
        ], limit=1)
        
        if not applicant:
            raise NotFound(_("Application not found or access denied"))
        return applicant
    
    def _set_session_message(self, message_type, message):
        """Set session message helper"""
        request.session['application_message'] = {
            'type': message_type,
            'message': message
        }
    
    def _get_session_message(self):
        """Get and clear session message"""
        return request.session.pop('application_message', None)
    
    def _get_description_field_value(self, applicant):
        """Get description from various possible fields"""
        possible_fields = ['description', 'user_input', 'cover_letter', 'motivation', 'note']
        
        for field_name in possible_fields:
            if hasattr(applicant, field_name):
                value = getattr(applicant, field_name, None)
                if value:
                    return value
        return ''

    def _set_description_field_value(self, applicant, value):
        """Set description in the appropriate field"""
        possible_fields = ['description', 'user_input', 'cover_letter', 'motivation']
        
        for field_name in possible_fields:
            if hasattr(applicant, field_name):
                try:
                    applicant.sudo().write({field_name: value})
                    _logger.info(f"Updated {field_name} field successfully")
                    return True
                except Exception as e:
                    _logger.warning(f"Failed to update {field_name}: {str(e)}")
                    continue
        
        # Fallback: add as message
        try:
            applicant.sudo().message_post(
                body=f"<p><strong>Description updated:</strong></p><p>{value}</p>",
                message_type='comment'
            )
            return True
        except Exception as e:
            _logger.warning(f"Failed to add description as message: {str(e)}")
            return False

    def _validate_file_upload(self, uploaded_file):
        """Validate uploaded file"""
        if not uploaded_file or not uploaded_file.filename:
            return None
            
        # Check file size
        file_content = uploaded_file.read()
        if len(file_content) > self.MAX_FILE_SIZE:
            raise ValidationError(_("File too large (max 10MB)"))
        
        # Check file extension
        file_ext = '.' + uploaded_file.filename.split('.')[-1].lower()
        if file_ext not in self.ALLOWED_FILE_EXTENSIONS:
            raise ValidationError(_("File type not allowed. Use: PDF, DOC, DOCX, TXT, RTF"))
        
        return file_content

    def _handle_file_upload(self, applicant, uploaded_file):
        """Handle CV file upload with proper cleanup"""
        file_content = self._validate_file_upload(uploaded_file)
        if not file_content:
            return
        
        # Remove old CV attachments
        old_attachments = request.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'hr.applicant'),
            ('res_id', '=', applicant.id),
            '|', '|', '|',
            ('name', 'ilike', '.pdf'),
            ('name', 'ilike', '.doc'),
            ('name', 'ilike', 'cv'),
            ('name', 'ilike', 'resume')
        ])
        old_attachments.unlink()
        
        # Create new attachment
        attachment = request.env['ir.attachment'].sudo().create({
            'name': uploaded_file.filename,
            'datas': base64.b64encode(file_content),
            'res_model': 'hr.applicant',
            'res_id': applicant.id,
            'mimetype': uploaded_file.content_type,
            'type': 'binary',
        })
        
        # Link to applicant
        self._link_attachment_to_applicant(applicant, attachment)
        _logger.info(f"CV uploaded successfully: {uploaded_file.filename}")

    def _link_attachment_to_applicant(self, applicant, attachment):
        """Link attachment to applicant using available fields"""
        attachment_fields = ['attachment_ids', 'resume_ids', 'cv_ids']
        
        for field_name in attachment_fields:
            if hasattr(applicant, field_name):
                try:
                    current_attachments = getattr(applicant, field_name).ids
                    applicant.sudo().write({
                        field_name: [(6, 0, current_attachments + [attachment.id])]
                    })
                    return
                except Exception as e:
                    _logger.warning(f"Failed to link attachment via {field_name}: {str(e)}")
                    continue

    def _get_or_create_withdrawn_stage(self):
        """Get or create withdrawn stage"""
        withdrawn_stage = request.env['hr.recruitment.stage'].sudo().search([
            ('name', '=', 'Retiré')
        ], limit=1)
        
        if not withdrawn_stage:
            # Try to find any folded stage
            withdrawn_stage = request.env['hr.recruitment.stage'].sudo().search([
                ('fold', '=', True)
            ], limit=1)
            
            if not withdrawn_stage:
                # Create new withdrawn stage
                withdrawn_stage = request.env['hr.recruitment.stage'].sudo().create({
                    'name': 'Retiré',
                    'fold': True,
                    'sequence': 100,
                })
                
        return withdrawn_stage

    def _render_template_with_fallback(self, template_name, values, fallback_html_func):
        """Render template with HTML fallback"""
        try:
            return request.render(template_name, values)
        except Exception as e:
            _logger.error(f"Template error for {template_name}: {str(e)}")
            return request.make_response(
                fallback_html_func(values), 
                headers=[('Content-Type', 'text/html; charset=utf-8')]
            )

    def _generate_applications_fallback_html(self, values):
        """Generate fallback HTML for applications list"""
        applicants = values.get('applicants', [])
        html = """
        <div class="container mt-4">
            <h1>Mes candidatures</h1>
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead><tr><th>Poste</th><th>Status</th><th>Date</th><th>Actions</th></tr></thead>
                    <tbody>
        """
        
        for applicant in applicants:
            html += f"""
                <tr>
                    <td>{applicant.job_id.name}</td>
                    <td>{applicant.stage_id.name}</td>
                    <td>{applicant.create_date.strftime('%d/%m/%Y')}</td>
                    <td>
                        <a href="/my/application/{applicant.id}" class="btn btn-sm btn-info">Détails</a>
                        <a href="/my/application/withdraw/{applicant.id}" class="btn btn-sm btn-warning ml-2" 
                           onclick="return confirm('Êtes-vous sûr?')">Retirer</a>
                    </td>
                </tr>
            """
        html += "</tbody></table></div></div>"
        return html

    @http.route(['/candidate/applications'], type='http', auth='user', website=True, sitemap=False)
    def candidate_applications(self, **kwargs):
        """Display all applications for the current user"""
        try:
            user, partner = self._get_current_user_partner()
            _logger.info(f"Loading applications for user: {user.name}")
            
            # Find all applications for this partner
            applicants = request.env['hr.applicant'].sudo().search([
                ('partner_id', '=', partner.id)
            ], order='create_date desc')
            
            values = {
                'applicants': applicants,
                'user': user,
                'partner': partner,
                'message': self._get_session_message(),
            }
            
            return self._render_template_with_fallback(
                'new_page.candidate_applications_template',
                values,
                self._generate_applications_fallback_html
            )
            
        except Exception as e:
            _logger.error(f"Error in candidate_applications: {str(e)}", exc_info=True)
            self._set_session_message('error', 'An error occurred while loading your applications')
            return request.redirect('/jobs')
    
    @http.route(['/my/application/<int:applicant_id>'], type='http', auth='user', website=True, sitemap=False)
    def application_detail(self, applicant_id, **kwargs):
        """View detailed information about a specific application"""
        try:
            user, partner = self._get_current_user_partner()
            applicant = self._get_user_applicant(applicant_id, partner.id)
            
            _logger.info(f"User {user.name} accessing application detail {applicant_id}")
            
            values = {
                'applicant': applicant,
                'user': user,
                'partner': partner,
            }
            
            def fallback_html(vals):
                app = vals['applicant']
                return f"""
                <div class="container mt-4">
                    <a href="/candidate/applications" class="btn btn-secondary mb-3">← Retour</a>
                    <h1>Détails de la candidature</h1>
                    <div class="card">
                        <div class="card-body">
                            <h3>{app.job_id.name}</h3>
                            <p><strong>Status:</strong> {app.stage_id.name}</p>
                            <p><strong>Date:</strong> {app.create_date.strftime('%d/%m/%Y %H:%M')}</p>
                            <div class="mt-3">
                                <a href="/jobs/detail/{app.job_id.id}" class="btn btn-primary">Voir l'offre</a>
                            </div>
                        </div>
                    </div>
                </div>
                """
            
            return self._render_template_with_fallback(
                'new_page.application_detail_template',
                values,
                fallback_html
            )
                
        except (NotFound, AccessError) as e:
            self._set_session_message('error', str(e))
            return request.redirect('/candidate/applications')
        except Exception as e:
            _logger.error(f"Error in application_detail: {str(e)}", exc_info=True)
            self._set_session_message('error', 'Error displaying application details')
            return request.redirect('/candidate/applications')

    @http.route(['/my/application/modify/<int:applicant_id>'], type='http', auth='user', website=True, sitemap=False, methods=['POST'])
    def modify_application(self, applicant_id, **kwargs):
        """Modify an existing application (only for modifiable statuses)"""
        try:
            user, partner = self._get_current_user_partner()
            applicant = self._get_user_applicant(applicant_id, partner.id)
            
            _logger.info(f"User {user.name} modifying application {applicant_id}")
            
            # Check if modifiable
            if applicant.stage_id.name not in self.MODIFIABLE_STAGES:
                raise ValidationError(f'This application cannot be modified (status: {applicant.stage_id.name})')
            
            # Prepare update data
            update_data = {
                'partner_name': kwargs.get('partner_name', applicant.partner_name),
                'email_from': kwargs.get('email_from', applicant.email_from),
                'partner_phone': kwargs.get('partner_phone', applicant.partner_phone),
            }
            
            # Handle description
            description_value = kwargs.get('description', '')
            if description_value:
                self._set_description_field_value(applicant, description_value)
            
            # Handle file upload
            if 'attachment_ids' in request.httprequest.files:
                self._handle_file_upload(applicant, request.httprequest.files['attachment_ids'])
            
            # Update partner info
            partner.sudo().write({
                'name': update_data['partner_name'],
                'email': update_data['email_from'],
                'phone': update_data['partner_phone'],
            })
            
            # Update application
            applicant.sudo().write(update_data)
            
            # Add modification note
            current_description = self._get_description_field_value(applicant)
            modification_note = f"\n\n--- Modified on {fields.Datetime.now()} ---"
            self._set_description_field_value(applicant, current_description + modification_note)
            
            self._set_session_message('success', f'Application for "{applicant.job_id.name}" updated successfully!')
            
        except (NotFound, AccessError, ValidationError) as e:
            self._set_session_message('error', str(e))
        except Exception as e:
            _logger.error(f"Error in modify_application: {str(e)}", exc_info=True)
            self._set_session_message('error', f'Error modifying application: {str(e)}')
        
        return request.redirect('/candidate/applications')
    
    
   


class CustomWebsiteHrRecruitment(WebsiteHrRecruitment):
    
    @http.route([
        '/jobs/apply/<model("hr.job"):job>',
        '/jobs/apply/<model("hr.job"):job>/<string:slug>'
    ], type='http', auth="public", website=True, sitemap=False)
    def jobs_apply(self, job, **kwargs):
        """Override job application route with authentication and duplicate checks"""
        _logger.info(f"Job apply request for job {job.id} - {job.name}")
        
        # Check authentication
        if request.env.user._is_public():
            current_url = request.httprequest.url
            redirect_url = f'/web/login?redirect={current_url}'
            _logger.info(f"Redirecting unauthenticated user to: {redirect_url}")
            return request.redirect(redirect_url)
        
        # Check for existing active applications
        partner = request.env.user.partner_id
        existing_applicant = request.env['hr.applicant'].sudo().search([
            ('partner_id', '=', partner.id),
            ('job_id', '=', job.id),
            ('stage_id.fold', '=', False)  # Active applications only
        ], limit=1)
        
        if existing_applicant:
            request.session['application_message'] = {
                'type': 'warning',
                'message': f'You already have an active application for "{job.name}". '
                          'You cannot apply again while your current application is in progress.'
            }
            return request.redirect('/candidate/applications')
        
        # Proceed with normal application flow
        _logger.info("User authenticated and eligible, proceeding with application")
        return super().jobs_apply(job=job, **kwargs)