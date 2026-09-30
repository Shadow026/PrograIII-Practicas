import mysql.connector
from mysql.connector import Error


class Conexion:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "db_sistema_impuestos"
        print("Conectando a la base de datos...")
        try:
            self.conexion = mysql.connector.connect(
                host=self.host, user=self.user,
                password=self.password, database=self.database
            )
            if self.conexion.is_connected():
                cursor = self.conexion.cursor()
                cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
                cursor.close()
                print("Conexion exitosa y aislamiento configurado")
            else:
                print("No se pudo conectar a la base de datos")
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")

    def consultar(self, sql, datos=None):
        try:
            cursor = self.conexion.cursor(dictionary=True)
            cursor.execute(sql, datos if datos is not None else ())
            resultado = cursor.fetchall()
            cursor.close()
            return resultado
        except Error as e:
            print(f"Error al consultar la base de datos: {e}")
            return None

    def ejecutar(self, sql, datos=None):
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql, datos if datos is not None else ())
            self.conexion.commit()
            cursor.close()
            return 'ok'
        except Error as e:
            self.conexion.rollback()
            print(f"Error al ejecutar la consulta: {e}")
            return f'Error: {e}'