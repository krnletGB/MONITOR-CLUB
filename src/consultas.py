
# =========================================================
# CONSULTAS, IDENTICAS A POWER BI
# =========================================================
CONSULTA_VENTA_CLUB = """
SELECT
    Fecha,
    Nombre,
    Tipo,
    Cve_Sucursal,
    Venta_Neta
FROM dbo.IA_VENTA_CLUB
WHERE Fecha >= '2024-01-01'
"""


CONSULTA_DETALLE_CLUB = """
SELECT
    Cve_Cliente,
    NoTarjeta,
    Nombre,
    Nombre_Completo,
    Fecha_Vencimiento,
    Fecha_Alta,
    Fecha_Ult_Modif,
    cluster_ia,
    subcluster_ia,
    AceptaApp,
    FechaAceptacionApp,
    acepta_condiciones,
    cliente_plus,
    saldo,
    nombre_cluster,
    limite_bonificacion,
    Cve_Categoria,
    Categoria,
    Fecha_Compra,
    Anio,
    Remision,
    Cve_Sucursal,
    Caja,
    PorcentajeClubPrecios,
    Cve_Producto,
    Cve_Presentacion,
    Cve_Movimiento,
    Cve_Campaña,
    Descuento_ClubPrecios,
    Aportar,
    Cantidad,
    Importe_Neto,
    TotalDescuentos,
    importeclubprecios,
    sucursal,
    Categoria_GB,
    Descripcion,
    Nombres_Agrupado,
    Costo_Promedio_Real,
    Costo_Promedio_Real_gral,
    CP_Real,
    CP_Real_Gral
FROM dbo.tarjetas_vigentes_club_nuevos_clusters

"""


CONSULTA_CLIENTES_APP = """
SELECT
    Cve_Cliente,
    NoTarjeta,
    Nombre_Completo,
    acepta_noti,
    PushToken,
    Acepta_condiciones,
    AceptaApp,
    Fecha_Vencimiento
FROM dbo.CLIENTES_QUE_USAN_APP
"""