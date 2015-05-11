# -*- mode: python -*-

block_cipher = None


a = Analysis(['CelestiaSunrise.py'],
             pathex=['C:\\Users\\Marc-Etienne\\Miniconda\\Lib\\site-packages', 'E:\\CelestiaSunrise'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             cipher=block_cipher)
for d in a.datas:
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
        break

pyz = PYZ(a.pure,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='CelestiaSunrise.exe',
          debug=False,
          strip=None,
          upx=False,
          console=False )
