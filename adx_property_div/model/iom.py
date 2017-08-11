from odoo import api,fields,models,_

confirm =[('draft','Draft'),('confirm','Confirm'),('approved','Approved'), ('compute_installment','Compute Installment'), ('cancel','Batal')]
class iom(models.Model):
    _name = "iom"

    name                        = fields.Char(string="No. IOM")
    perihal                     = fields.Char(string="Perihal")
    description                 = fields.Char(string="Deskripsi")
    opt_pcb                     = fields.Boolean(string="Perubahan Cara Bayar")
    opt_ptb                     = fields.Boolean(string="Perubahan Tanggal Bayar")
    opt_pd                      = fields.Boolean(string="Permintaan Diskon")
    opt_pu                      = fields.Boolean(string="Pergantian Unit")
    opt_cs                      = fields.Boolean(string="Pembatalan")
    opt_ppu                     = fields.Boolean(string="Pergantian Pemilik Unit")
    opt_pls                     = fields.Boolean(string="Pelunasan")
    opt_phd                     = fields.Boolean(string="Penghapusan Denda")
    opt_pdd                     = fields.Boolean(string="Pengurangan Denda")
    order_id                    = fields.Many2one(string="No. SPR", comodel_name="property.sale")
    current_customer_id         = fields.Many2one(string="Nama Kustomer", comodel_name="res.partner")
    current_payment_plan        = fields.Many2one(string="Cara Pembayaran", comodel_name="installment")
    current_property_unit_id    = fields.Many2one(string="Unit", comodel_name="property.unit")
    current_unit_price          = fields.Float(string="Harga Unit")
    total_paid                  = fields.Float(string="Total Sudah bayar")
    residual_installment        = fields.Float(string="Sisa Pembayaran")
    residual_interest           = fields.Float(string="Sisa Bunga")
    installment_paid            = fields.Float(string="Jumlah Installment yang sudah bayar")
    installment_id              = fields.Many2one(string="Cara Pembayaran Baru", comodel_name="installment")
    qty_installment             = fields.Float(string="Qty Installment Baru")
    disc_pp_percent             = fields.Float(string="Diskon Cara Pembayaran Baru (%)")
    is_flat_installment         = fields.Boolean(string="Installment Flat Baru")
    interest                    = fields.Float(string="Bunga (%) Baru")
    dp_method                   = fields.Selection([('nominal','Nominal'),('percent','Percent')], string="Tipe DP Baru")
    amount_dp                   = fields.Float(string="Jumlah DP Baru")
    total_amount_dp             = fields.Float(string="Total DP Baru")
    dp_qty                      = fields.Float(string="Qty DP Baru")
    special_dp_case             = fields.Boolean(string="Perlakuan DP Spesial Baru")
    dp_method_special           = fields.Selection([('nominal','Nominal'),('percent','Percent')], string="Tipe DP Spesial Baru")
    amount_dp_special           = fields.Float(string="Jumlah DP Spesial Baru")
    total_amount_dp_special     = fields.Float(string="Total DP Spesial Baru")
    dp_qty_special              = fields.Boolean(string="Qty DP Spesial Baru")
    old_date                    = fields.Date(string="Tanggal Bayar Lama")
    new_date                    = fields.Date(string="Tanggal Bayar Baru")
    new_unit_id                 = fields.Many2one(string="Unit Baru", comodel_name="property.unit")
    new_customer_id             = fields.Many2one(string="Pemilik Baru", comodel_name="res.partner")
    invoice_penalty_phd         = fields.One2many(inverse_name="iom_id", comodel_name="iom.invoice.penalty.phd", string="Daftar Invoice Yang Akan Di Hapus")
    invoice_penalty_pdd         = fields.One2many(inverse_name="iom_id", comodel_name="iom.invoice.penalty.pdd", string="Daftar Invoice Yang Akan Di Kurangi")
    cost_cancelation            = fields.One2many(inverse_name="iom_id", comodel_name="iom.cost.cancelation", string="Daftar Biaya Pembatalan")
    cost_pergantian_unit        = fields.One2many(inverse_name="iom_id", comodel_name="iom.cost.ganti.unit", string="Daftar Biaya Biaya Pergantian unit")
    old_installment_line        = fields.One2many(inverse_name="iom_id", comodel_name="iom.old.installment", string="Daftar Pembayaran Lama")
    new_installment_line        = fields.One2many(inverse_name="iom_id", comodel_name="iom.new.installment", string="Daftar Pembayaran Baru")
    state                       = state = fields.Selection(string="Status", selection=confirm, required=True,readonly=True,default=confirm[0][0])


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
    def button_compute_installment(self):
        self.state = confirm[3][0]
        
    @api.multi
    def button_cancel(self):
        self.state = confirm[4][0]



    @api.multi
    @api.onchange('disc_pp_percent')
    def onchange_disc_pp_percent(self):
        values = {
            'opt_pcb': '',
            
        }
        if not self.disc_pp_percent:
            self.update({
                'opt_pcb': '',
            })
        else :
            values['opt_pcb'] = self.disc_pp_percent.street
            self.update(values)


    @api.multi
    @api.onchange('qty_installment')
    def onchange_qty_installment(self):
        values = {
            'opt_pcb': '',
            
        }
        if not self.qty_installment:
            self.update({
                'opt_pcb': '',
            })
        else :
            values['opt_pcb'] = self.qty_installment.street
            self.update(values)


    @api.multi
    @api.onchange('installment_id')
    def onchange_installment_id(self):
        values = {
            'opt_pcb': '',
            
        }
        if not self.installment_id:
            self.update({
                'opt_pcb': '',
            })
        else :
            values['opt_pcb'] = self.installment_id.street
            self.update(values)



    @api.multi
    @api.onchange('order_id')
    def onchange_order_id(self):
        values = {
            'current_customer_id': '',
            
        }
        if not self.order_id:
            self.update({
                'current_customer_id': '',
            })
        else :
            values['current_customer_id'] = self.order_id.partner_id.id
            self.update(values)



    
