# Strangeland

Tooling for the Strangeland translation.

## `add_prefixes`

Use this script to migrate an outdated translation without prefixes (like `&31`) to a new one. You need the to download
the file `add_prefixes.py` and must call it with two or three arguments, e.g.

```shell
python add_prefixes.py my_old_version.trs new_template.trs merged.trs
```

`my_old_version.trs` is the file you have been working on, containing translated bits and maybe even some prefixes here
and there.
`new_template.trs` is the latest translation file, preferably completely without any translated bits.
`merged.trs` is an optional argument specifying where the merged file shall be stored. Defaults to `merged.trs`.
Overrides any existing file

Python 3.x must be available. In case you've installed it, open the Windows Command Prompt and insert the line above. In
case you've just downloaded it somewhere and Windows doesn't know what `python` means, you must run it with

```shell
my/path/to/python.exe add_prefixes.py my_old_version.trs new_template.trs merged.trs
```

### Behavior

See `add_prefixes_test.py` for examples.

In general, it works like that:

| old version | new version | merged version  | comment |
|---|---|---|---|
| `english`<br>`translation`  | `&31 english`<br>` ` | `&31 english`<br>`&31 translation` | prefixes got taken from the new file
| `&31 english`<br>`&31 translation`  | `&31 english`<br>` ` | `&31 english`<br>`&31 translation` | prefixes in the old file do no harm
| `english`<br>` ` | `&31 english`<br>`&31 translation` | `&31 english`<br>`&31 translation` | if there's only a translation in the new file it will be used
| `english`<br>`translation` | `&31 english`<br>`&31 other` | `&31 english`<br>`&31 translation` | in doubt the translation of the old file will be used

### Prerequisites

The script runs some validations to ensure the files are similar enough to work with. This validation will fail if:

- the number of lines in both files isn't equal
- the english texts in both files are different (expect for missing prefixes, those are okay)


