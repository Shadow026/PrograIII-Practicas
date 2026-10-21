from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from decimal import Decimal
import os
import crud_clientes
import crud_periodos
import crud_usuarios_usss020525
from http.cookies import SimpleCookie
import secrets
import json

# Fuerza el cwd al directorio del script
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"Sirviendo desde: {os.getcwd()}")

port = 3000
crudClientes = crud_clientes.crud_clientes()
crudPeriodos = crud_periodos.crud_periodos()
crudUsuarios = crud_usuarios_usss020525.crud_usuarios_usss020525()

# Sesiones activas: token -> datos del usuario (se pierden al reiniciar el servidor)
sesiones = {}
RUTAS_API = {'/clientes', '/periodos', '/productos', '/clientes-empresa', '/usuarios'}


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

    def _json(self, payload, status=200, cabeceras=None):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        for nombre, valor in (cabeceras or []):
            self.send_header(nombre, valor)
        self.end_headers()
        self.wfile.write(json.dumps(payload, cls=DecimalEncoder).encode("utf-8"))

    def _leer_body(self):
        longitud = int(self.headers.get('Content-Length', 0))
        if not longitud:
            return {}
        return json.loads(self.rfile.read(longitud).decode("utf-8"))

    # ---------- Sesión ----------
    def _token(self):
        c = SimpleCookie(self.headers.get('Cookie', ''))
        return c['sesion'].value if 'sesion' in c else None

    def _autenticado(self):
        return self._token() in sesiones

    def _redirigir(self, destino, cabeceras=None):
        self.send_response(302)
        self.send_header('Location', destino)
        for nombre, valor in (cabeceras or []):
            self.send_header(nombre, valor)
        self.end_headers()

    # ---------- POST ----------
    def do_POST(self):
        try:
            return self._post()
        except Exception as e:
            print(f"Error en POST {self.path}: {e}")
            return self._json({'msg': f'Error: {e}'}, 500)

    def _post(self):
        path = urlparse(self.path).path

        # Login: única ruta POST pública
        if path == "/login":
            datos = self._leer_body()
            user = crudUsuarios.login(datos.get('usuario'), datos.get('clave'))
            if not user:
                return self._json({'msg': 'Usuario o clave incorrectos. Acceso denegado.'}, 401)
            token = secrets.token_hex(16)
            sesiones[token] = user
            return self._json({'msg': 'ok', 'nombre': user['nombre']}, 200,
                              [('Set-Cookie', f'sesion={token}; Path=/; HttpOnly; SameSite=Strict')])

        if not self._autenticado():
            return self._json({'msg': 'Acceso denegado. Inicie sesión.'}, 401)

        if path == "/usuario":
            datos = self._leer_body()
            return self._json({'msg': crudUsuarios.administrar(datos)})

        if path == "/cliente":
            datos = self._leer_body()
            print(f"Guardando cliente - Accion: {datos.get('accion')}, Tipo: {datos.get('tipo')}")
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

        # El login es lo primero que se muestra al abrir el servidor
        if path in ("/", "/login.html"):
            self.path = "/login.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        if path == "/logout":
            sesiones.pop(self._token(), None)
            return self._redirigir('/login.html',
                                   [('Set-Cookie', 'sesion=; Path=/; Max-Age=0')])

        # Todo lo demás requiere sesión iniciada
        if not self._autenticado():
            if path in RUTAS_API:
                return self._json({'msg': 'Acceso denegado. Inicie sesión.'}, 401)
            return self._redirigir('/login.html')

        if path == "/usuarios":
            buscar = qs.get('buscar', [''])[0]
            return self._json(crudUsuarios.consultar(buscar) or [])

        if path == "/clientes":
            buscar = qs.get('buscar', [''])[0]
            return self._json(crudClientes.consultar(buscar) or [])

        if path == "/periodos":
            idCliente = qs.get('idCliente', [''])[0]
            return self._json(crudPeriodos.consultar(idCliente) or [])

        if path == "/productos":
            return self._json(crudPeriodos.productos() or [])

        if path == "/clientes-empresa":
            res = crudPeriodos.clientes_empresa()
            print(f"Clientes empresa encontrados: {len(res) if res else 0}")
            return self._json(res or [])

        return SimpleHTTPRequestHandler.do_GET(self)


print(f"Servidor corriendo en el puerto {port}")
server = HTTPServer(("localhost", port), miServidor)
server.serve_forever()