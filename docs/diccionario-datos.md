# Diccionario de datos de ReForest

Tarea: HT00-T00-API. Diseño para PostgreSQL 17; consultar [modelo-relacional.md](modelo-relacional.md) para relaciones, permisos y trazabilidad.

## Reglas comunes

UUID es el tipo de todas las claves; se genera en la aplicación, sin extensión PostgreSQL obligatoria. Todas las columnas son NOT NULL salvo observacion. Los textos obligatorios tienen CHECK(length(btrim(columna)) > 0), además de su límite VARCHAR. Los valores enumerados se representan mediante VARCHAR y CHECK IN, evitando tipos ENUM nativos por ahora.

created_at y updated_at usan TIMESTAMPTZ, con DEFAULT CURRENT_TIMESTAMP. El servicio debe actualizar updated_at en cada modificación; el valor por defecto no lo actualiza automáticamente. Inscripciones solo tiene created_at. La conexión y la serialización usan UTC.

Las claves foráneas usan ON DELETE RESTRICT y ON UPDATE NO ACTION. Los identificadores son inmutables. PRIMARY KEY y UNIQUE crean sus índices: no se duplican con índices adicionales. Los índices listados son B-tree.

## users

| Columna | Tipo | Nula | Valor inicial | Restricciones / significado |
|---|---|---|---|---|
| id | UUID | No | Generado por aplicación | PRIMARY KEY |
| nombre | VARCHAR(120) | No | Sin defecto | Texto no vacío |
| correo | VARCHAR(254) | No | Sin defecto | UNIQUE; no vacío; CHECK(correo = lower(btrim(correo))); formato validado por FastAPI. El límite 254 es una decisión de diseño. |
| password_hash | TEXT | No | Sin defecto | Hash no vacío; nunca contraseña en claro ni salida pública |
| rol | VARCHAR(13) | No | Sin defecto | CHECK IN ('CIUDADANO', 'VOLUNTARIO', 'ENTIDAD', 'ADMINISTRADOR') |
| activo | BOOLEAN | No | TRUE | Estado de habilitación del usuario |
| created_at | TIMESTAMPTZ | No | CURRENT_TIMESTAMP | Creación |
| updated_at | TIMESTAMPTZ | No | CURRENT_TIMESTAMP | Última modificación |

Índices: PRIMARY KEY(id) y UNIQUE(correo). No se añade un índice separado de correo ni de rol sin una consulta que lo justifique. El rol ADMINISTRADOR es válido en la base, pero está prohibido en el registro público por el servicio.

## incendios

| Columna | Tipo | Nula | Valor inicial | Restricciones / significado |
|---|---|---|---|---|
| id | UUID | No | Generado por aplicación | PRIMARY KEY |
| descripcion | VARCHAR(500) | No | Sin defecto | Texto no vacío, compatible con UTF-8 |
| latitud | NUMERIC(9,6) | No | Sin defecto | CHECK(latitud BETWEEN -90 AND 90) |
| longitud | NUMERIC(10,6) | No | Sin defecto | CHECK(longitud BETWEEN -180 AND 180) |
| estado | VARCHAR(10) | No | 'ACTIVO' | CHECK IN ('ACTIVO', 'CONTROLADO', 'EXTINGUIDO'); la API fija el valor inicial |
| reportado_por | UUID | No | Usuario autenticado | FOREIGN KEY -> users.id; ON DELETE RESTRICT |
| created_at | TIMESTAMPTZ | No | CURRENT_TIMESTAMP | Fecha del reporte |
| updated_at | TIMESTAMPTZ | No | CURRENT_TIMESTAMP | Última modificación |

Índices adicionales: ix_incendios_estado(estado), ix_incendios_created_at(created_at), ix_incendios_reportado_por(reportado_por), según el plan. Validar rangos antes de persistir y definir el tratamiento de más de seis decimales en los esquemas de HU01. Las coordenadas válidas permiten representar marcadores en el mapa; no se requiere PostGIS para este alcance.

## donaciones

