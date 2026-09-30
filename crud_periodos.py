from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_HALF_UP
from datetime import datetime
import conexion

db = conexion.Conexion()
usuario = 'admin'
DOS = Decimal('0.01')
SEIS = Decimal('0.000001')
MIL = Decimal('1000')


def fecha(texto):
    try:
        return datetime.strptime(str(texto), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


class crud_periodos:

    # ---------- Catálogos ----------
    def productos(self):
        return db.consultar(
            "SELECT idProducto, codigo, nombre FROM productos "
            "WHERE codigo IN ('11801','11802')"
        )

    def clientes_empresa(self):
        return db.consultar(
            "SELECT idCliente, codigo, nombre FROM clientes WHERE tipo='empresa'"
        )

    # ---------- Consulta ----------
    def consultar(self, idCliente):
        return db.consultar("""
            SELECT p.*, pr.codigo AS codigoProducto, pr.nombre AS nombreProducto
            FROM periodos p
            INNER JOIN productos pr ON pr.idProducto = p.idProducto
            WHERE p.idCliente = %s
            ORDER BY p.desde
        """, (idCliente,))

    # ---------- Cálculo ----------
    def calcular(self, idCliente, idProducto, monto, desde):
        # Normalizar monto
        try:
            monto = Decimal(str(monto))
        except (InvalidOperation, TypeError):
            monto = Decimal(0)
        if monto <= 0:
            return {'msg': 'Ingrese un balance mayor que cero.'}
        if not idProducto:
            return {'msg': 'Confirme si la actividad corresponde a comercio o industria.'}

        inicio = fecha(desde)
        if not inicio:
            return {'msg': 'Ingrese la fecha Desde.'}

        # RF 10: límites inclusivos  TarifaDesde <= Balance <= TarifaHasta
        tarifas = db.consultar("""
            SELECT * FROM tarifas
            WHERE idProducto = %s
              AND desde <= %s AND %s <= hasta
              AND vigenteDesde <= %s
              AND (vigenteHasta IS NULL OR vigenteHasta > %s)
        """, (idProducto, monto, monto, inicio, inicio))

        if not tarifas:
            return {'msg': 'No existe una tarifa configurada para el balance indicado.'}
        if len(tarifas) > 1:
            return {'msg': 'Existe más de una tarifa aplicable. Corrija la tabla tarifaria.'}
        t = tarifas[0]

        # Normalizar campos numéricos de la tarifa
        precio_base = Decimal(str(t['precioBase'] or 0))
        adicional   = Decimal(str(t['adicional']   or 0))
        porcentaje  = Decimal(str(t['porcentaje']  or 0))
        tarifa_desde = Decimal(str(t['desde']))
        tarifa_hasta = Decimal(str(t['hasta']))

        excedente = Decimal(0)
        bloques = 0

        if porcentaje > 0:
            # RF 10.4 tarifa porcentual
            precio = monto * porcentaje / Decimal('100')
            formula = 'PORCENTAJE_V1'
        else:
            # RF 10.1 tarifa por bloques CEIL
            excedente = monto - tarifa_desde
            if excedente < 0:
                excedente = Decimal(0)
            bloques = int((excedente / MIL).to_integral_value(rounding=ROUND_CEILING))
            precio = precio_base + bloques * adicional
            formula = 'BLOQUES_V2'

        precio = precio.quantize(SEIS, ROUND_HALF_UP)

        resultado = {
            'msg': 'ok',
            'idTarifa': t['idTarifa'],
            'tarifaDesde': tarifa_desde,
            'tarifaHasta': tarifa_hasta,
            'precioBase': precio_base,
            'adicional': adicional,
            'porcentaje': porcentaje,
            'excedente': excedente,
            'bloques': bloques,
            'precio': precio,
            'precioMensual': precio.quantize(DOS, ROUND_HALF_UP),
            'formula': formula,
        }

        # RF 06 aviso de hueco
        if idCliente:
            anterior = db.consultar(
                "SELECT MAX(hasta) AS hasta FROM periodos "
                "WHERE idCliente=%s AND idProducto=%s AND hasta<=%s",
                (idCliente, idProducto, inicio))
            if anterior and anterior[0]['hasta'] and anterior[0]['hasta'] < inicio:
                resultado['aviso'] = (
                    f"Existe un espacio sin cobertura entre "
                    f"{anterior[0]['hasta']} y {inicio}."
                )
        return resultado

    # ---------- Administración ----------
    def administrar(self, datos):
        accion = datos.get('accion')

        if accion == 'eliminar':
            p = db.consultar(
                "SELECT facturado FROM periodos WHERE idPeriodo=%s",
                (datos['idPeriodo'],))
            if p and p[0]['facturado']:
                return 'El período ya fue utilizado en recibos y no puede eliminarse.'
            return db.ejecutar(
                "DELETE FROM periodos WHERE idPeriodo=%s",
                (datos['idPeriodo'],))

        if accion != 'nuevo':
            return 'Error: accion no valida'

        # RF: cliente empresa
        cliente = db.consultar(
            "SELECT tipo FROM clientes WHERE idCliente=%s",
            (datos['idCliente'],))
        if not cliente or cliente[0]['tipo'] != 'empresa':
            return ('El Impuesto a las Actividades Económicas '
                    'requiere un cliente de tipo empresa.')

        # Fechas
        desde, hasta = fecha(datos['desde']), fecha(datos['hasta'])
        if not desde or not hasta or desde >= hasta:
            return 'La fecha Hasta debe ser posterior a la fecha Desde.'

        # Cálculo
        calculo = self.calcular(
            datos['idCliente'], datos['idProducto'],
            datos['monto'], datos['desde'])
        if calculo['msg'] != 'ok':
            return calculo['msg']

        # RF 04 superposición
        cruce = db.consultar("""
            SELECT idPeriodo FROM periodos
            WHERE idCliente=%s AND idProducto=%s
              AND desde<%s AND hasta>%s
        """, (datos['idCliente'], datos['idProducto'], hasta, desde))
        if cruce:
            return 'El período indicado se superpone con un período existente.'

        # Cálculo de subtotal
        cantidad = Decimal(str(datos.get('cantidad') or 1))
        subtotal = (cantidad * calculo['precio']).quantize(DOS, ROUND_HALF_UP)

        sql = """
            INSERT INTO periodos
              (idCliente,idProducto,idTarifa,desde,hasta,monto,cantidad,
               precio,subtotal,formula,
               tarifaDesde,tarifaHasta,precioBase,adicional,porcentaje,
               excedente,bloques,usuario,fechaCalculo)
            VALUES
              (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
               %s,%s,%s,%s,%s,%s,%s,%s,NOW())
        """
        valores = (
            datos['idCliente'], datos['idProducto'], calculo['idTarifa'],
            desde, hasta, Decimal(str(datos['monto'])), cantidad,
            calculo['precio'], subtotal, calculo['formula'],
            calculo['tarifaDesde'], calculo['tarifaHasta'],
            calculo['precioBase'], calculo['adicional'], calculo['porcentaje'],
            calculo['excedente'], calculo['bloques'], usuario
        )
        return db.ejecutar(sql, valores)

    # ---------- Cobro ----------
    def cargo(self, idCliente, idProducto, desde, hasta):
        d, h = fecha(desde), fecha(hasta)
        if not d or not h or d >= h:
            return {'msg': 'La fecha Hasta debe ser posterior a la fecha Desde.'}

        periodos = db.consultar("""
            SELECT desde, hasta, cantidad, precio FROM periodos
            WHERE idCliente=%s AND idProducto=%s
              AND desde<%s AND hasta>%s
            ORDER BY desde
        """, (idCliente, idProducto, h, d))

        if not periodos:
            return {'msg': 'No existen períodos vigentes en el rango indicado.',
                    'detalle': [], 'total': Decimal(0)}

        detalle, total = [], Decimal(0)
        for p in periodos:
            inicio, fin = max(d, p['desde']), min(h, p['hasta'])
            meses = (fin.year - inicio.year) * 12 + fin.month - inicio.month
            importe = (Decimal(str(p['cantidad'])) *
                       Decimal(str(p['precio'])) *
                       Decimal(meses)).quantize(DOS, ROUND_HALF_UP)
            total += importe
            detalle.append({
                'desde': inicio, 'hasta': fin, 'meses': meses,
                'precio': p['precio'], 'importe': importe
            })
        return {'msg': 'ok', 'detalle': detalle, 'total': total}