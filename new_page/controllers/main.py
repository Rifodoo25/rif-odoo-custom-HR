# controllers/main.py
from odoo import http
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
import logging

_logger = logging.getLogger(__name__)

class CandidatePortal(http.Controller):
    
    @http.route(['/candidate/applications'], type='http', auth='user', website=True, sitemap=False)
    def candidate_applications(self, **kwargs):
        """Display all applications for the current user"""
        user = request.env.user
        partner = user.partner_id
        
        _logger.info(f"Loading applications for user: {user.name}")
        
        # Find all applications linked to this partner
        applicants = request.env['hr.applicant'].sudo().search([
            ('partner_id', '=', partner.id)
        ], order='create_date desc')
        
        # Get any session message and clear it
        message = request.session.pop('application_message', None)
        
        values = {
            'applicants': applicants,
            'user': user,
            'partner': partner,
            'message': message,
        }
        
        try:
            # Try to render the template - if it fails, we'll catch the error
            return request.render('new_page.candidate_applications_template', values)
        except Exception as e:
            _logger.error(f"Error rendering template: {str(e)}")
            # Fallback to simple HTML if template fails
            html = f"""
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
                               onclick="return confirm('Êtes-vous sûr de vouloir retirer cette candidature?')">Retirer</a>
                        </td>
                    </tr>
                """
            html += "</tbody></table></div></div>"
            return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])
    
    @http.route(['/my/application/<int:applicant_id>'], type='http', auth='user', website=True, sitemap=False)
    def application_detail(self, applicant_id, **kwargs):
        """View detailed information about a specific application"""
        user = request.env.user
        partner = user.partner_id
        
        _logger.info(f"User {user.name} accessing application detail {applicant_id}")
        
        try:
            # Find the application and ensure it belongs to the current user
            applicant = request.env['hr.applicant'].sudo().search([
                ('id', '=', applicant_id),
                ('partner_id', '=', partner.id)
            ], limit=1)
            
            if not applicant:
                _logger.warning(f"Application {applicant_id} not found for user {user.name}")
                request.session['application_message'] = {
                    'type': 'error',
                    'message': 'Candidature non trouvée ou accès non autorisé.'
                }
                return request.redirect('/candidate/applications')
            
            values = {
                'applicant': applicant,
                'user': user,
                'partner': partner,
            }
            
            try:
                return request.render('new_page.application_detail_template', values)
            except Exception as template_error:
                _logger.error(f"Template error: {str(template_error)}")
                # Fallback to simple HTML
                html = f"""
                <div class="container mt-4">
                    <a href="/candidate/applications" class="btn btn-secondary mb-3">← Retour</a>
                    <h1>Détails de la candidature</h1>
                    <div class="card">
                        <div class="card-body">
                            <h3>{applicant.job_id.name}</h3>
                            <p><strong>Status:</strong> {applicant.stage_id.name}</p>
                            <p><strong>Date de candidature:</strong> {applicant.create_date.strftime('%d/%m/%Y %H:%M')}</p>
                            <p><strong>Département:</strong> {applicant.job_id.department_id.name if applicant.job_id.department_id else 'Non spécifié'}</p>
                            <div class="mt-3">
                                <a href="/jobs/detail/{applicant.job_id.id}" class="btn btn-primary">Voir l'offre</a>
                                <a href="/my/application/withdraw/{applicant.id}" class="btn btn-warning ml-2"
                                   onclick="return confirm('Êtes-vous sûr?')">Retirer candidature</a>
                            </div>
                        </div>
                    </div>
                </div>
                """
                return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])
                
        except Exception as e:
            _logger.error(f"Error viewing application {applicant_id}: {str(e)}")
            request.session['application_message'] = {
                'type': 'error',
                'message': 'Erreur lors de l\'affichage de la candidature.'
            }
            return request.redirect('/candidate/applications')
    
    @http.route(['/my/application/withdraw/<int:applicant_id>'], type='http', auth='user', website=True, sitemap=False)
    def withdraw_application(self, applicant_id, **kwargs):
        """Withdraw an active application"""
        user = request.env.user
        partner = user.partner_id
        
        _logger.info(f"User {user.name} attempting to withdraw application {applicant_id}")
        
        try:
            # Find the application and ensure it belongs to the current user
            applicant = request.env['hr.applicant'].sudo().search([
                ('id', '=', applicant_id),
                ('partner_id', '=', partner.id)
            ], limit=1)
            
            if not applicant:
                _logger.warning(f"Application {applicant_id} not found for user {user.name}")
                request.session['application_message'] = {
                    'type': 'error',
                    'message': 'Candidature non trouvée ou accès non autorisé.'
                }
                return request.redirect('/candidate/applications')
            
            # Use partner_name or job name for logging instead of applicant.name
            candidate_info = applicant.partner_name or applicant.email_from or f"Application {applicant.id}"
            _logger.info(f"Found application for {candidate_info} - Job: {applicant.job_id.name} - Stage: {applicant.stage_id.name} - Fold: {applicant.stage_id.fold}")
            
            # Check if the application can be withdrawn (only active applications)
            if applicant.stage_id.fold or applicant.stage_id.name in ['Accepté', 'Refusé', 'Retiré']:
                _logger.warning(f"Application {applicant_id} cannot be withdrawn - status: {applicant.stage_id.name}, fold: {applicant.stage_id.fold}")
                request.session['application_message'] = {
                    'type': 'error',
                    'message': f'Cette candidature ne peut pas être retirée (statut: {applicant.stage_id.name}).'
                }
                return request.redirect('/candidate/applications')
            
            # Find or create a "Retiré" (Withdrawn) stage
            withdrawn_stage = request.env['hr.recruitment.stage'].sudo().search([
                ('name', '=', 'Retiré')
            ], limit=1)
            
            if not withdrawn_stage:
                # Try to find any folded stage to use as withdrawn
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
                    _logger.info("Created new 'Retiré' stage")
            
            job_name = applicant.job_id.name
            
            # Update the application
            applicant.sudo().write({
                'stage_id': withdrawn_stage.id,
            })
            
            # Add a note to the description (using the correct field)
            # Try to add a withdrawal note - use different fields depending on what's available
            from datetime import datetime
            withdrawal_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            withdrawal_note = f"--- Candidature retirée par le candidat le {withdrawal_date} ---"
            
            # Try to add note to description field if it exists
            try:
                if hasattr(applicant, 'description'):
                    current_description = applicant.description or ''
                    applicant.sudo().write({
                        'description': current_description + f"\n\n{withdrawal_note}"
                    })
                elif hasattr(applicant, 'user_input'):
                    # Some versions use user_input field
                    current_input = applicant.user_input or ''
                    applicant.sudo().write({
                        'user_input': current_input + f"\n\n{withdrawal_note}"
                    })
                else:
                    # If no description field, we'll just log it
                    _logger.info(f"Added withdrawal note for application {applicant_id}: {withdrawal_note}")
            except Exception as note_error:
                # If adding note fails, just log it - don't break the withdrawal process
                _logger.warning(f"Could not add withdrawal note: {str(note_error)}")
                pass
            
            _logger.info(f"Application {applicant_id} withdrawn successfully. New stage: {withdrawn_stage.name}")
            
            request.session['application_message'] = {
                'type': 'success',
                'message': f'Candidature pour "{job_name}" retirée avec succès. Vous pouvez maintenant postuler à nouveau.'
            }
            
        except Exception as e:
            _logger.error(f"Error withdrawing application {applicant_id}: {str(e)}")
            import traceback
            _logger.error(traceback.format_exc())
            request.session['application_message'] = {
                'type': 'error',
                'message': f'Erreur lors du retrait de la candidature: {str(e)}'
            }
        
        return request.redirect('/candidate/applications')
    
    @http.route(['/my/application/delete/<int:applicant_id>'], type='http', auth='user', website=True, sitemap=False)
    def delete_application(self, applicant_id, **kwargs):
        """Delete a finished application"""
        user = request.env.user
        partner = user.partner_id
        
        _logger.info(f"User {user.name} attempting to delete application {applicant_id}")
        
        try:
            # Find the application and ensure it belongs to the current user
            applicant = request.env['hr.applicant'].sudo().search([
                ('id', '=', applicant_id),
                ('partner_id', '=', partner.id)
            ], limit=1)
            
            if not applicant:
                _logger.warning(f"Application {applicant_id} not found for user {user.name}")
                request.session['application_message'] = {
                    'type': 'error',
                    'message': 'Candidature non trouvée ou accès non autorisé.'
                }
                return request.redirect('/candidate/applications')
            
            # Check if the application can be deleted (only closed/finished applications)
            if not applicant.stage_id.fold and applicant.stage_id.name not in ['Refusé', 'Annulé', 'Retiré']:
                _logger.warning(f"Application {applicant_id} cannot be deleted - status: {applicant.stage_id.name}")
                request.session['application_message'] = {
                    'type': 'error',
                    'message': 'Vous ne pouvez supprimer que les candidatures terminées ou refusées.'
                }
                return request.redirect('/candidate/applications')
            
            job_name = applicant.job_id.name
            applicant.sudo().unlink()  # Delete the application
            
            _logger.info(f"Application {applicant_id} deleted successfully by user {user.name}")
            
            request.session['application_message'] = {
                'type': 'success',
                'message': f'Candidature pour "{job_name}" supprimée avec succès.'
            }
            
        except Exception as e:
            _logger.error(f"Error deleting application {applicant_id}: {str(e)}")
            request.session['application_message'] = {
                'type': 'error',
                'message': 'Erreur lors de la suppression de la candidature.'
            }
        
        return request.redirect('/candidate/applications')


