#! /usr/bin/python3
import sys
import logging
import os
from logging.handlers import RotatingFileHandler

logging.basicConfig(stream=sys.stderr)

app_dir = os.path.dirname(os.path.abspath(__file__))

# Proje ana klasörüne geçiş yapın
sys.path.insert(0, '/home/sametatabasch/PycharmProjects/akran_degerlendirme')

# Sanal ortamı etkinleştirin
venv_lib = os.path.join("/home/sametatabasch/PycharmProjects/akran_degerlendirme", 'venv/lib/python3.10/site-packages')
sys.path.insert(1, venv_lib)

# Uygulama örneğini alın
from akran_degerlendirme import app as application