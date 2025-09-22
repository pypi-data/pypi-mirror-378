import setuptools
from pathlib import Path

# setup usa argumentos nombrados, name es el nombre del paquete dentro de pypi
# usar la convención de sender o senver
# long description nos da la descripcion de nuestro proyecto pero leemos desde el readme md usando Path
# el de packages, lo hacemos para indicar donde estan los paquetes y lo hacemos con setuptools.find packages y a este
# le decimos que directorios o paquetes queremos ignorar para que no los considere. ignoramos mocks y tests

long_desc = Path("README.md").read_text()

setuptools.setup(
    name="holamundoplayerlupo123",
    version="0.0.1",
    long_description=long_desc,
    packages=setuptools.find_packages(exclude=['mocks', 'tests'])
)
