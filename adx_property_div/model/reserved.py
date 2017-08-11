from odoo import api,fields,models,_

confirm =[('Draft','Draft'),('confirmed','confirmed'),('cancel','cancel')]
class reserved(models.Model):
    _name ="reserved"
    
    @api.model
    def _default_company_id(self):
        user = self.env['res.users'].browse(self.env.uid)
        return user.company_id.id

    name = fields.Char(string="No. Reservasi", default='/',)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Nama Kustomer")
    reserved_date = fields.Date("Tanggal Reservasi")
    property_unit_id = fields.Many2one(comodel_name="property.unit", string="Unit Property")
    notes = fields.Text("Catatan")
    state = fields.Selection(string="Status", selection=confirm, required=True,readonly=True,default=confirm[0][0])
    company_id     = fields.Many2one(comodel_name="res.company", string="Nama Company/Divisi", default=_default_company_id)
    unit_price = fields.Float("Harga Unit")


    @api.multi
    def button_draft(self):
        self.state = confirm[0][0]
        
    @api.multi
    def button_confirmed(self):
        if self.name == '/':
            number = self.env['ir.sequence'].get('reserved_busafa')
            self.name = number
        prop_unit = self.env['property.unit'].browse(self.property_unit_id.id)
        prop_unit.write({'available': False, 'status': 'reserved'})
        self.state = confirm[1][0]
          
    @api.multi
    def button_cancel(self):
        prop_unit = self.env['property.unit'].browse(self.property_unit_id.id)
        prop_unit.write({'available': True, 'status': 'sale'})
        self.state = confirm[2][0]
    
    
    
    @api.multi
    def set_draft(self):
        self.state = 'Draft'
    
    @api.multi
    @api.onchange('property_unit_id')
    def onchange_unit_id(self):
        values = {
            'unit_price': 0.0,
            
        }
        if not self.property_unit_id:
            self.update({
                'unit_price': 0.0,   
            })
        else :
            values['unit_price'] = self.property_unit_id.current_pricelist
            self.update(values)
    