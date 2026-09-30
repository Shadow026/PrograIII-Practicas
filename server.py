from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from decimal import Decimal
import os
import crud_clientes
import crud_periodos
import json

# Fuerza el cwd al directorio del script
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"Sirviendo desde: {os.getcwd()}")

port = 3000
crudClientes = crud_clientes.crud_clientes()
crudPeriodos = crud_periodos.crud_periodos()


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if hasattr(o, 'isoformat'):
            return o.isoformat()
        return super().default(o)


class miServidor(SimpleHTTPRequestHandler):

    # ✅ CORREGIDO: dentro de la clase
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def _json(self, payload, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload, cls=DecimalEncoder).encode("utf-8"))

    def _leer_body(self):
        longitud = int(self.headers.get('Content-Length', 0))
        if not longitud:
            return {}
        return json.loads(self.rfile.read(longitud).decode("utf-8"))

    # ---------- POST ----------
    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/cliente":
            datos = self._leer_body()
            return self._json({'msg': crudClientes.administrar(datos)})

        if path == "/periodo":
            datos = self._leer_body()
            return self._json({'msg': crudPeriodos.administrar(datos)})

        if path == "/periodo/calcular":
            datos = self._leer_body()
            r = crudPeriodos.calcular(
                datos.get('idCliente'),
                datos.get('idProducto'),
                datos.get('monto'),
                datos.get('desde'))
            return self._json(r)

        if path == "/periodo/cargo":
            datos = self._leer_body()
            r = crudPeriodos.cargo(
                datos.get('idCliente'),
                datos.get('idProducto'),
                datos.get('desde'),
                datos.get('hasta'))
            return self._json(r)

        return self._json({'msg': 'Ruta no encontrada'}, 404)

    # ---------- GET ----------
    def do_GET(self):
        urlParse = urlparse(self.path)
        qs = parse_qs(urlParse.query)
        path = urlParse.path

        if path == "/clientes":
            buscar = qs.get('buscar', [''])[0]
            return self._json(crudClientes.consultar(buscar) or [])

        if path == "/periodos":
            idCliente = qs.get('idCliente', [''])[0]
            return self._json(crudPeriodos.consultar(idCliente) or [])

        if path == "/productos":
            return self._json(crudPeriodos.productos() or [])

        if path == "/clientes-empresa":
            return self._json(crudPeriodos.clientes_empresa() or [])

        if path == "/":
            self.path = "/index.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        return SimpleHTTPRequestHandler.do_GET(self)


print(f"Servidor corriendo en el puerto {port}")
server = HTTPServer(("localhost", port), miServidor)
server.serve_forever()