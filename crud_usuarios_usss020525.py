from mysql.connector.errors import Error
import hashlib
import conexion

# La tabla usuarios vive en db_sistema_impuestos (según el enunciado del parcial)
db = conexion.Conexion('db_sistema_impuestos')


def cifrar(clave):
    # MD5 hexadecimal = 32 caracteres, cabe en clave char(35)
    return hashlib.md5(str(clave).encode('utf-8')).hexdigest()


class crud_usuarios_usss020525:
    def consultar(self, buscar):
        # Nunca se devuelve la clave al navegador
        return db.consultar(
            "SELECT idUsuario,usuario,nombre,direccion,telefono "
            "FROM usuarios_usss020525 WHERE usuario LIKE %s OR nombre LIKE %s "
            "ORDER BY usuario",
            (f"%{buscar}%", f"%{buscar}%")
        )

    def administrar(self, datos):
        try:
            accion = datos.get('accion')

            if accion in ('nuevo', 'modificar'):
                usuario = str(datos.get('usuario', '')).strip()
                clave = str(datos.get('clave', ''))
                if not usuario:
                    return 'Ingrese el usuario.'

                # usuario único
                existe = db.consultar(
                    "SELECT idUsuario FROM usuarios_usss020525 WHERE usuario=%s AND idUsuario<>%s",
                    (usuario, datos.get('idUsuario') or 0))
                if existe:
                    return 'El usuario ya existe.'

            if accion == 'nuevo':
                if not clave:
                    return 'Ingrese la clave.'
                sql = """
                    INSERT INTO usuarios_usss020525(usuario,clave,nombre,direccion,telefono)
                    VALUES(%s,%s,%s,%s,%s)
                """
                valores = (usuario, cifrar(clave), datos['nombre'], datos['direccion'], datos['telefono'])
            elif accion == 'modificar':
                if clave:
                    sql = """
                        UPDATE usuarios_usss020525 SET usuario=%s,clave=%s,nombre=%s,direccion=%s,telefono=%s
                        WHERE idUsuario=%s
                    """
                    valores = (usuario, cifrar(clave), datos['nombre'], datos['direccion'],
                               datos['telefono'], datos['idUsuario'])
                else:
                    # clave vacía = conservar la clave actual
                    sql = """
                        UPDATE usuarios_usss020525 SET usuario=%s,nombre=%s,direccion=%s,telefono=%s
                        WHERE idUsuario=%s
                    """
                    valores = (usuario, datos['nombre'], datos['direccion'],
                               datos['telefono'], datos['idUsuario'])
            elif accion == 'eliminar':
                sql = """
                    DELETE FROM usuarios_usss020525 WHERE idUsuario=%s
                """
                valores = (datos['idUsuario'],)
            else:
                return "Error: accion no valida"
            return db.ejecutar(sql, valores)
        except Error as e:
            return f"Error al guardar el usuario: {e}"

    def login(self, usuario, clave):
        # Devuelve el usuario si existe y la clave coincide; si no, None
        filas = db.consultar(
            "SELECT idUsuario,usuario,nombre FROM usuarios_usss020525 "
            "WHERE usuario=%s AND clave=%s",
            (str(usuario or '').strip(), cifrar(clave or '')))
        return filas[0] if filas else None
