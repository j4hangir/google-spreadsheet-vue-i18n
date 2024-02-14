from setuptools import setup

setup(name='google-spreadsheet-vue-i18n',
      version='1.0.0',
      description='Google Spreadsheet Vue i18n',
      url='https://git.j4hangir.com/py/google-spreadsheet-vue-i18n.git',
      author='j4hangir',
      author_email='j4hangir@gmail.com',
      packages=['google_spreadsheet_vue_i18n'],
      scripts=['bin/google-spreadsheet-vue-i18n'],
      install_requires=[
          'requests',
          'loguru',
      ],
      zip_safe=False)
