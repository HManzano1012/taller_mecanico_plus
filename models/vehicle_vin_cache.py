class VehicleVinCache(models.Model):
    _name = "vehicle.vin.cache"
    _description = "Cache de VIN consultado"

    vin = fields.Char(required=True, index=True)
    data = fields.Json(required=True)
    fecha_consulta = fields.Datetime(default=fields.Datetime.now)
