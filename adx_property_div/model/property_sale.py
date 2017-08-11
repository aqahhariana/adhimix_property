from odoo import api,fields,models,_
from datetime import datetime, timedelta
from calendar import monthrange
from odoo.tools.misc import formatLang
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp
from gdata.contentforshopping.data import Price

confirm =[('draft','Draft'),('booking','Booking Confirmed'),('waiting_manager','Waiting Manager Approve'),('confirm','SPR Confirm'),('done','Done'),('cancel','Batal')]
class property_sale(models.Model):
    _name ="property.sale"
    
    @api.model
    def _default_company_id(self):
        user = self.env['res.users'].browse(self.env.uid)
        return user.company_id.id
    
    @api.model
    def _compute_tax(self, tax_id, price):
        tax = self.env['account.tax'].browse(tax_id)
        rate = 0
        reversed = 0
        amount = 0
        amount_tax = 0
        if tax.amount_type == 'fixed':
            rate = tax.amount
            reversed = tax.amount * 100
            
        elif tax.amount_type == 'percent' or tax.amount_type == 'division':
            rate = tax.amount/100
            reversed = tax.amount
        
        if tax.price_include == True:
            amount = price /(100+reversed/100)
            amount_tax = rate * amount
        else :
            amount = price
            amount_tax = rate * amount         
        return amount_tax
    
    @api.one
    @api.depends('property_order_ids','interest','amount_after_discount','total_amount_dp')
    def _compute_amount(self):
        total = 0
        total_tax = 0
        tax_id = []
        for line in self.property_order_ids:
            total = total + line.unit_price
            if line.tax_id :
                tax_id.append(line.tax_id.id)
        
        if len(tax_id) > 0:
            total_tax = self._compute_tax(tax_id[0], self.amount_after_discount)
        total_untaxed =  self.amount_after_discount - total_tax
        
        
        bunga = (self.amount_after_discount - self.total_amount_dp) * (self.interest/100)
        self.amount_before_discount = total
        self.amount_interest = bunga
        self.amount_taxed = total_tax
        self.amount_untaxed = total_untaxed
        self.amount_final = total_untaxed + total_tax + bunga
        


    name                    = fields.Char(string="No.SPR/No. BFR", default="/")
    booking_id              = fields.Many2one(comodel_name="booking.fee", string="No. Pemesanan")
    partner_id              = fields.Many2one(comodel_name="res.partner", string="Nama Kustomer")
    date_spr                = fields.Date(string="Tanggal SPR")
    is_ppjb                 = fields.Boolean(string="Sudah PPJB")
    is_bast                 = fields.Boolean(string="Sudah BAST")
    notes                   = fields.Text(string="Catatan")
    property_order_ids      = fields.One2many(comodel_name="property.order.line", inverse_name="order_id", string="Unit Property")
    installment_id          = fields.Many2one(comodel_name="installment", string="Cara Pembayaran")
    qty_installment         = fields.Float(string="Qty Installment")
    disc_pp_percent         = fields.Float(string="Diskon Cara Pembayaran (%)")
    is_flat_installment     = fields.Boolean(string="Installment Flat")
    interest                = fields.Float(string="Bunga (%)")
    dp_method               = fields.Selection([('percent','Percent'),('nominal','Nominal')], string="Tipe DP")
    amount_dp               = fields.Float(string="Jumlah DP")
    total_amount_dp         = fields.Float(string="Total DP")
    dp_qty                  = fields.Float(string="Qty DP")
    special_dp_case         = fields.Boolean(string="Perlakuan DP Spesial")
    dp_method_special       = fields.Selection([('percent','Percent'),('nominal','Nominal')], string="Tipe DP Spesial")
    amount_dp_special       = fields.Float(string="Jumlah DP Spesial")
    total_amount_dp_special = fields.Float(string="Total DP Spesial")
    dp_qty_special          = fields.Float(string="Qty DP Spesial")
    booking_fee_amount      = fields.Float(string="Jumlah Booking Fee")
    pembayaran              = fields.One2many(comodel_name="property.payment.line", inverse_name="order_id", string="Pembayaran")
    state = fields.Selection(string="Status", selection=confirm, required=True,readonly=True,default=confirm[0][0])
    company_id     = fields.Many2one(comodel_name="res.company", string="Nama Company/Divisi", default=_default_company_id)
    amount_before_discount  = fields.Float(string='Total Sebelum Diskon', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_discount_pp      = fields.Float(string="Diskon Cara Pembayaran")
    amount_after_discount       = fields.Float(string="Total Setelah Diskon")
    is_flat_dp              = fields.Boolean(string="DP Flat")
    amount_interest = fields.Float(string='Total Bunga', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_untaxed = fields.Float(string='Total Tanpa Pajak', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_taxed = fields.Float(string='Total Pajak', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_final = fields.Float(string='Total Keseluruhan', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    
    
    
    @api.multi
    def button_confirmed(self):
        if self.name == '/':
            number = self.env['ir.sequence'].get('sales_busafa') 
        self.state = confirm[1][0]
        
    @api.multi
    def action_confirm_booking_fee(self):
        booking = self.env['booking.fee'].browse(self.booking_id.id)
        booking.write({'state': 'spr'})
        self.state = 'waiting_manager'

    @api.multi
    def action_confirm_manager(self):
        for line in self.pembayaran:
            line.write({'state': 'confirm'})
        self.state = 'confirm'

    @api.multi
    def button_cancel(self):
        for line in self.property_order_ids:
            line.property_unit_id.write({'available': True, 'state': 'sale'})
        for line in self.pembayaran:
            line.write({'state': 'cancel'})
        self.state = 'cancel'
    
    @api.multi
    def set_draft(self):
        for line in self.property_order_ids:
            line.property_unit_id.write({'available': False, 'state': 'booked'})
        self.state = 'draft'
    
    @api.multi
    def compute_installment(self):
        payment_line = self.env['property.payment.line']
        old_payment = payment_line.search([('state', '=', 'draft'),('order_id', '=', self.id)])
        if old_payment :
            old_payment.unlink()
        #Iniate Date
        curr_date = datetime.strptime(self.date_spr, '%Y-%m-%d')
        date_inv = curr_date
        day = date_inv.day
        month = date_inv.month
        year = date_inv.year
        total_days = (year % 4) and 365 or 366
        #initiate Payment
        qty_inst = self.qty_installment
        payment_plan = self.installment_id.type
        is_flat_pp = self.is_flat_installment
        is_flat_dp = self.is_flat_dp
        total_dp = self.total_amount_dp
        qty_dp = self.dp_qty
        if qty_dp > 0:
            #calculate downpayment from any use plan (cash bertahap, kpa)
            if is_flat_dp == True:
                amount_dp = total_dp - self.booking_fee_amount
            else:
                amount_dp = total_dp
            dp_per = amount_dp / qty_dp
            first_dp = dp_per - self.booking_fee_amount
            j= 0
            # define interest for downpayment special for kpa
            if payment_plan == 'kpa':
                interest_kpa = self.amount_interest/qty_dp
            else :
                interest_kpa = 0
            if self.special_dp_case == False:
                for i in range(0, int(qty_dp)):
                    if j == 0 :
                        if is_flat_dp != True :
                            dp_payment= first_dp
                        else:
                            dp_payment = amount_dp/qty_dp
                    else :
                        dp_payment = amount_dp/qty_dp
                    values = {
                            'order_id': self.id,
                            'date_due': date_inv.strftime("%Y-%m-%d"),
                            
                            'description': i < (qty_dp - 1) and "Downpayment-%s" % (i + 1) or "Pelunasan Downpayment",
                            'amount_total': dp_payment + interest_kpa,
                            'amount':dp_payment,
                            'amount_interest': interest_kpa,
                            'state': 'draft',
                           
                        }
                   
                    month_range = monthrange(date_inv.year, date_inv.month)
                    date_inv = (datetime(year, month, day) + relativedelta(months=+1))
                    if month_range[1] == 28:
                        if curr_date.day == 29:
                            date_inv += timedelta(days=+1)
                        if curr_date.day == 30:
                            date_inv += timedelta(days=+2)
                        if curr_date.day == 31:
                                date_inv += timedelta(days=+3)

                    elif month_range[1] == 29:
                        if curr_date.day == 30:
                            date_inv += timedelta(days=+1)
                        if curr_date.day == 31:
                            date_inv += timedelta(days=+2)
                    day = date_inv.day
                    month = date_inv.month
                    year = date_inv.year
                    payment_line.create(values)
                    j = j+1
            else :
                amount_dp_special = self.total_amount_dp_special
                if is_flat_dp == True:
                    amount_dp = total_dp - amount_dp_special - self.booking_fee_amount
                else:
                    amount_dp = total_dp - amount_dp_special
                
                qty_special = self.dp_qty_special
                residual_qty = qty_dp - qty_special
                if amount_dp_special >= total_dp:
                    raise osv.except_osv(_('Error !'), _('DP Spesial Tidak Boleh Melebihi DP'))

                for i in range(0, int(qty_special)):
                    if i == 0:
                        if is_flat_dp != True:
                            #dp = amount_dp_special/qty_special
                            dp_payment = (amount_dp_special/qty_special) - self.booking_fee_amount
                        else:
                            dp_payment = amount_dp_special/qty_special
                    else:
                        dp_payment = amount_dp_special/qty_special
                        
                    values = {
                            'order_id': self.id,
                            'date_due': date_inv.strftime("%Y-%m-%d"),
                            
                            'description': i < (qty_dp - 1) and "Downpayment-%s" % (i + 1) or "Pelunasan Downpayment",
                            'amount_total': dp_payment + interest_kpa,
                            'amount':dp_payment,
                            'amount_interest': interest_kpa,
                            'state': 'draft',
                           
                        }
                   
                    month_range = monthrange(date_inv.year, date_inv.month)
                    date_inv = (datetime(year, month, day) + relativedelta(months=+1))
                    if month_range[1] == 28:
                        if curr_date.day == 29:
                            date_inv += timedelta(days=+1)
                        if curr_date.day == 30:
                            date_inv += timedelta(days=+2)
                        if curr_date.day == 31:
                                date_inv += timedelta(days=+3)

                    elif month_range[1] == 29:
                        if curr_date.day == 30:
                            date_inv += timedelta(days=+1)
                        if curr_date.day == 31:
                            date_inv += timedelta(days=+2)
                    day = date_inv.day
                    month = date_inv.month
                    year = date_inv.year
                    payment_line.create(values)
                    j = j+1
                    
                for i in range(0, int(residual_qty)):
                    dp_payment = amount_dp/residual_qty
                    values = {
                            'order_id': self.id,
                            'date_due': date_inv.strftime("%Y-%m-%d"),
                            
                            'description': i < (qty_dp - 1) and "Downpayment-%s" % (i + 1) or "Pelunasan Downpayment",
                            'amount_total': dp_payment + interest_kpa,
                            'amount':dp_payment,
                            'amount_interest': interest_kpa,
                            'state': 'draft',
                        }
                   
                    month_range = monthrange(date_inv.year, date_inv.month)
                    date_inv = (datetime(year, month, day) + relativedelta(months=+1))
                    if month_range[1] == 28:
                        if curr_date.day == 29:
                            date_inv += timedelta(days=+1)
                        if curr_date.day == 30:
                            date_inv += timedelta(days=+2)
                        if curr_date.day == 31:
                                date_inv += timedelta(days=+3)

                    elif month_range[1] == 29:
                        if curr_date.day == 30:
                            date_inv += timedelta(days=+1)
                        if curr_date.day == 31:
                            date_inv += timedelta(days=+2)
                    day = date_inv.day
                    month = date_inv.month
                    year = date_inv.year
                    payment_line.create(values)
                    j = j+1
        
        if payment_plan == 'cash' or payment_plan == 'cash_bertahap':
            if payment_plan == 'cash':
                desc='Pelunasan'
                desc2 = 'Pelunasan'
            elif payment_plan == 'cash_bertahap':
                desc ='Cicilan'
                desc2 ='Pelunasan Cicilan'
            amount_sisa = self.amount_after_discount - self.total_amount_dp
            if is_flat_pp == True or self.total_amount_dp == 0:
                res= self.amount_after_discount - self.booking_fee_amount
                amount_sisa = res
            total_interest = self.amount_interest
            
            j = 0
            for i in range(0, int(qty_inst)):
                interest = total_interest/qty_inst
                if j == 0 :
                    if is_flat_pp == True or self.total_amount_dp == 0:
                        payment = (amount_sisa/qty_inst) - self.booking_fee_amount
                    else:
                        payment = amount_sisa/qty_inst
                else :
                    payment = amount_sisa/qty_inst

                values = {
                            
                            'order_id': self.id,
                            'date_due': date_inv.strftime("%Y-%m-%d"),
                            'description':i < (qty_inst - 1) and str(desc)+"-%s" % (i + 1) or str(desc2)+"-%s" % (i + 1),
                            'amount_total': payment+interest,
                            'amount':payment,
                            'amount_interest': interest,
                            'state': 'draft',
                            }

                month_range = monthrange(date_inv.year, date_inv.month)
                date_inv = (datetime(year, month, day) + relativedelta(months=+1))
                if month_range[1] == 28:
                    if curr_date.day == 29:
                        date_inv += timedelta(days=+1)
                    if curr_date.day == 30:
                        date_inv += timedelta(days=+2)
                    if curr_date.day == 31:
                        date_inv += timedelta(days=+3)

                elif month_range[1] == 29:
                    if curr_date.day == 30:
                        date_inv += timedelta(days=+1)
                    if curr_date.day == 31:
                        date_inv += timedelta(days=+2)
                day = date_inv.day
                month = date_inv.month
                year = date_inv.year
                payment_line.create(values)
                j = j + 1
        
        if payment_plan == 'kpa':
            sisa_pelunasan = self.amount_after_discount - self.total_amount_dp
            #date_inv = ((datetime(year, month, day) - relativedelta(months=+1)) + relativedelta(days=+7))
            date_inv = (datetime(year, month, day) + relativedelta(months=+1))
            values = {      
                'order_id': self.id,
                'date_due': date_inv.strftime("%Y-%m-%d"),
                'description':'Pelunasan KPR',
                'amount_total': sisa_pelunasan,
                'amount':sisa_pelunasan,
                'amount_interest': 0,
                'state': 'draft',
            }
            payment_line.create(values)      
              
        return True
            

    
    @api.multi
    @api.onchange('booking_id')
    def onchange_booking_id(self):
        property = []
        values = {
            'partner_id': False,
            'property_order_ids': property,
            'booking_fee_amount': 0
            
        }
        if self.booking_id :
            property.append(((0,0,{'property_unit_id':self.booking_id.property_unit_id.id, 'description': self.booking_id.property_unit_id.name, 'unit_price': self.booking_id.property_unit_id.current_pricelist})))
            values['partner_id'] = self.booking_id.partner_id.id
            values['property_order_ids'] = property
            values['booking_fee_amount'] = self.booking_id.amount
        self.update(values)
    
    @api.multi
    @api.onchange('installment_id')
    def onchange_installment_id(self):
        property = []
        values = {
            'qty_installment': 0,
            'disc_pp_percent': 0,
            'is_flat_installment': False,
            'interest': 0,
            'dp_method': '',
            'amount_dp': 0,
            'dp_qty': 0,
            'is_flat_dp': False,
            'special_dp_case': False,
            'dp_method_special': '',
            'amount_dp_special': 0,
            'total_amount_dp_special': 0,
            'dp_qty_special': 0
            
        }
        if self.installment_id :
          
            values['qty_installment'] = self.installment_id.qty_installment
            values['disc_pp_percent'] = self.installment_id.disc_pp_percent
            values['is_flat_installment'] = self.installment_id.is_flat_installment
            values['interest'] = self.installment_id.interest
            values['dp_method'] = self.installment_id.dp_method
            values['amount_dp'] = self.installment_id.min_amount_dp
            values['dp_qty'] = self.installment_id.dp_qty
            values['is_flat_dp'] = self.installment_id.is_flat_dp
            values['special_dp_case'] = self.installment_id.special_dp_case
        self.update(values)
    
    
    @api.multi
    @api.onchange('disc_pp_percent')
    def onchange_discount_pp(self):
        amount = 0
        amount_after = 0
        values = {
            'amount_discount_pp': 0,
            'amount_after_discount': 0,
            
        }
        if self.disc_pp_percent :
            amount = (self.disc_pp_percent/100) * self.amount_before_discount
            amount_after = self.amount_before_discount - amount
            values['amount_discount_pp'] = amount
            values['amount_after_discount'] = amount_after
            
        self.update(values)
    
    @api.multi
    @api.onchange('amount_dp','dp_method')
    def onchange_amount_dp(self):
        amount = 0
        values = {
            'total_amount_dp': 0,
            
        }
        if self.amount_dp and self.dp_method :
            if self.dp_method == 'percent':
                amount = (self.disc_pp_percent/100) * self.amount_before_discount
                amount_after = self.amount_before_discount - amount
                amount = (self.amount_dp/100) * amount_after
            elif self.dp_method == 'nominal':
                amount = self.amount_dp
            values['total_amount_dp'] = amount
            
        self.update(values)
    
    @api.multi
    @api.onchange('amount_dp_special','dp_method_special')
    def onchange_amount_dp_special(self):
        amount = 0
        values = {
            'total_amount_dp_special': 0,
            
        }
        if self.amount_dp_special and self.dp_method_special :
            if self.dp_method_special == 'percent':
                amount = (self.disc_pp_percent/100) * self.amount_before_discount
                amount_after = self.amount_before_discount - amount
                amount = (self.amount_dp_special/100) * amount_after
            elif self.dp_method_special == 'nominal':
                amount = self.amount_dp_special
            values['total_amount_dp_special'] = amount
            
        self.update(values)

class property_order_line(models.Model):
    _name ="property.order.line"

    property_unit_id = fields.Many2one (comodel_name="property.unit", string="Unit")
    description      = fields.Char(string="Deskripsi")
    back_date        = fields.Boolean(string="Track Harga Lama")
    old_price_date   = fields.Date(string="Tanggal Track Harga")
    unit_price       = fields.Float(string="Harga Unit")
    tax_id           = fields.Many2one(comodel_name="account.tax", string="Pajak")
    subtotal         = fields.Float(string="Total Harga")
    order_id         = fields.Many2one(comodel_name="property.sale", string="Order ID")


ooconfirm =[('draft','Draft'),('confirm','Confirm'),('paid','Paid'),('cancel','Cancel')]
class property_payment_line(models.Model):
    _name ="property.payment.line"

    date_due            = fields.Date(string="Tanggal Pembayaran")
    property_unit_id    = fields.Many2one(comodel_name="property.unit", string="Unit")
    description         = fields.Char(string="Deskripsi")
    use_nota_kredit     = fields.Boolean(string="Pakai Nota Kredit")
    amount_nota_kredit  = fields.Float(string="Total Nota Kredit")
    amount_total        = fields.Float(string="Total Harga")
    amount              = fields.Float(string="Harga Pokok")
    amount_interest     = fields.Float(string="Bunga")
    amount_invoiced     = fields.Float(string="Harga Penagihan")
    amount_outstanding  = fields.Float(string="Harga Belum Bayar")
    amount_paid         = fields.Float(string="Harga Sudah Bayar")
    invoice_id          = fields.Many2one(comodel_name="account.invoice", string="ID Invoice")
    nota_kredit_id      = fields.Many2one(comodel_name="nota.kredit", string="ID Nota Kredit")
    order_id            = fields.Many2one(comodel_name="property.sale", string="Order ID")
    state               = fields.Selection(string="Status", selection=ooconfirm, required=True,readonly=True,default=confirm[0][0])



