from odoo import models, fields, api, _
from .vehicle_integration import get_vehicle_info_by_vin

class OrdenTrabajo(models.Model):
    _name = 'orden.trabajo'
    _description = 'Orden de Trabajo'

    name = fields.Char(string='Número de Orden', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    vin = fields.Char(string='VIN', required=True)
    cliente_id = fields.Many2one('res.partner', string='Cliente', required=True)
    fecha = fields.Datetime(string='Fecha', default=fields.Datetime.now)
    vehiculo_id = fields.Many2one('fleet.vehicle', string='Vehículo')
    descripcion = fields.Text(string='Descripción')
    estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado')
    ], default='pendiente')
    items_ids = fields.One2many('orden.trabajo.item', 'orden_id', string='Items de Trabajo')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('orden.trabajo.seq') or _('New')

        vin = vals.get('vin')
        if vin:
            info = get_vehicle_info_by_vin(vin)
            vehiculo_modelo = info.get('Model')
            vehiculo_marca = info.get('Make')
            vehiculo_anio = info.get('Model Year')

            brand = self.env['fleet.vehicle.model.brand'].search([('name', '=', vehiculo_marca)], limit=1)
            if not brand:
                brand = self.env['fleet.vehicle.model.brand'].create({'name': vehiculo_marca})

            modelo = self.env['fleet.vehicle.model'].search([
                ('name', '=', vehiculo_modelo),
                ('brand_id', '=', brand.id)
            ], limit=1)
            if not modelo:
                modelo = self.env['fleet.vehicle.model'].create({
                    'name': vehiculo_modelo,
                    'brand_id': brand.id
                })

            vehiculo = self.env['fleet.vehicle'].search([('vin', '=', vin)], limit=1)
            if not vehiculo:
                vehiculo = self.env['fleet.vehicle'].create({
                    'vin': vin,
                    'model_id': modelo.id,
                    'brand_id': brand.id,
                    'year': vehiculo_anio,
                    'name': f'{vehiculo_marca} {vehiculo_modelo} ({vehiculo_anio})'
                })

            vals['vehiculo_id'] = vehiculo.id

        return super().create(vals)


class OrdenTrabajoItem(models.Model):
    _name = 'orden.trabajo.item'
    _description = 'Item de Trabajo'

    orden_id = fields.Many2one('orden.trabajo', string='Orden de Trabajo')
    servicio_id = fields.Many2one('product.product', string='Servicio', required=True)
    cantidad = fields.Float(string='Cantidad', default=1.0)
    precio_unitario = fields.Float(string='Precio Unitario')

