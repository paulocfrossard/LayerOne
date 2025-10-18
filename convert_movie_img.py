from numbers import Number

from tqdm.asyncio import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from log import logging
from pathlib import Path
import asyncio

from tqdm_config import tqdm_get_config
from upscaling_img import gen_commands

async  def process_video_async(command: dict, semaphore: asyncio.Semaphore):
    size = len(command)-1
    filename = command['file']
    command = command['command']

    async with semaphore:
        logging.warning(f"[ 🚀 | TAM: {size} | FILA | ADD ] ADICIONADO A FILA: {filename}")
        try:
            process = await asyncio.create_subprocess_shell(
                cmd=command,
                shell=True,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                logging.critical(f"[ 🚨 | ERRO | ASSYNCIO ] Erro ao processar {filename}:")
                logging.critical(stderr.decode().strip())
            else:
                logging.info(f"[ ✅ | EXITO | ASSYNCIO ]: {filename}")
        except Exception as e:
            logging.critical(f"[ 🚨 | ERROR | ASSYNCIO ] uma exceção inesperada ao processar {filename}: {e}")

def gen_commands(serie_name: str, item: str, path: Path, ep_number: str, format: str, final_command:(str | None) = None) -> dict | None:
    file_name = f'{serie_name}-{ep_number}'
    final_command = f'ffmpeg -hwaccel cuda -c:v h264_cuvid -i "Serial Experiments Lain - Episode {ep_number} [MorpheusN and Ghosty6464].mkv" -pix_fmt rgb24 {ep_number}/frame_%08d.bmp'
    return {'command': str(final_command), 'file': file_name}

async def convert_to_img(serie: str, max_tasks: int = 12, path: str = ".", format: str = 'mkv') -> bool:
    #Local config
    semaphore = asyncio.Semaphore(max_tasks)
    local = Path(path)
    list_file_path = list(local.glob(f"*.{format}"))
    list_files_str = [str(arquivo) for arquivo in list_file_path]
    name_list = list_file_path[0].name.split(' ')
    tqdm_default = tqdm_get_config()

    for item in name_list:
        try:
            ep_number = f"{int(item):02}"
        except (ValueError, TypeError):
            continue
    #Verify
    filter = Path(f'{ep_number}').exists()

    if filter:
        logging.warning(f'[ FOLDER ] {serie, ep_number} already exists')
        pass
    else:
        path = Path(f'{ep_number}')
        path.mkdir(parents=True, exist_ok=True)
        logging.warning(f'[ FOLDER ] {serie, ep_number} created')

    path = Path(ep_number)

    #Gen
    commands = [gen_commands(serie_name=serie, item=item, format=format, ep_number=ep_number, path=path) for item in list_files_str]

    tasks = [process_video_async(command=command, semaphore=semaphore) for command in commands]

    with logging_redirect_tqdm():
        await tqdm.gather(*tasks, desc='Processing images', unit=tqdm_default['unit'],
                          bar_format=tqdm_default['bar_format'], colour=tqdm_default['colour'],
                          ncols=tqdm_default['ncols'])

    return {'status': True, 'folder_name': ep_number}