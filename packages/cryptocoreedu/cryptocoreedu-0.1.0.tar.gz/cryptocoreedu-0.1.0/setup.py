import pathlib

from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name="cryptocoreedu",
    version="0.1.0",
    description="Educational cryptography toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="michaans",
    keywords=["cryptography", "educational", "aes", "ecb"],
    # Автоматически находит все пакеты (папки с __init__.py)
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    # Зависимости проекта (библиотеки, которые нужны для работы)
    install_requires=[
        'pycryptodome>=3.23.0',  # Ваша основная зависимость
    ],

    # entry_points - это "магия", которая делает из вашего кода CLI-утилиту
    entry_points={
        'console_scripts': [
            'crypto=cryptocoreedu.main:main',  # Формат: 'имя_команды=путь.к.модулю:функция'
        ],
    },

)