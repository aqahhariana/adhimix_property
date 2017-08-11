from odoo import api,fields,models,_


class property_category(models.Model):
    _name ="property.category"

    code                            = fields.Char("Kode")
    name                            = fields.Char("Nama")
    type                            = fields.Selection([('landed_house','Landed House'),
                                                        ('apartement','Apartement'),
                                                        ('hotel','Hotel')], string="Tipe")
    property_receivable_account_id  = fields.Many2one(comodel_name="account.account", string="Account Receivable")
    property_cogs_account_id        = fields.Many2one(comodel_name="account.account", string="Account COGS")
    property_account_inventory_id   = fields.Many2one(comodel_name="account.account", string="Account Inventory")
    property_account_booking_fee_id = fields.Many2one("account.account", "Booking Fee")
    property_account_income_id      = fields.Many2one(comodel_name="account.account", string="Account Income")
    company_id     = fields.Many2one(comodel_name="res.company", string="Nama Company/Divisi")



class property_view(models.Model):
    _name ="property.view"

    name                    = fields.Char("Nama View")
    property_category_id    = fields.Many2one(comodel_name="property.category", string="Nama Cluster/Apartement/Hotel")
    company_id     = fields.Many2one(comodel_name="res.company", string="Nama Company/Divisi")


class property_floor(models.Model):
    _name ="property.floor"

    name                    = fields.Char("Nama Lantai")
    property_category_id    = fields.Many2one(comodel_name="property.category", string="Nama Cluster/Apartement/Hotel")
    company_id     = fields.Many2one(comodel_name="res.company", string="Nama Company/Divisi")


class property_tower(models.Model):
    _name ="property.tower"

    name                    = fields.Char("Nama Tower")
    property_category_id    = fields.Many2one(comodel_name="property.category", string="Nama Cluster/Apartement/Hotel")
    company_id     = fields.Many2one(comodel_name="res.company", string="Nama Company/Divisi")


class property_type(models.Model):
    _name ="property.type"

    name                    = fields.Char("Nama Type")
    property_category_id    = fields.Many2one(comodel_name="property.category", string="Nama Cluster/Apartement/Hotel")
    company_id     = fields.Many2one(comodel_name="res.company", string="Nama Company/Divisi")

class property_jenis(models.Model):
    _name ="property.jenis"

    name                    = fields.Char("Nama Jenis")
    property_category_id    = fields.Many2one(comodel_name="property.category", string="Nama Cluster/Apartement/Hotel")
    company_id     = fields.Many2one(comodel_name="res.company", string="Nama Company/Divisi")


class property_unit(models.Model):
    _name ="property.unit"
    
    def _get_pricelist(self):
        cursor = self.env.cr
        for line in self:
            cursor.execute("""
                select net_price 
                from property_unit_price 
                where property_unit_id= %s
                and date = (select max(date) from property_unit_price where property_unit_id= %s) 
                limit 1
            """,(line.id,line.id,))
            count = cursor.rowcount
            val = cursor.fetchall()
            if count > 0:
                price = val[0][0]
            else :
                price = 0
            line.current_pricelist = price
            

    name                    = fields.Char("Nama Property")
    type                            = fields.Selection([('landed_house','Landed House'),
                                                        ('apartement','Apartement'),
                                                        ('hotel','Hotel')], string="Tipe")
    address                 = fields.Char(string="Alamat")
    property_category_id    = fields.Many2one(comodel_name="property.category", string="Nama Cluster/Apartement/Hotel")
    property_view_id        = fields.Many2one(comodel_name="property.view", string="view")
    property_tower_id       = fields.Many2one(comodel_name="property.tower", string="Tower")
    property_type_id        = fields.Many2one("property.type", "Type Unit")
    property_floor_id       = fields.Many2one(comodel_name="property.floor", string="Lantai")
    property_jenis_id       = fields.Many2one(comodel_name="property.jenis", string="Jenis")
    direction               = fields.Selection([('north', 'Utara'),
                                                ('northwest','Barat Laut'),
                                                ('west', 'Barat'),
                                                ('southwest','Barat Daya'),
                                                ('south', 'Selatan'),
                                                ('southeast','Tenggara'),
                                                ('east', 'Timur'),
                                                ('northeast','Timur Laut'),
                                                ('none','-')], string="Arah")
    bulding_area     = fields.Float(string="Luas Bangunan (m2)")
    land_area        = fields.Float(string="Luas Tanah (m2)")
    nett_area     = fields.Float(string="Nett")
    semi_gross_area  = fields.Float(string="Semi Gross")
    price_ids        = fields.One2many(comodel_name="property.unit.price", inverse_name="property_unit_id", string="Daftar Harga")
    available        = fields.Boolean(string="Status Ketersediaan")
    status           = fields.Selection([('sale','Dapat Dijual'),('reserved','Reservasi'),('booked','Booking'),('owned','Sudah Dimiliki')],string="Status Property")
    owner_id         = fields.Many2one(comodel_name="res.partner", string="Nama Pemilik")
    company_id       = fields.Many2one(comodel_name="res.company", string="Nama Company/Divisi")
    rental_price_ids = fields.One2many(comodel_name="property.unit.rental.price", inverse_name="property_unit_id", string="Tarif Harga Sewa")
    is_rent          = fields.Boolean(string="Property Sewa")
    rent_available   = fields.Selection([('available','Tersedia'),('unvailable','Tidak Tersedia')])
    current_pricelist = fields.Float(string='Harga Jual Sekarang', compute="_get_pricelist", readonly=True, copy=False)



class property_unit_price(models.Model):
    _name ="property.unit.price"

    date                = fields.Date("Tanggal")
    property_unit_id    = fields.Many2one(comodel_name="property.unit", string="ID Unit")
    name                = fields.Char("Deskripsi")
    net_price           = fields.Float("Harga")



class property_unit_rental_price(models.Model):
    _name ="property.unit.rental.price"

    date             = fields.Date(string="Tanggal")
    price            = fields.Float(string="Harga")
    pricing_type     = fields.Selection([('daily','Harian'),('monthly','Bulanan'),('weekly','Mingguan')], string="Tipe Harga")
    deskripsi        = fields.Char(string="Deskripsi")
    property_unit_id = fields.Many2one(comodel_name="property.unit", string="Property Unit")
    
    