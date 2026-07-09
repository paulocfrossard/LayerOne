import asyncio
import sys
from convert_img_movie import convert_to_movie
from convert_movie_img import convert_to_img
from history import file_etapa, etapa_write
from log import logging
from upscaling_img import upscaling_image

def image_convert(MAX_CONCURRENT_TASKS,format, NOME_SERIE):
    image_task = asyncio.run(convert_to_img(max_tasks=MAX_CONCURRENT_TASKS, format=format, serie=NOME_SERIE))
    etapa_write('image_convert',f';{image_task}')
    return image_task

def upscaling_img(image_task: dict, upscale_client: str, upscale_size: float, codec: str, PATH: str):
    upscaling_status = asyncio.run(
        upscaling_image(max_tasks=MAX_CONCURRENT_TASKS,
                        base_folder=PATH,
                        codec=codec,
                        upscale_size=upscale_size,
                        upscale_client=upscale_client,
                        project_folder_name=image_task['folder_name']
                        )
    )
    etapa_write('upscaling_img', f';{upscaling_status}')
    return upscaling_status

def convert_img_to_movie(format: str, up_img: dict, output_name: dict, dict_resolution: dict):
    movie_status = asyncio.run(convert_to_movie(format_output=format,imgs_folder=up_img['upscale_folder'],output_file_name=output_name['folder_name'], dict_resolution=dict_resolution))
    etapa_write('convert_to_movie', f';{movie_status}')
    return movie_status

if __name__ == '__main__':
    file_etapa()
    try:
        #Configs
        NOME_SERIE = 'Serial Experiments Lain'
        MAX_CONCURRENT_TASKS: int = 24
        PATH = "/media/midias_3/Projeto Lain/projeto_lain_experience/arquivos base/episodios/"
        format = 'mkv'
        dict_resolution = [{'name': '1080p', 'size':  1080}, {'name': '2k', 'size': 2560}, {'name': '4k', 'size': 4096}]
        codecs = ['acnet-hdn1']
        upscale_client = '/home/paulo/Documentos/anime_ai_models/Anime4KCPP-3.0.0/build/bin/ac_cli'


        #trensforma em imagens
        image_status = image_convert(MAX_CONCURRENT_TASKS=MAX_CONCURRENT_TASKS, format=format, NOME_SERIE=NOME_SERIE)
        if image_status:
            for codec in codecs:
                if image_status['status']:
                    up_img = upscaling_img(image_task=image_status, upscale_client=upscale_client,upscale_size=4.0, codec=codec, PATH=PATHs
                    logging.critical(f"format={format}, up_img={up_img}, output_name={image_status}, dict_resolution={dict_resolution}")
                    if up_img['status']:
                        to_movie = convert_img_to_movie(format=format, up_img=up_img, output_name=image_status, dict_resolution=dict_resolution)
                        if to_movie:
                            logging.warning('[ ✅  ✅  ✅  ✅  COMPLETE ALL EPISODES ✅  ✅  ✅  ✅ ]')
            else:
                logging.critical(f'[ 🚨 | FATAL | IMAGE TASK FAIL | VERIFY MOVIE ]')
                sys.exit()

    except asyncio.CancelledError:
        logging.critical('[ 🚨 | CancelledError ] asyncio CancelledError.')
        pass
    except KeyboardInterrupt:
        logging.critical('[ 🚨 | KEY INTERRUPT ] Key stopped.')
    except Exception as e:
        logging.critical(f'[ 🚨 | ERROR ] {e}')
