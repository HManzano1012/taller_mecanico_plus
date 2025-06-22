from odoo import fields, models


class OrdenTrabajoItem(models.Model):
    _name = "orden.trabajo.item"
    _description = "Item de Trabajo"

    orden_id = fields.Many2one(
        "orden.trabajo", string="Orden de Trabajo", required=True, ondelete="cascade"
    )
    servicio_id = fields.Many2one("product.product", string="Servicio", required=True)
    cantidad = fields.Float(string="Cantidad", default=1.0)
    precio_unitario = fields.Float(string="Precio Unitario")
