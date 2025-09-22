from setuptools import setup


with open('README.md', 'r', encoding='utf-8') as file:
    readme = file.read()


setup(
    name='ixcpy',
    version='1.1.0',
    license='MIT License',
    author='Felipe Sousa',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='sousa.felipe@outlook.com',
    description=u'Wrapper não oficial para conexão com a API do sistema IXC Provedor',
    url='https://github.com/SousaFelipe/ixcpy',
    packages=['ixcpy'],
    install_requires=['requests'],
    keywords=[
        'ixc',
        'ixcsoft',
        'api ixc',
        'ixc python'
    ]
)
