from mysql.connector.errors import Error
import conexion

db = conexion.Conexion()

class crud_clientes:
    def consultar(self, buscar):
        return db.consultar(
            "SELECT * FROM clientes WHERE nombre LIKE %s OR codigo LIKE %s",
            (f"%{buscar}%", f"%{buscar}%")
        )

    def administrar(self, datos):
        try:
            # Normalizar el tipo para evitar inconsistencias en el filtrado
            tipo_normalizado = str(datos.get('tipo', '')).strip().lower()

            if datos['accion'] == 'nuevo':
                sql = """
                    INSERT INTO clientes(codigo,nombre,direccion,telefono,email,tipo)
                    VALUES(%s,%s,%s,%s,%s,%s)
                """
                valores = (datos['codigo'], datos['nombre'], datos['direccion'], datos['telefono'], datos['email'], tipo_normalizado)
            elif datos['accion'] == 'modificar':
                sql = """
                    UPDATE clientes SET codigo=%s,nombre=%s,direccion=%s,telefono=%s,email=%s,tipo=%s
                    WHERE idCliente=%s
                """
                valores = (datos['codigo'], datos['nombre'], datos['direccion'], datos['telefono'], datos['email'], tipo_normalizado, datos['idCliente'])
            elif datos['accion'] == 'eliminar':
                sql = """
                    DELETE FROM clientes WHERE idCliente=%s
                """
                valores = (datos['idCliente'],)
            else:
                return "Error: accion no valida"
            return db.ejecutar(sql, valores)
        except Error as e:
            return f"Error al guardar el cliente: {e}"
