from setuptools import setup

setup(
    name='mlab_amo_async',
    version='0.0.4',
    author='MLAB',
    description='Небольшая библиотека для работы с AmoCRM+MongoDB',
    install_requires=[
        'requests',
        'pyjwt',
        'motor',
        'aiohttp>=3.0.0',
        'aiofiles>=0.6.0',
        'importlib-metadata; python_version<"3.11"',
    ],
)