| Columna | Tipo | Nula | Valor inicial | Restricciones / significado |
|---|---|---|---|---|
| id | UUID | No | Generado por aplicación | PRIMARY KEY |
| donante_id | UUID | No | Sin defecto | FOREIGN KEY -> users.id; ON DELETE RESTRICT; el servicio comprueba ENTIDAD |
| especie_o_insumo | VARCHAR(150) | No | Sin defecto | Texto no vacío |
| cantidad | INTEGER | No | Sin defecto | CHECK(cantidad > 0); FastAPI debe rechazar decimales, sin coerción ni truncamiento |
| observacion | VARCHAR(500) | Sí | NULL | Texto opcional |
| created_at | TIMESTAMPTZ | No | CURRENT_TIMESTAMP | Creación |
| updated_at | TIMESTAMPTZ | No | CURRENT_TIMESTAMP | Última modificación |

Índice adicional: ix_donaciones_donante_id(donante_id), para la relación con users. La correspondencia del campo donante del contrato queda pendiente; no se introduce una columna adicional sin definirlo.

## jornadas

| Columna | Tipo | Nula | Valor inicial | Restricciones / significado |
|---|---|---|---|---|
| id | UUID | No | Generado por aplicación | PRIMARY KEY |
| nombre | VARCHAR(150) | No | Sin defecto | Texto no vacío |
| fecha | TIMESTAMPTZ | No | Sin defecto | Fecha y hora de la actividad; FastAPI valida la entrada |
| lugar | VARCHAR(200) | No | Sin defecto | Texto no vacío |
| cupo_total | INTEGER | No | Sin defecto | CHECK(cupo_total > 0); entrada entera estricta |
| creada_por | UUID | No | Usuario autenticado | FOREIGN KEY -> users.id; ON DELETE RESTRICT; el servicio comprueba ADMINISTRADOR |
| created_at | TIMESTAMPTZ | No | CURRENT_TIMESTAMP | Creación |
| updated_at | TIMESTAMPTZ | No | CURRENT_TIMESTAMP | Última modificación |

Índice adicional: ix_jornadas_creada_por(creada_por), para la relación con users. No hay columna cupo_disponible: se calcula con inscripciones. La política de jornadas pasadas y disponibles=true debe concretarse en HU09 antes de añadir índices o restricciones relacionados con fechas.

## inscripciones

| Columna | Tipo | Nula | Valor inicial | Restricciones / significado |
|---|---|---|---|---|
| id | UUID | No | Generado por aplicación | PRIMARY KEY |
| jornada_id | UUID | No | Jornada solicitada | FOREIGN KEY -> jornadas.id; ON DELETE RESTRICT |
| voluntario_id | UUID | No | Usuario autenticado | FOREIGN KEY -> users.id; ON DELETE RESTRICT; el servicio comprueba VOLUNTARIO |
| created_at | TIMESTAMPTZ | No | CURRENT_TIMESTAMP | Fecha de inscripción |

Restricción uq_inscripciones_jornada_voluntario: UNIQUE(jornada_id, voluntario_id).

Índices: PRIMARY KEY(id), el índice único compuesto y ix_inscripciones_voluntario_id(voluntario_id). El índice compuesto ya cubre búsquedas por jornada_id, por ser su primera columna; no se añade un índice redundante sobre jornada_id. Ambas relaciones quedan indexadas.

El límite de cupo depende de otras filas y no se resuelve con un CHECK sobre esta tabla. Se garantiza con la transacción y bloqueo de jornada descritos en el modelo relacional. Cada fila representa una inscripción confirmada; no hay estado de inscripción en el alcance actual.

## Restricciones que deben probar las futuras migraciones

- Correo duplicado o sin normalizar; campos obligatorios vacíos; rol y estado desconocidos.
- Coordenadas fuera de rango y longitudes de texto excesivas.
- Cantidad o cupo no positivos; entradas decimales rechazadas por FastAPI.
- Claves foráneas inexistentes y eliminación de padres referenciados.
- Inscripción duplicada y solicitudes concurrentes para el último cupo.

Estas verificaciones son criterios para las historias de implementación. HT00 documenta las restricciones y no ejecuta ni crea migraciones.
