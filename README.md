# Matchgrícola

Matchgrícola es un proyecto que parte de cero, para facilitar la búsqueda de mano de obra agrícola en el pueblo durante todo el año, adaptándose a las distintas necesidades del campo.

Al acercarse alguna temporada alta, los propietarios requieren apoyo en distintas faenas, tanto en cosecha como en labores no estacionales (regar, quemar rastrojos, plantar, podar o realizar mantenimientos puntuales). Tradicionalmente, se buscan jornaleros llamando por teléfono o mandando mensajes a cada uno de los trabajadores de los que se tenga referencia, y no son pocas las veces en que varios contactan con un mismo agricultor, ya comprometido en otras labores. Este método de búsqueda es poco eficiente y se limita a los contactos que tenga el propietario, o que pueda conseguir por recomendaciones informales de terceros.

Para resolver el problema, en la aplicación aparecerán solo personas disponibles para el período filtrado y el tipo de tarea requerida, ahorrando tiempo al evitar conflictos de agenda y la necesidad de conseguir contactos adicionales. Además, se contará con un sistema de evaluación, tanto de propietarios como de jornaleros, para mejorar la confianza y transparencia en ambos sentidos y priorizar la búsqueda según la valoración en el tipo de labor.

## Despliegue en la nube

* El servidor, que es lo que se despliega en la nube, es el núcleo funcional del proyecto: conectar a múltiples usuarios y gestionar los emparejamientos entre estos (propietarios y jornaleros).

* La aplicación se beneficia del despliegue en la nube, ya que:
  -  garantiza una alta disponibilidad y seguridad gracias a la distribución de nodos en distintos puntos del mundo (redundancia).
  - posibilita la sincronización de datos en tiempo real, de modo que los usuarios pueden ver de inmediato cualquier cambio en ofertas o disponibilidades.
  - favorece el escalado automático del sistema según las necesidades y la demanda en distintas temporadas agrícolas.
  - facilita una monitorización continua del servicio, asegurando su correcto funcionamiento y una rápida detección de incidencias.

## Hitos

* [Hito 1](./documentacion/hito1.md)

## Roles

El sistema contará con tres roles para su funcionamiento:

* **Administrador:** se encarga de supervisar los perfiles, propuestas y valoraciones, además de resolver incidencias. También crea las distintas categorías de tareas y puede aceptar sugerencias.

* **Propietarios:** suben propuestas de trabajo para un período. En el inicio les aparecen jornaleros que tienen disponibilidad para las ofertas que hayan subido, ordenados por prioridad según la valoración en la labor que se requiera. A los que les interesen les pueden proponer el trabajo dando *like* y seleccionando para qué oferta/s (solo saldrán para seleccionar en las que coincida disponibilidad y tarea con la del jornalero). También valoran a los jornaleros con los que trabajen y pueden hacer sugerencias de categorías de tareas.

* **Jornaleros:** tienen un calendario de disponibilidad laboral y pueden configurar su perfil para ordenar y/o filtrar las tareas que puedan o quieran hacer. En el inicio les salen las propuestas de trabajo que se ajustan a su calendario, ordenadas por valoración y por prioridad si así lo han configurado, y se suscriben a las que les interesen dando *like*. También valoran a los propietarios con los que trabajen y pueden hacer sugerencias de categorías de tareas.

En caso de *like* recíproco se considera que ha habido un *match*, y se dividirán en dos secciones las propuestas en las que te han dado *like* de las que hayan sido *match*. En la sección de *likes* será donde el propietario y el jornalero acepten o rechacen el trabajo, y en caso de aceptar pasarán a la sección de *match*. Si una oferta pasa a la sección de *match*, se proporciona la información de contacto y se descuenta en uno las vacantes de la oferta.

## Historias de Usuario

### Funcionalidad principal

* **HU1.** Como propietario, debo poder hacer una propuesta de trabajo para un período determinado.
* **HU2.** Como jornalero, debo poder tener un calendario de disponibilidad.
* **HU3.** Como jornalero, debo poder editar mi calendario de disponibilidad.
* **HU4.** Como jornalero, debo ver en mi inicio ofertas que se adecúen a mi disponibilidad.
* **HU5.** Como jornalero, debo poder suscribirme a la oferta que me interese.
* **HU6.** Como propietario, debo poder ver las suscripciones a mi oferta.
* **HU7.** Como propietario, debo poder aceptar la suscripción a una oferta.
* **HU8.** Como propietario, debo poder rechazar la suscripción a una oferta.
* **HU9.** Como propietario, debo ver en mi inicio jornaleros disponibles para mis ofertas.
* **HU10.** Como propietario, debo poder proponer mi oferta al jornalero que me interese.
* **HU11.** Como jornalero, debo poder ver las propuestas de ofertas.
* **HU12.** Como jornalero, debo poder aceptar la propuesta de una oferta.
* **HU13.** Como jornalero, debo poder rechazar la propuesta de una oferta.
* **HU14.** Como jornalero, debo poder cancelar un trabajo.
* **HU15.** Como propietario, debo poder cancelar un trabajo.
* **HU16.** Como usuario (propietario o jornalero), debo poder establecer mi información de contacto.
* **HU17.** Como propietario, debo poder ver la información de contacto del jornalero con el que vaya a trabajar.
* **HU18.** Como jornalero, debo poder ver la información de contacto del propietario con el que vaya a trabajar.
* **HU19.** Como administrador, debo poder eliminar un perfil.
* **HU20.** Como administrador, debo poder eliminar una oferta.

### Funcionalidad secundaria: valoraciones

*A extender tras el desarrollo de la funcionalidad principal*

### Funcionalidad secundaria: tareas categorizadas

*A extender tras el desarrollo de la funcionalidad secundaria de valoraciones*
