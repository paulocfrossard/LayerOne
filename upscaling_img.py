from log import logging
from pathlib import Path

import asyncio

from tqdm_config import tqdm_get_config
from tqdm.contrib.logging import logging_redirect_tqdm
from tqdm.asyncio import tqdm


async def process_image_async(command: dict, semaphore: asyncio.Semaphore):
    file = command['file']
    command = command['command']
    async with semaphore:
        logging.info(f"[ FILA | ADD ] ADICIONADO A FILA: {file}")
        try:
            process = await asyncio.create_subprocess_shell(
                cmd=command,
                shell=True,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logging.info(f"[ ✅ | EXITO | ASSYNCIO ]: {file}")
            else:
                # Mostra uma mensagem de erro se o comando falhar
                logging.critical(f"[ ⚠️ | ERROR | ASSYNCIO ] Erro ao processar {file}:")
                logging.critical(stderr.decode().strip())
        except asyncio.TimeoutError:
            logging.critical(
                f" [ ⏲️ | TIMEOUT ] O processo para {file} criou o arquivo mas não finalizou corretamente. Travado e cancelado.")

        except Exception as e:
            logging.critical(f"[ ⚠️ | ERROR | ASSYNCIO ] uma exceção inesperada ao processar {file}: {e}")

def gen_commands(output_extension: str, output_folder: str, item:str, extension: str, codec: str, up_size: float,
                 folder: str, up_cli: str, gpu: str, device: int) -> dict [str,]:
    new_name = str(item.split(extension)[0]+f'_codec-{codec}_up-{up_size}{output_extension}').split(folder)[1].split('/')[1]
    output_file = f"{output_folder}/{new_name}"
    command = f'{up_cli} -i "{item}" -o "{output_file}" -m {codec} -f {up_size} -p {gpu} -d {device}'
    return {'command': command, 'file': output_file}

async def upscaling_image(project_folder_name: str, max_tasks: int, upscale_size: float, upscale_client: str,
                          base_folder: str, codec: str, gpu: str = "cuda", device: int = 0, input_ext: str = ".bmp",
                          output_ext: str = ".png") -> dict[str, bool | str]:
    logging.warning(f'[ 🚨 | Iniciando upscaling | CODEC: {str(codec).upper()} | 🚨 ]')
    # load configs
    semaphore = asyncio.Semaphore(max_tasks)
    tqdm_default = tqdm_get_config()

    # Folders
    base_folder = f'{base_folder}{project_folder_name}'
    output_folder = f'{base_folder}/{codec}'

    # File Obj
    local = Path(base_folder)
    new_folder = Path(f"{output_folder}")
    new_folder.mkdir(parents=True, exist_ok=True)

    # Create list
    list_file_path = list(local.glob(f"*{input_ext}"))

    #Pego a função e executo ela posteiormente em um for
    commands = [gen_commands(output_folder=output_folder, item=str(file), extension=input_ext, output_extension=output_ext, codec=codec, up_size=upscale_size, folder=base_folder, up_cli=upscale_client, gpu=gpu, device=device) for file in list_file_path]
    tasks = [process_image_async(command=command, semaphore=semaphore) for command in commands]

    with logging_redirect_tqdm():
        await tqdm.gather(*tasks, desc='Processing images', unit=tqdm_default['unit'],bar_format=tqdm_default['bar_format'],colour=tqdm_default['colour'],ncols=tqdm_default['ncols'])

    return {'status': True, 'upscale_folder': output_folder}
