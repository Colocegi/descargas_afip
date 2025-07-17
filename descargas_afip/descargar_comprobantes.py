import os
import datetime
import traceback
from pyafipws.wsfev1 import WSFEv1

# Obtener el directorio del script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Crear carpeta de salida
output_dir = os.path.join(script_dir, "comprobantes")
os.makedirs(output_dir, exist_ok=True)

# Fechas del mes pasado
hoy = datetime.date.today()
primero_mes_actual = hoy.replace(day=1)
ultimo_dia_mes_pasado = primero_mes_actual - datetime.timedelta(days=1)
primero_dia_mes_pasado = ultimo_dia_mes_pasado.replace(day=1)

fecha_desde = primero_dia_mes_pasado.strftime("%Y%m%d")
fecha_hasta = ultimo_dia_mes_pasado.strftime("%Y%m%d")
mes_anio = primero_dia_mes_pasado.strftime("%Y-%m")

print(f"Descargando comprobantes del período: {fecha_desde} al {fecha_hasta}")
print(f" Guardando en: {output_dir}")
print(f" Mes/Año: {mes_anio}")
print("=" * 50)


def log_error(context, error):
    print(f" ERROR en {context}: {error}")
    print(traceback.format_exc())


# Leer lista de CUITs
try:
    with open(os.path.join(script_dir, "cuit_list.txt")) as f:
        cuits = [line.strip() for line in f if line.strip()]
except Exception as e:
    log_error("lectura de cuit_list.txt", e)
    exit(1)

for cuit in cuits:
    print(f"\n[{datetime.datetime.now()}] 🔎 Procesando CUIT NUM.: {cuit}")
    cert = os.path.join(script_dir, "certificados", f"{cuit}.crt")
    key = os.path.join(script_dir, "certificados", f"{cuit}.key")
    
    # Si no existe el .crt, intentar con .csr como respaldo
    if not os.path.isfile(cert):
        cert = os.path.join(script_dir, "certificados", f"{cuit}.csr")

    if not (os.path.isfile(cert) and os.path.isfile(key)):
        available_files = os.listdir(os.path.join(script_dir, "certificados"))
        log_error(f"verificación de archivos de certificado para CUIT {cuit}", 
                 f"Certificados no encontrados. Archivos disponibles: {available_files}")
        continue

    try:
        fe = WSFEv1()
        try:
            fe.Cuit = int(cuit)
            fe.Certificado = cert
            fe.ClavePrivada = key
        except Exception as e:
            log_error(f"asignación de credenciales para CUIT {cuit}", e)
            continue

        try:
            fe.Conectar()
        except Exception as e:
            log_error(f"conexión a AFIP para CUIT {cuit}", e)
            continue

        for tipo_cbte in [1, 6, 11]:  # Factura A, B, C
            punto_venta = 1
            try:
                ultimo = fe.CompUltimoAutorizado(punto_venta, tipo_cbte)
                ultimo = int(ultimo) if ultimo else 0
                print(f"  Tipo {tipo_cbte}: último comprobante autorizado = {ultimo}")
            except Exception as e:
                log_error(f"obtención del último comprobante autorizado (CUIT {cuit}, Tipo {tipo_cbte})", e)
                continue

            comprobantes_encontrados = 0
            comprobantes_descargados = 0
            
            for nro_cbte in range(1, ultimo + 1):
                try:
                    if fe.CompConsultar(str(tipo_cbte), str(punto_venta), str(nro_cbte)):
                        comprobantes_encontrados += 1
                        cbte_fecha = str(fe.CbteFch) if fe.CbteFch else ""
                        if fecha_desde <= cbte_fecha <= fecha_hasta:
                            filename = os.path.join(output_dir, f"emitido_{cuit}{tipo_cbte}{nro_cbte}_{mes_anio}.xml")
                            try:
                                with open(filename, "w", encoding="utf-8") as f_xml:
                                    f_xml.write(fe.xml_request)
                                comprobantes_descargados += 1
                            except Exception as e:
                                log_error(f"escritura de archivo XML {filename}", e)
                        # else: comprobante fuera del rango de fechas
                    # else: comprobante no existe o no autorizado, se ignora silenciosamente
                except Exception as e:
                    log_error(f"consulta del comprobante (CUIT {cuit}, Tipo {tipo_cbte}, Nro {nro_cbte})", e)
            
            print(f"   Tipo {tipo_cbte}: {comprobantes_encontrados} encontrados, {comprobantes_descargados} descargados")

        print(" Comprobantes emitidos descargados.")
    except Exception as e:
        log_error(f"proceso general para CUIT {cuit}", e)