class iom_invoice_penalty_pdd(models.Model):
    _name = "iom.invoice.penalty.pdd"

    iom_id              = fields.Many2one(string="IOM_ID", comodel_name="iom")
    invoice_id          = fields.Many2one(string="No. Invoice", comodel_name="account.invoice")
    amount_invoiced     = fields.Float(string="Jumlah Tagihan")
    amount_proposed     = fields.Float(string="Jumlah Pengurangan Denda")

    # @api.onchange('invoice_id')
    # def onchange_invoice_id(self):
    #     self.invoice_id = self.invoice_id.account_id


class iom_invoice_penalty_phd(models.Model):
    _name = "iom.invoice.penalty.phd"

    iom_id            = fields.Many2one(string="IOM ID", comodel_name="iom")
    invoice_id        = fields.Many2one(string="No. Invoice", comodel_name="account.Invoice")
    amount_invoiced   = fields.Float(string="Jumlah Tagihan")

    # @api.onchange('invoice_id')
    # def onchange_invoice_id(self):
    #     self.invoice_id = self.invoice_id.account_id


class iom_cost_cancelation(models.Model):
    _name = "iom.cost.cancelation"
 
    iom_id          = fields.Many2one(string="IOM ID", comodel_name="iom")
    description     = fields.Char(string="Deskripsi Biaya")
    cost            = fields.Float(string="Biaya")


class iom_cost_ganti_unit(models.Model):
    _name = "iom.cost.ganti.unit"

    iom_id          = fields.Many2one(string="IOM ID", comodel_name="iom")
    description     = fields.Char(string="Deskripsi Biaya")
    cost            = fields.Float(string="Biaya")


class iom_old_installment(models.Model):
    _name = "iom.old.installment"

    date_due         = fields.Date(string="Tanggal Pembayaran")
    unit_id          = fields.Many2one(comodel_name="property.unit", string="Unit")
    description      = fields.Char(string="Deskripsi")
    amount_total     = fields.Float(string="Total Harga")
    amount           = fields.Float(string="Harga Pokok")
    amount_interest  = fields.Float(string="Bunga")
    iom_id           = fields.Many2one(string="IOM ID", comodel_name="iom")



class iom_new_installment(models.Model):
    _name = "iom.new.installment"

    date_due         = fields.Date(string="Tanggal Pembayaran")
    unit_id          = fields.Many2one(comodel_name="property.unit", string="Unit")
    description      = fields.Char(string="Deskripsi")
    amount_total     = fields.Float(string="Total Harga")
    amount           = fields.Float(string="Harga Pokok")
    amount_interest  = fields.Float(string="Bunga")
    iom_id           = fields.Many2one(string="IOM ID", comodel_name="iom")