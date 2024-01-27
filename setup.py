from distutils.core import setup


setup(
    name='akran_degerlendirme',
    version='1.0.0',
    packages=[''],
    url='https://github.com/sametatabasch/akran_degerlendirme',
    license='MIT',
    author='sametatabasch',
    author_email='sametatabasch@gmail.com',
    description='',
    install_requires=[
        'Flask',
        'flask_bcrypt',
        'flask_login',
        'flask_sqlalchemy',
        'flask_wtf',
        'email_validator',
        'tinify,',
        'Flask-Migrate'
    ],
    entry_points={
        'console_scripts': [

        ],
    },
    # bdist_wheel parametresi eklendi
    setup_requires=[
        'wheel',
    ],
)