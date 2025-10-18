from history import etapa_write
from log import logging
from pathlib import Path

import asyncio

from tqdm.contrib.logging import logging_redirect_tqdm
from tqdm.asyncio import tqdm
from tqdm_config import tqdm_get_config



async def convert_movie_async(command: dict, semaphore: asyncio.Semaphore):
    filename = command['file']
    command = command['command']

    async with semaphore:
        logging.info(f"[ FILA | ADD ] ADICIONADO A FILA: {filename}")
        try:
            process = await asyncio.create_subprocess_shell(
                cmd=command,
                shell=True,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logging.info(f"[ ✅ | EXITO | ASSYNCIO ]: {filename}")
            else:
                # Mostra uma mensagem de erro se o comando falhar
                logging.critical(f"[ ⚠️ | ERROR | ASSYNCIO ] Erro ao processar {filename}:")
                logging.critical(stderr.decode().strip())

        except asyncio.TimeoutError:
            logging.critical(
                f" [ ⏲️ | TIMEOUT ] O processo para {filename} criou o arquivo mas não finalizou corretamente.\
                 Travado e cancelado.")

        except Exception as e:
            logging.critical(f"[ ⚠️ | ERROR | ASSYNCIO ] uma exceção inesperada ao processar {filename}: {e}")

def gen_commands(folder: str, ffmpeg_framerate: str, ffmpeg_default_name: str, ffmpeg_format: str,
                 list_resolution: list, ffmpeg_codec: str, ffmpeg_preset: str, ffmpeg_quality: int,
                 output_name: str, format_output: str) -> list:
    commands = []
    input_data = Path(folder)
    output_data = Path(folder)
    for ffmpeg_resolution in list_resolution:
        command = f'ffmpeg -framerate {ffmpeg_framerate} -i "{input_data}/{ffmpeg_default_name}" -vf "format={ffmpeg_format}=w={ffmpeg_resolution['size']}:h=-1" -c:v {ffmpeg_codec} -preset {ffmpeg_preset} -qp {ffmpeg_quality} "{output_data}/{output_name}_{ffmpeg_resolution['name']}_{ffmpeg_codec}.{format_output}"'
        commands.append({'command': str(command), 'file': output_name})
    return commands

async def convert_to_movie(format_output: str, imgs_folder: str, output_file_name: str, dict_resolution: list[dict], max_tasks: int = 12) -> bool:
    #Saida esperada:
    #[CRITICAL] [root] - format_output: mkv, imgs_folder: /media/midias_3/Projeto Lain/projeto_lain_experience/arquivos base/episodios/06/acnet-hdn1, output_file_name: lain_06, dict_resolution: [{'name': '1080p', 'size': 1080}, {'name': '2k', 'size': 2560}, {'name': '4k', 'size': 4096}], max_tasks: 12
    logging.critical(f"format_output: {format_output}, imgs_folder: {imgs_folder}, output_file_name: {output_file_name}, dict_resolution: {dict_resolution}, max_tasks: {max_tasks}")
    etapa_write('[ convert_to_movie | Status com erro ]', f"format_output: {format_output}, imgs_folder: {imgs_folder}, output_file_name: {output_file_name}, dict_resolution: {dict_resolution}, max_tasks: {max_tasks}")
    # Geral configs
    semaphore = asyncio.Semaphore(max_tasks)
    output_name = output_file_name
    tqdm_default = tqdm_get_config()
    folder_up = f"{imgs_folder}"

    #ffmpeg configs
    ffmpeg_codec = 'hevc_nvenc'
    ffmpeg_preset = 'p7'
    ffmpeg_quality = 20
    ffmpeg_format = 'yuv420p,hwupload_cuda,scale_cuda'
    ffmpeg_framerate = '24000/1001'
    ffmpeg_default_name = 'frame_%08d_codec-acnet-hdn1_up-4.0.png'

    commands_list = gen_commands(ffmpeg_framerate=ffmpeg_framerate, ffmpeg_default_name=ffmpeg_default_name,
                                 ffmpeg_format=ffmpeg_format, list_resolution=dict_resolution, ffmpeg_codec=ffmpeg_codec,
                                 ffmpeg_preset=ffmpeg_preset, ffmpeg_quality=ffmpeg_quality,
                                 output_name=output_name,folder=str(folder_up), format_output=format_output)
    local = Path('.')
    tasks = [convert_movie_async(command=command, semaphore=semaphore) for command in commands_list]

    with logging_redirect_tqdm():
        await tqdm.gather(*tasks, desc='Processing images', unit=tqdm_default['unit'],
                          bar_format=tqdm_default['bar_format'], colour=tqdm_default['colour'],
                          ncols=tqdm_default['ncols'])

    return {'status': True}

asyncio.run(convert_to_movie('mkv', '/media/midias_3/Projeto Lain/projeto_lain_experience/arquivos base/episodios/09/acnet-hdn1', output_file_name='lain_09s', dict_resolution=[{'name': '1080p', 'size':  1080}, {'name': '2k', 'size': 2560}, {'name': '4k', 'size': 4096}]))
