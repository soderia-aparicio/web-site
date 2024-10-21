from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv('DATABASE_URL')

# Crear la conexión con la base de datos
engine = create_engine(DATABASE_URL)
metadata = MetaData(bind=engine)

# Reflejar todas las tablas de la base de datos
metadata.reflect(bind=engine)

# Crear una sesión
Session = sessionmaker(bind=engine)
session = Session()

# Función para listar las tablas disponibles
def listar_tablas():
    tablas = metadata.tables.keys()
    for i, tabla in enumerate(tablas, start=1):
        print(f"{i}. {tabla}")
    return list(tablas)

# Función para eliminar los registros de una tabla específica
def eliminar_registros(tabla):
    try:
        # Usar TRUNCATE para eliminar todos los registros de la tabla con CASCADE
        tabla_name = f'"{tabla.name}"'  # Rodear con comillas dobles para evitar palabras reservadas
        session.execute(text(f'TRUNCATE TABLE {tabla_name} CASCADE'))
        session.commit()
        print(f"Todos los registros de la tabla '{tabla.name}' han sido eliminados.")
    except Exception as e:
        session.rollback()
        print(f"Error al eliminar los registros: {e}")

# Función para limpiar todas las tablas manteniendo las dependencias
def limpiar_todas_las_tablas():
    try:
        # Obtener los nombres de todas las tablas y ordenar según las dependencias
        tablas = list(metadata.tables.keys())
        
        # Usar TRUNCATE para eliminar todas las tablas con CASCADE
        for nombre_tabla in tablas:
            tabla = Table(nombre_tabla, metadata, autoload_with=engine)
            eliminar_registros(tabla)

        print("Todas las tablas han sido limpiadas con éxito.")
    except Exception as e:
        session.rollback()
        print(f"Error al limpiar las tablas: {e}")

# Función principal para ejecutar el script
def main():
    print("Seleccione una opción:")
    print("1. Limpiar una tabla específica")
    print("2. Limpiar todas las tablas")

    try:
        opcion = int(input("Ingrese el número de la opción que desea realizar: "))

        if opcion == 1:
            tablas = listar_tablas()
            seleccion = int(input("Ingrese el número de la tabla que desea limpiar: "))
            if 1 <= seleccion <= len(tablas):
                tabla_seleccionada = Table(tablas[seleccion - 1], metadata, autoload_with=engine)
                
                confirmacion = input(f"Está a punto de eliminar todos los registros de la tabla '{tabla_seleccionada.name}'. "
                                     "Esta acción no se puede deshacer. Escriba 'si, quiero borrar' para confirmar: ")
                if confirmacion == "si, quiero borrar":
                    eliminar_registros(tabla_seleccionada)
                else:
                    print("Operación cancelada.")
            else:
                print("Selección inválida. Por favor, intente nuevamente.")

        elif opcion == 2:
            confirmacion = input("Está a punto de eliminar todos los registros de TODAS las tablas. "
                                 "Esta acción no se puede deshacer. Escriba 'si, quiero borrar' para confirmar: ")
            if confirmacion == "si, quiero borrar":
                limpiar_todas_las_tablas()
            else:
                print("Operación cancelada.")

        else:
            print("Opción inválida. Por favor, intente nuevamente.")

    except ValueError:
        print("Entrada inválida. Por favor, ingrese un número.")
    finally:
        session.close()

if __name__ == "__main__":
    main()
