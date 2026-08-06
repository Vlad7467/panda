[app]
title = Panda Chaos
package.name = pandachaos
package.domain = org.pandachaos

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,wav,mp3,json,db

version = 0.1
requirements = python3,pygame,numpy,pillow,requests

orientation = landscape
fullscreen = 1

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 30
android.minapi = 24
android.ndk = 28c
android.sdk = 30
android.build_tools = 30.0.3

android.sdk_path = /home/runner/android-sdk
android.ndk_path = /home/runner/android-ndk
android.ant_path = /home/runner/apache-ant

[buildozer]
log_level = 2
warn_on_root = 1
