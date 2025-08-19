from odoo import models, fields

class LeaveRefuseWizard(models.TransientModel):
    _name = 'leave.refuse.wizard'
    _description = 'Wizard de refus de congé'

    reason = fields.Text('Raison du refus', required=True, 
                        help="Expliquez pourquoi cette demande est refusée...")

    def action_refuse(self):
        """Refuse le congé avec la raison saisie"""
        active_id = self.env.context.get('active_id')
        if active_id:
            leave = self.env['hr.leave'].browse(active_id)
            # Sauvegarder la raison
            leave.refuse_reason = self.reason
            # Appeler la méthode de refus (qui gère tout automatiquement)
            leave.action_refuse()
            
        return {'type': 'ir.actions.act_window_close'}