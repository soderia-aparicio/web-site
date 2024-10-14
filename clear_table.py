from sqlalchemy import create_engine, MetaData, Table
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

def listar_tablas():
    tablas = metadata.tables.keys()
    for i, tabla in enumerate(tablas, start=1):
        print(f"{i}. {tabla}")
    return list(tablas)

def eliminar_registros(tabla):
    try:
        session.execute(tabla.delete())
        session.commit()
        print(f"Todos los registros de la tabla '{tabla.name}' han sido eliminados.")
    except Exception as e:
        session.rollback()
        print(f"Error al eliminar los registros: {e}")

def main():
    print("Tablas disponibles en la base de datos:")
    tablas = listar_tablas()

    try:
        seleccion = int(input("Ingrese el número de la tabla que desea limpiar: "))
        if 1 <= seleccion <= len(tablas):
            tabla_seleccionada = Table(tablas[seleccion - 1], metadata, autoload_with=engine)
            
            confirmacion = input(f"Está a punto de eliminar todos los registros de la tabla '{tabla_seleccionada.name}'. "
                                 "Esta acción no se puede deshacer. Escriba 'si, quiero borrar' para confirmar: ")
            if confirmacion == "si, quiero borrar":
                # Eliminar registros de las tablas dependientes primero
                if tabla_seleccionada.name == 'user':
                    # Eliminar registros de 'comment' y 'message' que dependen de 'user'
                    comment_table = Table('comment', metadata, autoload_with=engine)
                    eliminar_registros(comment_table)
                    message_table = Table('message', metadata, autoload_with=engine)
                    eliminar_registros(message_table)
                eliminar_registros(tabla_seleccionada)
            else:
                print("Operación cancelada.")
        else:
            print("Selección inválida. Por favor, intente nuevamente.")
    except ValueError:
        print("Entrada inválida. Por favor, ingrese un número.")
    finally:
        session.close()

if __name__ == "__main__":
    main()
