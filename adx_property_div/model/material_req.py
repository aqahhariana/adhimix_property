from odoo import api,fields,models,_


confirm =[('draft','Draft'),('confirm','Konfirmasi'),('approved','Di Setujui'), ('cancel','Batal')]
class property_material_req(models.Model):
    _name = "property.material.req"

    name               = fields.Char(string="No. Pengadaan Barang")
    date               = fields.Date(string="Tanggal")
    employee_id        = fields.Many2one(comodel_name="hr.employee", string="Penanggung Jawab")
    description        = fields.Char(string="Deskripsi")
    material_line      = fields.Char(string="Daftar Barang")
    material_req_lines = fields.Many2one(comodel_name="property.material.line", inverse_name="material_id", string="Daftar Permintaan Barang")
    state              = fields.Selection(string="Status", selection=confirm, required=True,readonly=True,default=confirm[0][0])


    @api.multi
    def button_draft(self):
        self.state = confirm[0][0]
        
    @api.multi
    def button_confirm(self):
        self.state = confirm[1][0]

    @api.multi
    def button_approved(self):
        self.state = confirm[2][0]
        
    @api.multi
    def button_cancel(self):
        self.state = confirm[3][0]




class property_material_line(models.Model):
    _name = "property.material.line"

    product_id = fields.Many2one(comodel_name="product.product", string="Product ID")
    qty = fields.Float(string="Qty")
    unit_price = fields.Float(string="Unit Price")
    subtotal = fields.Float(string="Total", compute="_get_subtotal")


    @api.depends('subtotal')
    def _get_subtotal(self):
        self.subtotal = self.qty * self.unit_price
