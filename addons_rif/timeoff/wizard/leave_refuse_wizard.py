from odoo import models, fields

class LeaveRefuseWizard(models.TransientModel):
    _name = 'leave.refuse.wizard'
    _description = 'Wizard de refus de congé'

    reason = fields.Text('Raison du refus', required=True, 
                        help="Expliquez pourquoi cette demande est refusée...")

    def action_refuse(self):
        """Enregistre la raison puis déclenche le refus réel."""
        leave = self.env['hr.leave'].browse(self.env.context.get('active_id'))
        if leave:
            leave.write({'refuse_reason': self.reason})
            
            return leave.with_context(from_refuse_wizard=True).action_refuse()
        return {'type': 'ir.actions.act_window_close'}