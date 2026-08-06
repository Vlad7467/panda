#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматический сборщик APK для Pygame-игр.
Использует buildozer. Работает в Termux или Linux.
Запустите: python build_apk.py
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

def run_command(cmd, check=True):
    print(f"▶ Выполняю: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if check and result.returncode != 0:
        print("❌ Ошибка выполнения:")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def install_buildozer():
    print("🔧 Проверяю наличие buildozer...")
    try:
        subprocess.run(["buildozer", "--version"], check=True, capture_output=True)
        print("✅ buildozer уже установлен.")
    except FileNotFoundError:
        print("📦 Устанавливаю buildozer...")
        run_command("pip install buildozer cython")

def create_spec_file(app_name, package_name, main_py_path):
    spec_path = "buildozer.spec"
    if os.path.exists(spec_path):
        print("⚠️ Файл buildozer.spec уже существует. Перезаписываю...")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(f"""
[app]
title = {app_name}
package.name = {package_name.lower()}
package.domain = org.{package_name.lower()}

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,wav,mp3,json,db
version = 0.1

requirements = python3,pygame,numpy,pillow,requests

orientation = landscape
fullscreen = 1

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (опционально) иконка
# android.icon = icon.png

[buildozer]
log_level = 2
warn_on_root = 1
""")
    print("✅ Файл buildozer.spec создан.")

def build_apk():
    print("🚀 Запускаю сборку APK. Это займёт 10–30 минут...")
    run_command("buildozer android debug deploy run")

def main():
    # Проверяем, что main.py существует
    if not os.path.exists("main.py"):
        print("❌ Файл main.py не найден в текущей папке.")
        print("   Поместите ваш main.py в эту папку и запустите скрипт снова.")
        sys.exit(1)

    # Устанавливаем buildozer
    install_buildozer()

    # Запрашиваем название приложения
    app_name = input("Введите название игры (например, 'Panda Chaos'): ").strip()
    if not app_name:
        app_name = "MyGame"
    package_name = input("Введите имя пакета (латиница, например, 'pandachaos'): ").strip()
    if not package_name:
        package_name = "mygame"

    # Создаём spec-файл
    create_spec_file(app_name, package_name, "main.py")

    # Запускаем сборку
    build_apk()

    print("🎉 Готово! APK файл находится в папке bin/")
    print("   Установите его на телефон и играйте!")

if __name__ == "__main__":
    main()
