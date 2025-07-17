import os
import datetime
from pyafipws.wsfev1 import WSFEv1

# Crear carpeta de salida
output_dir = "comprobantes"
os.makedirs(output_dir, exist_ok=True)

# Fechas del mes pasado
hoy = datetime.date.today()
primero_mes_actual = hoy.replace(day=1)
ultimo_dia_mes_pasado = primero_mes_actual - datetime.timedelta(days=1)
primero_dia_mes_pasado = ultimo_dia_mes_pasado.replace(day=1)

fecha_desde = primero_dia_mes_pasado.strftime("%Y%m%d")
fecha_hasta = ultimo_dia_mes_pasado.strftime("%Y%m%d")
mes_anio = primero_dia_mes_pasado.strftime("%Y-%m")


# Leer lista de CUITs
with open("cuit_list.txt") as f:
    cuits = [line.strip() for line in f if line.strip()]

for cuit in cuits:
    print(f"\n[{datetime.datetime.now()}] 🔎 Procesando CUIT NUM.: {cuit}")
    cert = f"certificados/{cuit}.crt"
    key = f"certificados/{cuit}.key"

    if not (os.path.isfile(cert) and os.path.isfile(key)):
        print(f" Certificados no encontrados para CUIT {cuit}. Saltando...")
        continue

    try:
        fe = WSFEv1()
        fe.Cuit = int(cuit)
        fe.Certificado = cert
        fe.ClavePrivada = key
        fe.Conectar()

        for tipo_cbte in [1, 6, 11]:  # Factura A, B, C
            punto_venta = 1
            ultimo = fe.CompUltimoAutorizado(punto_venta, tipo_cbte)

            for nro_cbte in range(1, ultimo + 1):
                if fe.CompConsultar(str(tipo_cbte), str(punto_venta), str(nro_cbte)):
                    cbte_fecha = str(fe.CbteFch) if fe.CbteFch else ""
                    if fecha_desde <= cbte_fecha <= fecha_hasta:
                        filename = f"{output_dir}/emitido_{cuit}_{tipo_cbte}_{nro_cbte}_{mes_anio}.xml"
                        

                        with open(filename, "w", encoding="utf-8") as f_xml:
                            f_xml.write(fe.xml_request)

        print("✅ Comprobantes emitidos descargados.")
    except Exception as e:
        print(f"❗ Error en comprobantes emitidos para CUIT {cuit}: {e}")
