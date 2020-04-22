# See LICENSE file for full copyright and licensing details.
"""This Module Contain information related to freight Configration."""

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class FreightPort(models.Model):
    """Ports Details."""

    _name = 'freight.port'
    _description = 'Ports Details'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    country_id = fields.Many2one('res.country', string="Country")
    state_id = fields.Many2one('res.country.state', string='State',
                               domain="[('country_id', '=', country_id)]")
    is_land = fields.Boolean(string="Land")
    is_ocean = fields.Boolean(string="Ocean")
    is_air = fields.Boolean(string="Air")
    active = fields.Boolean(string='Active', default=True)

    @api.constrains('is_land', 'is_ocean', 'is_air')
    def _check_port(self):
        for port in self:
            if not port.is_land and not port.is_ocean and not port.is_air:
                raise Warning(_("Please Check at least one port !!"))


class FreightVessels(models.Model):
    """Vessels Details."""

    _name = 'freight.vessels'
    _description = 'Vessels(Boat) Details.'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    country_id = fields.Many2one('res.country', string="Country")
    note = fields.Text(string='Note')
    active = fields.Boolean(string='Active', default=True)
    transport = fields.Selection([('land', 'Land'),
                                  ('ocean', 'Ocean'),
                                  ('air', 'Air')],
                                 default="land")


class FreightAirline(models.Model):
    """Model for Airlines Details."""

    _name = 'freight.airline'
    _description = 'Airline Details'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    country_id = fields.Many2one('res.country', string="Country")
    icao = fields.Char(string="ICAO",
                       help="International Civil Aviation Organization")
    active = fields.Boolean(string='Active', default=True)


class FreightContainers(models.Model):
    """Container Details."""

    _name = 'freight.container'
    _description = 'Container Details'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    state = fields.Selection([('available', 'Available'),
                              ('reserve', 'Reserve')],
                             default='available')
    size = fields.Float(string='Size',
                        help="Maximum Size Handling Capacity")
    size_uom_id = fields.Many2one('uom.uom', string="Size UOM")
    volume = fields.Float(string='Volume',
                          help="Maximum Volume(M3) Handling Capacity")
    weight = fields.Float(string="Weight",
                          help="Maximum Weight(KG) Handling Capacity")
    is_container = fields.Boolean(string='Is Container?', default=True)

    @api.constrains('size', 'volume', 'weight')
    def _check_conatiner_capacity(self):
        for cont in self:
            if cont.size < 0.0 or cont.volume < 0.0 or cont.weight < 0.0:
                raise Warning(_("You can't enter negative value!!"))


# class FreightMoveType(models.Model):
#     """Freight Move Types."""

#     _name = 'freight.move.type'
#     _description = 'Freight Move Types'

#     name = fields.Char(string="Name")
#     code = fields.Char(string="Code")
#     active = fields.Boolean(string="Active", default=True)


class OperationPriceList(models.Model):
    """Operation PriceListing."""

    _name = 'operation.price.list'
    _description = 'Operation Price Listing'

    name = fields.Char('Name')
    volume_price = fields.Float("Volume Price", help="Per m3 Volume Price")
    weight_price = fields.Float("Weight Price", help="Per KG Weight Price")

    @api.constrains('volume_price', 'weight_price')
    def _check_price(self):
        for price_list in self:
            if price_list.volume_price < 0.0 or \
                    price_list.weight_price < 0.0:
                raise Warning("You can't enter the negative price !!")
