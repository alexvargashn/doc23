from setuptools import setup, find_packages

# Runtime dependencies - required for the core functionality
RUNTIME_DEPS = [
    'annotated-types==0.7.0',
    'anyio==4.8.0',
    'certifi==2025.1.31',
    'cffi==1.17.1',
    'charset-normalizer==3.4.1',
    'click==8.1.8',
    'cryptography==44.0.2',
    'dnspython==2.7.0',
    'docx2txt==0.8',
    'pdf2image==1.17.0',
    'python-docx==1.1.0',
    'odfpy==1.4.1',
    'h11==0.14.0',
    'httpcore==1.0.7',
    'httptools==0.6.4',
    'httpx==0.28.1',
    'idna==3.10',
    'Jinja2==3.1.5',
    'markdown==3.5.2',
    'python-magic==0.4.27',
    'python-multipart==0.0.20',
    'PyYAML==6.0.2',
    'sniffio==1.3.1',
    'striprtf==0.0.28',
    'typing_extensions==4.12.2',
    'pdfplumber==0.11.5',
    'pytesseract==0.3.10',
    'Pillow==11.1.0',
    'pypdfium2==4.30.1',
    'pdfminer.six==20231228'
]

# Development dependencies - for testing, linting, and development
DEV_DEPS = [
    'autopep8==2.3.2',
    'black==25.1.0',
    'mypy-extensions==1.0.0',
    'pycodestyle==2.12.1',
    'Pygments==2.19.1',
    'rich==13.9.4',
    'rich-toolkit==0.13.2',
    'yapf==0.43.0',
]

# Web dependencies - for FastAPI and related functionality
WEB_DEPS = [
    'email_validator==2.2.0',
    'fastapi==0.115.11',
    'fastapi-cli==0.0.7',
    'shellingham==1.5.4',
    'starlette==0.46.0',
    'typer==0.12.5',
    'uvicorn==0.34.0',
    'uvloop==0.21.0',
    'watchfiles==1.0.4',
    'websockets==15.0',
]

setup(
    name                          = "doc23",
    version                       = "0.1.0",
    packages                      = find_packages(),
    install_requires              = RUNTIME_DEPS,
    extras_require               = {
        'dev': DEV_DEPS,
        'web': WEB_DEPS,
        'all': RUNTIME_DEPS + DEV_DEPS + WEB_DEPS,
    },
    author                        = "Alex Vargas",
    author_email                  = "alexv7142@gmail.com",
    description                   = "A python library to extract text from documents like pdf, docx, odt, md, rtf and images and formatting the output to a JSON dinamic tree provided by the user.",
    long_description              = open("README.md").read(),
    long_description_content_type = "text/markdown",
    url                           = "https://github.com/alexvargashn/doc23",
    classifiers                   = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires = '>=3',
)
