# Especificación: <ID> <título>

- **Issue:** <#123 o APP-123> · **Evaluación:** docs/assessments/<FILE-ID>-*.md · **ADR:** <enlaces o ninguno>
- **Estado:** Borrador / Aprobada · **Aprobada por:** <persona> el YYYY-MM-DD
- **Áreas protegidas:** ninguna / <lista> → `human-review`

## 1. Objetivo
<!-- Un párrafo: qué cambia, para quién y por qué. -->

## 2. Historias de usuario
- Como <rol>, quiero <capacidad>, para <beneficio>.

## 3. Criterios de aceptación
<!-- Cada criterio debe poder probarse. Numéralos; las pruebas y los pasos de UAT hacen referencia a estos números. -->
**AC1:** <nombre>
- Given …
- When …
- Then …

**AC2:** …

## 4. Fuera del alcance
- 

## 5. Notas de diseño
- **Archivos o módulos que probablemente se tocan:** 
- **Modelo de datos / migraciones:** ninguno / <descríbelo, incluido el relleno de datos existentes y si es reversible>
- **Configuración / variables de entorno:** ninguna / <nombres, y añádelas a .env.example>
- **API externas:** 
- **Notas de interfaz / textos:** 
- **Estados de error y casos límite:** 

## 6. Plan de pruebas
| AC | Prueba(s) unitaria(s) o de integración | Notas |
|---|---|---|
| AC1 | `test_…` | |

**Esbozo de la UAT:** <lo que una persona recorrerá en local>

## 7. Despliegue y marcha atrás
- **Feature flag:** ninguna / <nombre>
- **Despliegue:** 
- **Marcha atrás:** <¿basta con una PR que revierta el cambio? ¿hay datos que limpiar?>

## 8. Porciones (si se divide)
| Sub-issue | Alcance | Depende de |
|---|---|---|

## 9. Preguntas abiertas
1. 
