# Mapa de la arquitectura

> Los agentes leen esto al principio de cada sesión (lo importa `AGENTS.md`). Es un **mapa**, no una documentación completa: lo justo para que un agente nuevo se oriente en dos minutos.
> Los agentes lo mantienen al día: si tu PR cambia la estructura o descubres una trampa, actualiza este archivo en la misma PR.
>
> **Configuración inicial:** pídele a tu agente de programación: *"Explora este repositorio y rellena docs/product/ARCHITECTURE.md siguiendo los títulos de sus secciones. Que no pase de 150 líneas."* Después revísalo tú.

## Stack
- Lenguaje / framework: `TODO`
- Base de datos: `TODO`
- Hosting / destino del despliegue: `TODO`
- Servicios externos clave: `TODO` (API, correo, pagos, proveedores de autenticación…)

## Estructura del repositorio
```
TODO: top-level folders and what lives in each
```

## Módulos principales
| Módulo / ruta | Responsabilidad | ¿Área protegida? |
|---|---|---|
| `TODO` | | |

## Modelo de datos (entidades clave)
`TODO`

## Entornos
| Entorno | URL | Cómo se despliega |
|---|---|---|
| Local | http://localhost:`TODO` | `make dev` |
| Producción | `TODO` | GitHub Actions `deploy.yml`, requiere aprobación |

## Configuración
- Las variables de entorno están documentadas en `.env.example` (nunca hagas commit de valores reales).

## Pruebas
- Las pruebas unitarias están en `TODO` y se ejecutan con `make test`.
- Fixtures de prueba sintéticos: `TODO` (nunca uses datos personales reales).
- E2E / navegador: `TODO`

## Trampas
- `TODO`: cosas que ya les han dado problemas a agentes o desarrolladores.
