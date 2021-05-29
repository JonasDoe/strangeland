# Strangeland

Tooling for the Strangeland translation.

## `add_prefixes`

Note that this feature will be renamed soon since the focus of this project is shifting towards an interactive
validation/merge process (see validation infos below).

Use this script to migrate an outdated translation without prefixes (like `&31`) to a new one. You need the to download
the file `add_prefixes.py` and must call it with two to four arguments, e.g.

```shell
python add_prefixes.py my_old_version.trs new_template.trs utf-8 merged.trs
```

`my_old_version.trs` is the file you have been working on, containing translated bits and maybe even some prefixes here
and there.
`new_template.trs` is the latest translation file, preferably completely without any translated bits.
`utf-8` is the encoding of the input files and of the output file. Optional, defaults to `utf-8`.
`merged.trs` is an optional argument specifying where the merged file shall be stored. Optional, defaults
to `merged.trs`. Overrides any existing file

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
| `English`<br>`German`  | `&31 English`<br>` ` | `&31 English`<br>`&31 German` | prefixes got taken from the new file
| `&31 English`<br>`&31 German`  | `&31 English`<br>` ` | `&31 English`<br>`&31 German` | prefixes in the old file do no harm
| `English`<br>` ` | `&31 English`<br>`&31 German` | `&31 English`<br>`&31 German` | if there's only a translation in the new file it will be used
| `English`<br>`German` | `&31 English`<br>`&31 Other` | `&31 English`<br>`&31 German` | in doubt the translation of the old file will be used

### Prerequisites

The script runs some validations to ensure the files are similar enough to work with. This validation will fail if:

- the number of lines in both files isn't equal
- the English texts in both files are different (expect for missing prefixes, those are okay)
- other, more unlikely cases

For certain cases, interactive solving is possible (see `Validation`).

### Validation

Note that in case English texts are different, you will be asked on how to proceed, so you can fix those issues on the
fly.

In general, your run will look like this:

```
(venv) C:\Users\Jonas\strangeland>python add_prefixes.py german.trs english.trs
Line 2605 differs:
Because... we were already dead. (german.trs)
&287 Because... we were already condemned. (english.trs)

The translation is:
Weil ... wir schon tot sind. (german.trs)

Enter number:
(1) Keep new english line and old translation line
(2) Keep new english line and enter new custom line
(3) Abort
2

New translation:
Weil ... wir schon verdammt sind.
--------------
Line 2651 differs:
No (german.trs)
No    (english.trs)

The translation is:
Nein. (german.trs)

Enter number:
(1) Keep new english line and old translation line
(2) Keep new english line and enter new custom line
(3) Abort
1
--------------
Line 2659 differs:
Wow. (german.trs)
&3 Wow.    (english.trs)

The translation is:
Wow. (german.trs)

Enter number:
(1) Keep new english line and old translation line
(2) Keep new english line and enter new custom line
(3) Abort
1
...
```

As you can see, most of the times you'll gonna select option `1`, just taking the new english line and the old
translation line. For cases like `&287 Because... we were already condemned.`, where something more has changed in
content, you can chose option `2` and write a new translation line. In case you're not sure but don't want to abort,
I'ld to recommend marking the translation just with something line `(???)` you can find later.

In case you abort at some point (option `3`), all processed lines and all decisions made up to this point will be stored
in the target file. It might be a good idea to take these and replace the regarding lines in your input file before the
next run. If you don't do that and run the script again, all the effort you've put into merging up to this point is
lost!

## Shortcomings

- It's pure cli-tool and is not recommended if there are huge changes to be merged. Resort to another tool like [
  WinMerge](https://winmerge.org) in that case. Once all major changes have been sorted out, you can go back to this
  tool.
- There's no back-option. If you are in a semi-trance while tapping 1 + ENTER, you might accept a translation which
  could have needed some adjustments. You have to scroll up and write it down for later, or you have abort, merge your
  state into your old translation file, fix what you've forgotten and re-run the script to continue.
- It's often hard to see the differences between old and new. I know, but for now I want this script to have as little
  requirements as possible, so colored fonts or sophisticated text diff analysis has to wait until there's really
  massive need for that.
