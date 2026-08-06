
[app]
title = pand
package.name = panda
package.domain = org.panda

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
