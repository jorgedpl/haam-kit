# changes

One small file per shipped change, named `<FILE-ID>.md` (e.g. `GH-12.md`), added by `/uat` on the change's own branch so it ships with it. One file per change means parallel PRs never conflict here.

Each file is one or two lines a user would understand:

```
- #12: Export to CSV now works on mobile.
```

To write release notes or update `CHANGELOG.md`, ask an agent to collect the files added since the last release.
