from setuptools import setup, find_packages

setup(
    name='leo-prompt_optimizer',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'openai>=1.0.0',
    ],
    description='A Python library to optimize prompts from drafts and LLM inputs/outputs.',
    author='Léonard Baesen-Wagner',
    author_email='lr.baesen@gmail.com',
    license='MIT',
)
