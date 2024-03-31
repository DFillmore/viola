from setuptools import setup

setup(name='Viola',
      version='0.8',
      description='Z-Machine interpreter written in Python',
      author='David Fillmore',
      author_email='marvin@frobnitz.co.uk',
      packages=["vio", "zcode"],
      scripts=['viola.py',],
      py_modules=["babel", "blorb", "iff", "quetzal", "settings"],
      data_files=[('fonts', ['fonts/bzork.ttf',
                             'fonts/noto/mono/NotoSansMono-Bold.ttf',
                             'fonts/noto/mono/NotoSansMono-Regular.ttf',
                             'fonts/noto/mono/OFL.txt',
                             'fonts/noto/serif/NotoSerif-Regular.ttf',
                             'fonts/noto/serif/NotoSerif-Bold.ttf',
                             'fonts/noto/serif/NotoSerif-Italic.ttf',
                             'fonts/noto/serif/NotoSerif-BoldItalic.ttf',
                             'fonts/noto/serif/OFL.txt'
                            ]
                  )
                 ],
      install_requires=['pygame>=2.5']
     )