class CustomWebsiteHrRecruitment(WebsiteHrRecruitment):
    
    @http.route([
        '/jobs/apply/<model("hr.job"):job>',
        '/jobs/apply/<model("hr.job"):job>/<string:slug>'
    ], type='http', auth="public", website=True, sitemap=False)
    def jobs_apply(self, job, **kwargs):
        """Override the job application route to handle unauthenticated users"""
        
        _logger.info(f"Job apply request for job {job.id} - {job.name}")
        
        # Check if user is authenticated (not a public/anonymous user)
        if request.env.user._is_public():
            # User is not logged in, redirect to login page
            current_url = request.httprequest.url
            redirect_url = f'/web/login?redirect={current_url}'
            _logger.info(f"Redirecting unauthenticated user to: {redirect_url}")
            return request.redirect(redirect_url)
        
        # Check if user already has an active application for this job
        partner = request.env.user.partner_id
        existing_applicant = request.env['hr.applicant'].sudo().search([
            ('partner_id', '=', partner.id),
            ('job_id', '=', job.id),
            ('stage_id.fold', '=', False)  # Active application (not closed/archived)
        ], limit=1)
        
        if existing_applicant:
            # User already has an active application, redirect to applications page with message
            request.session['application_message'] = {
                'type': 'warning',
                'message': f'Vous avez déjà une candidature active pour le poste "{job.name}". Vous ne pouvez pas postuler à nouveau tant que votre candidature actuelle est en cours.'
            }
            return request.redirect('/candidate/applications')
        
        # User is authenticated and can apply, proceed with normal flow
        _logger.info("User is authenticated, proceeding with application")
        return super().jobs_apply(job=job, **kwargs)