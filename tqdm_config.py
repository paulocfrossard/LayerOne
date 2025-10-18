
def tqdm_get_config():
    bar_format = '[ TOTAL PROGRESS ] {bar} | {n_fmt}/{total_fmt} | {rate_fmt} | {elapsed} < {remaining}'
    colour = 'green'
    unit = 'frame'
    ncols = 170
    return {'bar_format': bar_format, 'colour': colour, 'unit': unit, 'ncols': ncols}