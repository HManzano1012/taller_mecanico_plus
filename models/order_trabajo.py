from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .vehicle_integration import get_vehicle_info_by_vin


class OrdenTrabajo(models.Model):
    _name = "orden.trabajo"
    _description = "Orden de Trabajo"

    name = fields.Char(
        string="Número de Orden",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )
    vin = fields.Char(string="VIN", required=True)
    cliente_id = fields.Many2one("res.partner", string="Cliente", required=True)
    fecha = fields.Datetime(
        string="Fecha", default=fields.Datetime.now, required=True, readonly=True
    )
    descripcion = fields.Text(string="Descripción", required=True)
    placa = fields.Char(string="Placa del Vehículo", required=True)

    # Datos técnicos del vehículo
    vehiculo_marca = fields.Char(string="Marca del vehículo", required=True)
    vehiculo_modelo = fields.Char(string="Modelo del vehículo", required=True)
    vehiculo_anio = fields.Char(string="Año del vehículo", required=True)
    vehiculo_carroceria = fields.Char(string="Carrocería")
    vehiculo_combustible = fields.Char(string="Combustible")
    vehiculo_transmision = fields.Char(string="Transmisión")

    estado = fields.Selection(
        [
            ("pendiente", "Pendiente"),
            ("en_proceso", "En Proceso"),
            ("completado", "Completado"),
        ],
        default="pendiente",
    )
    items_ids = fields.One2many(
        "orden.trabajo.item", "orden_id", string="Items de Trabajo"
    )

    @api.onchange("vin")
    def _onchange_vin(self):
        if self.vin:
            try:
                info = get_vehicle_info_by_vin(self.vin, env=self.env)
                if not info:
                    return {
                        "warning": {
                            "title": "VIN no encontrado",
                            "message": "No se encontró información para el VIN ingresado.",
                            "type": "notification",
                        }
                    }

                self.vehiculo_marca = info.get("Make")
                self.vehiculo_modelo = info.get("Model")
                self.vehiculo_anio = info.get("ModelYear")
                self.vehiculo_carroceria = info.get("BodyClass")
                self.vehiculo_combustible = info.get("FuelTypePrimary")
                self.vehiculo_transmision = info.get("TransmissionStyle")

                self.descripcion = " • ".join(
                    filter(
                        None,
                        [
                            self.vehiculo_marca,
                            self.vehiculo_modelo,
                            self.vehiculo_anio,
                            self.vehiculo_carroceria,
                            self.vehiculo_combustible,
                            self.vehiculo_transmision,
                        ],
                    )
                )
            except Exception as e:
                return {
                    "warning": {
                        "title": "Error al consultar VIN",
                        "message": str(e),
                        "type": "notification",
                    }
                }

    def action_buscar_vehiculo_por_vin(self):
        for orden in self:
            if not orden.vin:
                raise UserError("Debe ingresar un VIN antes de buscar.")

            try:
                info = get_vehicle_info_by_vin(orden.vin, env=self.env)
                if not info:
                    raise UserError("No se encontró información para el VIN ingresado.")

                orden.vehiculo_marca = info.get("Make")
                orden.vehiculo_modelo = info.get("Model")
                orden.vehiculo_anio = info.get("ModelYear")
                orden.vehiculo_carroceria = info.get("BodyClass")
                orden.vehiculo_combustible = info.get("FuelTypePrimary")
                orden.vehiculo_transmision = info.get("TransmissionStyle")

                orden.descripcion = " • ".join(
                    filter(
                        None,
                        [
                            orden.vehiculo_marca,
                            orden.vehiculo_modelo,
                            orden.vehiculo_anio,
                            orden.vehiculo_carroceria,
                            orden.vehiculo_combustible,
                            orden.vehiculo_transmision,
                        ],
                    )
                )
            except Exception as e:
                raise UserError(f"No se pudo consultar el VIN: {str(e)}")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vin = vals.get("vin")
            if vin:
                try:
                    info = get_vehicle_info_by_vin(vin, env=self.env)
                    if not info:
                        raise UserError(
                            "No se encontró información para el VIN ingresado."
                        )

                    vals["vehiculo_marca"] = info.get("Make", "Desconocida")
                    vals["vehiculo_modelo"] = info.get("Model", "Desconocido")
                    vals["vehiculo_anio"] = info.get("ModelYear", "Desconocido")
                    vals["vehiculo_carroceria"] = info.get("Body Class")
                    vals["vehiculo_combustible"] = info.get("Fuel Type - Primary")
                    vals["vehiculo_transmision"] = info.get("Transmission Style")

                    vals["descripcion"] = " • ".join(
                        filter(
                            None,
                            [
                                vals["vehiculo_marca"],
                                vals["vehiculo_modelo"],
                                vals["vehiculo_anio"],
                                vals["vehiculo_carroceria"],
                                vals["vehiculo_combustible"],
                                vals["vehiculo_transmision"],
                            ],
                        )
                    )
                except Exception as e:
                    raise UserError(f"Error al consultar el VIN: {str(e)}")

            for field in ["vin", "vehiculo_marca", "vehiculo_modelo", "vehiculo_anio"]:
                if not vals.get(field):
                    raise UserError(
                        _(f"El campo '{field}' es obligatorio para crear la orden.")
                    )

            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "orden.trabajo.seq"
                ) or _("New")

        return super().create(vals_list)


class OrdenTrabajoItem(models.Model):
    _name = "orden.trabajo.item"
    _description = "Item de Trabajo"

    orden_id = fields.Many2one("orden.trabajo", string="Orden de Trabajo")
    servicio_id = fields.Many2one("product.product", string="Servicio", required=True)
    cantidad = fields.Float(string="Cantidad", default=1.0)
    precio_unitario = fields.Float(string="Precio Unitario")
