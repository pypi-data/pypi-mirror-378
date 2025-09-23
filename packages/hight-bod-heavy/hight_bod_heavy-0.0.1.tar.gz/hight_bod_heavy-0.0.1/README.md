# <strong>higth_bod_heavy</strong>

set PYTHONPATH=C:\Users\LENOVO\Desktop\libreria\pg2_practica_7.1\src

esta libreria tiene las sigtes finciones: `alculadoraIMC`, `CalculadoraGrasaCorporal`, `CalculadoraMasaMuscular`.
comenzamo armando la estructura de los archivos
creanado los archivos del paquete
pg2_practica_7/
├── LICENSE
├── pyproject.toml
├── README.md
├── src/
│ └── hinght_bod_heavy/
│ ├── **init**.py
│ └── hight_bod_haevy.py
└── tests/

## Configurando metadatos de project.toml

Abre pyproject.toml e ingresa el siguiente contenido.

```python
[build-system]
requires = ['setuptools>=40.8.0', 'wheel']
build-backend = 'setuptools.build_meta:__legacy__'
```

## Configurando metadatos en setup.cfg y setup.py

Abre setup.cfg e ingresa el siguiente contenido. Cambia el name por el nombre de tu paquete; asegúrate de que el nombre sea único en PyPI. Puedes verificar esto buscando en https://pypi.org/search/.

```python
[metadata]
name = example_package_pg2_tecba
version = 0.0.1
description = Reemplaza aquí con una descripción corta de tu paquete
long_description = file:README.md
long_description_content_type = text/markdown
url = https://github.com/yefeza/example_package_pg2_tecba
author = TU NOMBRE
author_email = tucorreo@example.com
license = MIT
classifiers =
    Intended Audience :: Developers
    Programming Language :: Python
    Topic :: Software Development

[options]
include_package_data = true
package_dir=
    =src
packages=find:
python_requires = >=3.7
install_requires =

[options.packages.find]
where=src
```

Abre setup.py e ingresa el siguiente contenido.

```python
from setuptools import setup

if __name__ == "__main__":
    setup()
```

# Generando archivos de distribución

El siguiente paso es generar paquetes de distribución para el paquete. Estos son archivos que se suben al Índice de Paquetes de Python y pueden ser instalados por pip.

Asegúrate de tener la última versión de build de PyPi instalada:

`python -m pip install --upgrade build`
Ahora ejecuta este comando desde el mismo directorio donde se encuentra pyproject.toml:

`python -m build`
Este comando debería generar mucho texto y una vez completado debería generar dos archivos en el directorio dist:
`dist/
├── example_package_pg2_tecba-0.0.1-py3-none-any.whl
└── example_package_pg2_tecba-0.0.1.tar.gz`

# Subiendo los archivos de distribución

¡Finalmente, es hora de subir tu paquete al Índice de Paquetes de Python!

Lo primero que necesitarás hacer es registrar una cuenta en PyPI, que es una instancia separada del índice de paquetes destinada a pruebas y experimentación. Para registrar una cuenta, ve a https://pypi.org/account/register/ y completa los pasos en esa página. También necesitarás verificar tu dirección de correo electrónico antes de poder subir cualquier paquete.

Para subir tu proyecto de forma segura, necesitarás un token API de PyPI. Crea uno en https://pypi.org/manage/account/#api-tokens, estableciendo el "Scope" a "Entire account". No cierres la página hasta que hayas copiado y guardado el token --- no verás ese token otra vez.

Ahora que estás registrado, puedes usar twine para subir los paquetes de distribución. Necesitarás instalar Twine:

python -m pip install --upgrade twine
Una vez instalado, ejecuta Twine para subir todos los archivos en dist:

python -m twine upload --repository pypi dist/\*
Se te pedirá un token API. Usa el valor del token, incluyendo el prefijo pypi-. Ten en cuenta que la entrada estará oculta, así que asegúrate de pegar correctamente.

Después de que el comando se complete, deberías ver una salida similar a esta:

```
Uploading distributions to https://pypi.org/legacy/
Enter your API token:
Uploading example_package_pg2_tecba-0.0.1-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 8.2/8.2 kB • 00:01 • ?
Uploading example_package_pg2_tecba-0.0.1.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.8/6.8 kB • 00:00 • ?
Una vez subido, tu paquete debería ser visible en PyPI; por ejemplo: https://pypi.org/project/example_package_pg2_tecba.
```

# Instalando tu paquete recién subido

Puedes usar pip para instalar tu paquete y verificar que funciona. Crea un entorno virtual e instala tu paquete desde PyPI:

`python -m pip install example-package-pg2-tecba`
pip debería instalar el paquete y la salida debería verse algo así:

```
Collecting example-package-TU-NOMBRE-DE-USUARIO-AQUÍ
Downloading https://test-files.pythonhosted.org/packages/.../example_package_pg2_tecba_0.0.1-py3-none-any.whl
Installing collected packages: example_package_pg2_tecba
Successfully installed example_package_pg2_tecba-0.0.1
```

Puedes probar que se instaló correctamente importando el paquete. Asegúrate de estar aún en tu entorno virtual, luego ejecuta Python:

```
python

```

e importa el paquete:

````
>>> from example_package_pg2_tecba import primer_modulo
>>> primer_modulo.add_one(2)
3```
````
