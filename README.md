# Guía

## Hitos

* [Hito 1: Repositorio de prácticas y definición del proyecto.](./documentacion/hito1.md)
* [Hito 2: Integración Continua.](./documentacion/hito2.md)

## Configuración
**Se requiere git y python junto a su gestor de paquetes pip**
```bash
  git clone https://github.com/lorena47/Matchgricola.git
  cd Matchgricola
  python -m venv venv
  source venv/bin/activate  # Linux / Mac
  venv\Scripts\activate     # Windows
  pip install invoke
  invoke configurar
```

* Prueba Hito 2
```bash
    invoke migrar
    invoke test
```
