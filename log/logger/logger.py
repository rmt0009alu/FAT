import logging


def get_logger_configurado(nombreLogger):
    nombreLogger = padding_nombre(nombreLogger)
    archivoLog = 'log/tests.log'
    # Logger con un nombre específico
    test_logger_analysis = logging.getLogger(nombreLogger)
    # Filemode=w para que se sobreescriba siempre
    logging.basicConfig(filename=archivoLog, 
                        level=logging.INFO, 
                        encoding='utf-8', 
                        filemode='w', 
                        format='%(levelname)s:%(name)s:%(message)s')
    return test_logger_analysis


def padding_nombre(nombreLogger):
    tam = 15
    if len(nombreLogger) >= tam:
        return nombreLogger[:tam]
    else:
        multiplicador = tam - len(nombreLogger)
        return nombreLogger + ' ' * multiplicador
