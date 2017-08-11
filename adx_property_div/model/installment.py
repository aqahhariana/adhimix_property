from odoo import api,fields,models,_


class Installment(models.Model):
    _name = "installment"
  
    name                = fields.Char(string="Nama Pembayaran")
    qty_installment     = fields.Float(string="Qty Installment")
    disc_pp_percent     = fields.Float(string="Diskon Cara Pembayaran (%)")
    is_flat_installment = fields.Boolean(string="Instalment Flat")
    interest            = fields.Float(string="Bunga (%)")
    type                = fields.Selection([('kpa','KPA'),('cash_bertahap','Cash Bertahap'),('cash','Cash')], string="Tipe Pembayaran")
    dp_method           = fields.Selection([('percent','Percent'),('nominal','Nominal')], string="Tipe DP", default='percent')
    min_amount_dp       = fields.Float(string="Jumlah DP")
    dp_qty              = fields.Float(string="Qty DP")
    special_dp_case     = fields.Boolean(string="Perlakuan DP Spesial")
    dp_method_special   = fields.Selection([('percent','Percent'),('nominal','Nominal')], string="Tipe DP Spesial")
    amount_dp_special   = fields.Float(string="Jumlah DP Spesial")
    dp_qty_special      = fields.Float(string="Qty DP Spesial")
    active              = fields.Boolean(string="Aktiv", default=True)
    is_flat_dp          = fields.Boolean(string="DP Flat")