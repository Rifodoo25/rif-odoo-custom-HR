from odoo import http
from odoo.http import request

class HrRecruitmentAuth(http.Controller):

    @http.route('/jobs/apply/auth/<model("hr.job"):job>', 
                type='http', 
                auth="public", 
                website=True,
                sitemap=False)
    def apply_auth(self, job, **kwargs):
        if not request.env.user.has_group('base.group_user'):
            # Store job ID in session and redirect directly to login
            request.session['apply_job_id'] = job.id
            return request.redirect('/web/login?redirect=/jobs/apply/%s' % job.id)
        return request.redirect('/jobs/apply/%s' % job.id)

    @http.route('/web/login', type='http', auth="none", website=True)
    def web_login(self, redirect=None, **kw):
        # Add job context if coming from application
        if redirect and '/jobs/apply/' in redirect:
            job_id = request.session.get('apply_job_id')
            if job_id:
                # Use sudo to safely access job data
                job = request.env['hr.job'].sudo().browse(int(job_id))
                if job.exists():
                    kw['job_title'] = job.name
        
        # Clear the session variable before proceeding
        if 'apply_job_id' in request.session:
            request.session.pop('apply_job_id')
            
        # Render the login page directly
        return request.env['ir.http'].sudo().render_template('web.login', values={
            'redirect': redirect,
            'job_title': kw.get('job_title', False),
            **kw
        })