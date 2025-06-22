import requests
from odoo import models, fields, api
from odoo.exceptions import UserError

def get_vehicle_info_by_vin(vin):
    try:
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        results = response.json().get('Results', [])
        return {r['Variable']: r['Value'] for r in results if r['Value']}
    except Exception as e:
        raise UserError(f"No se pudo obtener información del vehículo: {str(e)}")


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    vin = fields.Char(string='VIN')
    year = fields.Char(string='Año del Modelo')

    def autocomplete_vehicle_info(self):
        for vehicle in self:
            if not vehicle.vin:
                raise UserError("El campo VIN está vacío.")

            info = get_vehicle_info_by_vin(vehicle.vin)

            # Mapea los campos comunes
            if 'Model' in info:
                vehicle.model_id = self.env['fleet.vehicle.model'].search([('name', '=', info['Model'])], limit=1).id
            if 'Make' in info:
                brand = self.env['fleet.vehicle.model.brand'].search([('name', '=', info['Make'])], limit=1)
                if not brand:
                    brand = self.env['fleet.vehicle.model.brand'].create({'name': info['Make']})
                vehicle.brand_id = brand.id
            if 'Model Year' in info:
                vehicle.year = info['Model Year']

