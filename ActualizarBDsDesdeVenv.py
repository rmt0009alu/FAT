import subprocess

# Aquí indico la ruta de mi entorno virtual en el server
rutaVenv = '/home/takeiteasy/.virtualenvs/venv'

# Activo el entorno virtual
activate_command = f'source {rutaVenv}/bin/activate'
subprocess.run(activate_command, shell=True, executable='/bin/bash')

# Lanzo el script de actualizaciónn de bases de datos
scriptActualizar = '/home/takeiteasy/FAT/ActualizarBDs.py'
subprocess.run(['python', scriptActualizar])