# changes

Eine kleine Datei pro ausgelieferter Änderung, benannt `<FILE-ID>.md` (z. B. `GH-12.md`), von `/uat` auf dem eigenen Branch der Änderung hinzugefügt, sodass sie mit ihr ausgeliefert wird. Eine Datei pro Änderung heißt, dass parallele PRs hier nie in Konflikt geraten.

Jede Datei besteht aus ein oder zwei Zeilen, die ein Nutzer verstehen würde:

```
- #12: Export to CSV now works on mobile.
```

Um Release Notes zu schreiben oder `CHANGELOG.md` zu aktualisieren, bitte einen Agenten, die seit dem letzten Release hinzugefügten Dateien zu sammeln.
