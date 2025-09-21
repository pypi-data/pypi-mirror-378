from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='cursofiap-marinaslucas-2025',
    version='1.0.0',
    packages=find_packages(),
    description='Curso de Python da FIAP - IA Para Devs',
    author='Marina Altoé',
    author_email='aws.developer.studies@gmail.com',
    url='https://github.com/marinaslucas/cursofiap',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
