import subprocess
import os

# Aquí indico la ruta de mi entorno virtual en el server
rutaVenv = '/home/takeiteasy/.virtualenvs/venv'

# Aquí indico el script de actualización de las BDs
scriptActualizar = '/home/takeiteasy/FAT/ActualizarBDs.py'

# Activo el entorno virtual y lanzo el script
# de actualización (hay que hacerlo todo a la vez
# para que detecte bien el entorno virtual)
comando = f'source {rutaVenv}/bin/activate && python {scriptActualizar}'
subprocess.run(comando, shell=True, executable='/bin/bash')

# Cerrar la consola (ojo, sólo UNIX)
os.system('exit')
# subprocess.run('exit', shell=True, executable='/bin/bash')