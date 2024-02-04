import logging


def get_logger_analysis(nombreLogger):
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


def get_logger_dashboard(nombreLogger):
    archivoLog = 'log/tests.log'
    # Logger con un nombre específico
    test_logger_dashboard = logging.getLogger(nombreLogger)
    # Filemode=w para que se sobreescriba siempre
    logging.basicConfig(filename=archivoLog, 
                        level=logging.INFO, 
                        encoding='utf-8', 
                        filemode='w', 
                        format='%(levelname)s:%(name)s:%(message)s')
    return test_logger_dashboard