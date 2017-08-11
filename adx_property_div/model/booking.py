from odoo import api,fields,models,_


confirm =[('draft','Draft'),('confirm','confirm'),('booking_fee_created','Booking Fee Created'),
          ('paid','Paid'),('cancel','cancel'),('waiting_refund_confirmation','Waiting Refund Confirmation'),
          ('refund_fee_created','Refund Fee Created'),('refund_paid','Refund Paid'),('spr','SPR')]
class booking(models.Model):
    _name ="booking.fee"
    
    @api.model
    def _default_company_id(self):
        user = self.env['res.users'].browse(self.env.uid)
        return user.company_id.id
    
    name = fields.Char(string="No.Pemesanan", default="/")
    is_reserved = fields.Boolean(string="Sudah Reservasi")
    reserved_id = fields.Many2one(comodel_name="reserved", string="No. Reservasi")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Nama Kustomer")
    booking_date = fields.Date(string="Tanggal Pemesanan")
    property_unit_id = fields.Many2one(comodel_name="property.unit", string="Unit Properti")
    amount = fields.Float(string="Jumlah Harga Booking")
    notes = fields.Char(string="Catatan")
    state = fields.Selection(string="Status", selection=confirm, required=True,readonly=True,default=confirm[0][0])
    company_id     = fields.Many2one(comodel_name="res.company", string="Nama Company/Divisi", default=_default_company_id)


    @api.multi
    def button_draft(self):
        self.state = confirm[0][0]
        
    @api.multi
    def button_confirmed(self):
        if self.name == '/':
            number = self.env['ir.sequence'].get('booking_busafa')
            self.name = number
        self.state = confirm[1][0]
        
    @api.multi
    def button_create_booking_fee(self):
        self.state = confirm[2][0]

    @api.multi
    def button_create_refund(self):
        self.state = confirm[2][0]

    @api.multi
    def button_create_cancel(self):
        self.state = confirm[2][0]
    
    @api.multi
    def set_draft(self):
        self.state = 'Draft'
    
    @api.multi
    @api.onchange('reserved_id')
    def onchange_reserved_id(self):
        values = {
            'partner_id': False,
            'property_unit_id': False, 
            
        }
        if self.reserved_id :
            values['partner_id'] = self.reserved_id.partner_id.id
            values['property_unit_id'] = self.reserved_id.property_unit_id.id
        self.update(values)