from log import logging
file_path = "./etapas.etp"  # Replace with your file's path

def file_etapa():
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            logging.warning(f"[ 🔎 | ETAPA ] Arquivo de consulta salvo{content}")

    except FileNotFoundError:
        logging.critical(f'Create file {file_path}')
        with open(file_path, 'w') as file:
            pass

    except Exception as e:
        logging.info(f"An error occurred: {e}")

def etapa_write(etapa: str, status: str):
    with open(file_path, 'a') as file:
        file.write(f"{etapa, status}") 