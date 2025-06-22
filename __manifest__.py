{
    "name": "Taller Mecánico Plus",
    "version": "1.0",
    "depends": ["base", "fleet", "product"],
    "author": "Tu Nombre",
    "category": "Services",
    "description": "Gestión de órdenes de trabajo de taller con integración VIN",
    "data": [
        "security/ir.model.access.csv",
        "data/orden_trabajo_sequence.xml",
        "report/report_action.xml",
        "report/orden_trabajo_report.xml",
        "views/fleet_vehicle_views.xml",
        "views/orden_trabajo_views.xml",
        "views/orden_trabajo_graph_views.xml",
    ],
    "installable": True,
    "application": True,
}
