from setuptools import setup

setup(name='Viola',
      version='0.8',
      description='Z-Machine interpreter written in Python',
      author='David Fillmore',
      author_email='marvin@frobnitz.co.uk',
      packages=["vio", "zcode"],
      scripts=['viola.py',],
      py_modules=["babel", "blorb", "iff", "quetzal", "settings"],
      data_files=[('fonts', ['bzork.ttf/mono/'
                             'noto/mono/NotoSansMono-Bold.ttf',
                             'noto/mono/NotoSansMono-Regular.ttf',
                             'noto/mono/OFL.txt',
                             'noto/serif/NotoSerif-Regular.ttf',
                             'noto/serif/NotoSerif-Bold.ttf',
                             'noto/serif/NotoSerif-Italic.ttf',
                             'noto/serif/NotoSerif-BoldItalic.ttf',
                             'noto/serif/OFL.txt'
                            ]
                  )
                 ],
      install_requires=['pygame>=2.5']
     )
