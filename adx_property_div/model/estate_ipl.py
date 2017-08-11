from odoo import api,fields,models,_


confirm =[('draft','Draft'),('confirm','confirm'),
          ('paid','Paid'),('cancel','Batal')]
class estate_ipl(models.Model):
    _name = "estate.ipl"
  
    name = fields.Char(string="No.")
    unit_id = fields.Many2one(comodel_name="property.unit", string="Unit")
    customer_id = fields.Many2one(comodel_name="res.partner", string="Nama Pemilik")
    category_id = fields.Many2one(comodel_name="property.category", string="Apartement/Hotel/Cluster")
    due_date = fields.Date(string="Tanggal")
    journal_id = fields.Many2one(comodel_name="account.journal", string="Jurnal Pembayaran")
    period_id = fields.Many2one(comodel_name="account.period", string="Period")
    cost_lines = fields.One2many(comodel_name="ipl.cost.line", inverse_name="ipl_id", string="Daftar Biaya")
    state = fields.Selection(string="Status", selection=confirm, required=True,readonly=True,default=confirm[0][0])

    @api.multi
    def button_draft(self):
        self.state = confirm[0][0]
        
    @api.multi
    def button_confirm(self):
        self.state = confirm[1][0]

    @api.multi
    def button_paid(self):
        self.state = confirm[2][0]

    @api.multi
    def button_cancel(self):
        self.state = confirm[2][0]



class ipl_cost_line(models.Model):
    _name = "ipl.cost.line"
  
    ipl_id = fields.Many2one(comodel_name="estate.ipl", string="ID IPL")
    description = fields.Char(string="Deskripsi Biaya")
    amount = fields.Float(string="Biaya")
    account_id = fields.Many2one(comodel_name="account.account", string="Akun Biaya")

    


confirm =[('draft','Draft'),('confirm','Confirm'),('done','Selesai'), ('cancel','Batal')]
class property_rent(models.Model):
    _name ="property.rental"

    name       = fields.Char(string="No. Sewa")
    date       = fields.Date(string="Tanggal Permintaan")
    date_start = fields.Date(string="Tanggal Mulai Sewa")
    date_stop  = fields.Date(string="Tanggal Akhir Sewa")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Nama Kustomer")
    state      = fields.Selection(string="Status", selection=confirm, required=True,readonly=True,default=confirm[0][0])



    @api.multi
    def button_draft(self):
        self.state = confirm[0][0]
        
    @api.multi
    def button_confirm(self):
        self.state = confirm[1][0]

    @api.multi
    def button_done(self):
        self.state = confirm[2][0]
        
    @api.multi
    def button_cancel(self):
        self.state = confirm[3][0]
  