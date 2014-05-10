from distutils.core import setup



setup(name='Viola',
      version='0.8',
      description='A Blorb-capable Z-Machine interpreter.',
      author='David Fillmore',
      author_email='marvin@frobnitz.co.uk',
      packages=["zio", "zcode"],
      scripts=['viola.py',],      
      py_modules=["babel", "blorb", "iff", "quetzal", "settings"],
      data_files=[('fonts', ['fonts/FreeMono.ttf',
                             'fonts/FreeMonoBold.ttf',
                             'fonts/FreeMonoBoldOblique.ttf',
                             'fonts/FreeMonoOblique.ttf',
                             'fonts/FreeSans.ttf',
                             'fonts/FreeSansBold.ttf',
                             'fonts/FreeSansBoldOblique.ttf',
                             'fonts/FreeSerif.ttf',
                             'fonts/FreeSerifBold.ttf',
                             'fonts/FreeSerifBoldItalic.ttf',
                             'fonts/FreeSerifItalic.ttf',
                            ]
                  )
                 ]
     ) 
