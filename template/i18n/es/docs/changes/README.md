# changes

Un archivo pequeño por cada cambio llevado a producción, con el nombre `<FILE-ID>.md` (p. ej. `GH-12.md`), que añade `/uat` en la propia rama del cambio para que viaje con él. Un archivo por cambio significa que las PR en paralelo nunca entran en conflicto aquí.

Cada archivo tiene una o dos líneas que un usuario entendería:

```
- #12: Export to CSV now works on mobile.
```

Para escribir las notas de versión o actualizar `CHANGELOG.md`, pide a un agente que recopile los archivos añadidos desde la última release.
