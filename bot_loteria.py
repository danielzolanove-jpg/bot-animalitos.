name: Monitoreo de Resultados

on:
  schedule:
    - cron: '*/30 * * * *'  # Ejecuta cada 30 minutos
  workflow_dispatch:        # Permite probarlo manualmente

jobs:
  check-website:
    runs-on: ubuntu-latest

    steps:
    - name: Descargar código
      uses: actions/checkout@v3

    - name: Configurar Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Instalar librerías
      run: |
        pip install requests beautifulsoup4

    - name: Ejecutar script de revisión
      run: |
        python bot_loteria.py

    - name: Guardar estado actualizado
      run: |
        git config --global user.name "github-actions[bot]"
        git config --global user.email "github-actions[bot]@users.noreply.github.com"
        git add ultimo_estado.txt || true
        git commit -m "Actualizar ultimo estado" || true
        git push || true

