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
            return request.redirect('/web/login?redirect=/jobs/apply/auth/%s' % job.id)
        return request.redirect(f'/jobs/apply/{job.id}')