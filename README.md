# MARIS

WFMS Backend built using Python Django

## Getting Started

1. Open your terminal and clone the project using `git clone `
2. Install a python virtual enviroment

#### Linux

- `sudo apt-get install python3-venv` # If needed
- `python3 -m venv .venv`
- `source .venv/bin/activate`

#### macOS

- `python3 -m venv .venv`
- `source .venv/bin/activate`

#### Windows

- `py -3.9 -m venv .venv`
- `.venv/scripts/activate`

3. Upgrade PIP using `python -m pip install --upgrade pip`
4. Install packages using `python -m pip install -r requirements.txt`
`pip install https://download.lfd.uci.edu/pythonlibs/archived/GDAL-$(ogrinfo --version | cut -d' ' -f2 | cut -d',' -f1)-cp$(python --version | cut -d' ' -f2 | cut -d',' -f1 | cut -c 1,3)-cp$(python --version | cut -d' ' -f2 | cut -d',' -f1 | cut -c 1,3)-win_amd64.whl`

`pip install https://filetransfer.itc.nl/pub/52n/ilwis_py/wheels/windows/20230929/ilwis-1.0.20230929-cp311-cp311-win_amd64.whl`

5. Run migrations `python manage.py migrate`
6. Start the app using `python manage.py runserver`
