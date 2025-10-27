# Guía

## Hitos

* [Hito 1: Repositorio de prácticas y definición del proyecto.](./documentacion/hito1.md)
* [Hito 2: Integración Continua.](./documentacion/hito2.md)

## Configuración
**Se requiere tener instalados git y python >= 3.10**
```bash
  git clone https://github.com/lorena47/Matchgricola.git
  cd Matchgricola
  python -m venv venv
  source venv/bin/activate  # Linux / Mac
  venv\Scripts\activate     # Windows
  python -m pip install --upgrade pip
  pip install invoke
  invoke configurar
```

* Probar Hito 2
```bash
    invoke migrar
    invoke test
```
