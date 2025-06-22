import logging

import requests
from odoo import api, fields, models
from odoo.exceptions import UserError
from requests.exceptions import ConnectionError, RequestException, Timeout


def get_vehicle_info_by_vin(vin, env=None):
    if not vin or not env:
        return {}

    # Buscar en caché
    # cache = env["vehicle.vin.cache"].search([("vin", "=", vin)], limit=1)
    # if cache:
    #     return cache.data

    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vin}?format=json"

    try:
        response = requests.get(url, timeout=5)  # Timeout de 5 segundos
        response.raise_for_status()  # Lanza HTTPError si status no es 2xx

        data = response.json()

        if not data.get("Results") or not isinstance(data["Results"], list):
            raise Exception("Respuesta inválida de la API")

        parsed = data["Results"][0]
        _logger = logging.getLogger(__name__)
        _logger.info("VIN parsed result: %s", parsed)

        # Guardar en caché
        env["vehicle.vin.cache"].create(
            {
                "vin": vin,
                "data": parsed,
            }
        )

        return parsed

    except Timeout:
        raise Exception("La solicitud al servicio de VIN excedió el tiempo de espera.")
    except ConnectionError:
        raise Exception("No se pudo conectar con el servicio externo de VIN.")
    except RequestException as e:
        raise Exception(f"Error en la solicitud HTTP: {str(e)}")
    except Exception as e:
        raise Exception(f"Error procesando la respuesta de VIN: {str(e)}")


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    vin = fields.Char(string="VIN")
    year = fields.Char(string="Año del Modelo")
    body_class = fields.Char(string="Carrocería")
    fuel_type = fields.Char(string="Tipo de Combustible")
    transmission = fields.Char(string="Transmisión")

    def autocomplete_vehicle_info(self):
        for vehicle in self:
            if not vehicle.vin:
                raise UserError("El campo VIN está vacío.")

            info = get_vehicle_info_by_vin(vehicle.vin, env=self.env)

            if info.get("Model"):
                model = self.env["fleet.vehicle.model"].search(
                    [("name", "=", info["Model"])], limit=1
                )
                if model:
                    vehicle.model_id = model.id

            if info.get("Make"):
                brand = self.env["fleet.vehicle.model.brand"].search(
                    [("name", "=", info["Make"])], limit=1
                )
                if not brand:
                    brand = self.env["fleet.vehicle.model.brand"].create(
                        {"name": info["Make"]}
                    )
                vehicle.brand_id = brand.id

            vehicle.year = str(info.get("ModelYear") or "")
            vehicle.body_class = info.get("Body Class") or ""
            vehicle.fuel_type = info.get("Fuel Type - Primary") or ""
            vehicle.transmission = info.get("Transmission Style") or ""
