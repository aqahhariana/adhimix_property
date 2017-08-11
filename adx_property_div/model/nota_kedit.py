from odoo import api,fields,models,_


class nota_kredit(models.Model):
    _name = "nota.kredit"

    order_id    = fields.Many2one(comodel_name="property.sale", string="No.SPR")
    amount      = fields.Float(string="Jumlah")
    name        = fields.Char(string="Nama Nota Kredit")