from odoo import api,fields,models,_

confirm =[('draft','Draft'),('confirm','Konfirmasi'),('approved','Di Setujui'), ('cancel','Batal')]
class property_budget(models.Model):
    _name = "property.budget"

    name                  = fields.Char(string="No. Budget")
    date                  = fields.Date(string="Tanggal")
    jenis                 = fields.Selection([('makro','Makro'),('mikro','Mikro')], string="Jenis")
    type                  = fields.Selection([('infrastructure','Infrastructure'),('building','Building')], string="Tipe Budget")
    area_code             = fields.Char(string="Kode Area")
    land_area             = fields.Float(string="Luas Area")
    effective_land_area   = fields.Float(string="Luas Area Effective")
    work_order            = fields.One2many(inverse_name="budget_id", comodel_name="work.order", string="Deskripsi Pekerjaan")
    state                 = fields.Selection(string="Status", selection=confirm, required=True,readonly=True,default=confirm[0][0])


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



class work_order(models.Model):
    _name = "work.order"

    budget_id     = fields.Many2one(comodel_name="property.budget", string="ID Budget")
    description   = fields.Char(string="Deskripsi Anggaran Biaya")
    amount        = fields.Float(string="Anggaran Biaya")