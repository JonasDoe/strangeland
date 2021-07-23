# Strangeland

Tooling for the Strangeland translation (and other AGS translation files).

## `add_prefixes.py`

Note that this feature will be renamed soon since the focus of this project is shifting towards an interactive
validation/merge process (see validation infos below). Use this script to migrate an outdated translation without
prefixes (like `&31`) to a new one.

## Installation

You need to download `add_prefixes.py` and `requirements.txt` and have python installed.

## Running the Script

You can call the script with one to four arguments, e.g.

```shell
python add_prefixes.py my_translation.trs --template=template.trs --encoding=utf-8 --output=merged.trs
```

- The mandatory argument, here `my_translation.trs`, is the file you have been working on, containing translated bits
  and maybe even some prefixes here and there.
- `--template` specifies the latest translation file, preferably completely without any translated bits. Updates from
  here can shoved into the translation file. If it's not set, no lines will be validated against a template. Suffixes
  from english lines in the translation file will still be added to translated lines where missing, and different
  suffixes between both lines will be reported.
- `--encoding` specifies the encoding of the input files and of the output file. Optional - when left empty,
  auto-detection will be triggered. If you're facing issues with that, set the encoding manually with this argument,
  e.g. to `utf-8` or `cp1252`. Make sure all files have the same encoding in that case.
- `--output` specifies where the merged/fixed file shall be stored. Optional, defaults to `merged.trs`. Overrides any
  existing file

File paths are allowed. Note that in case the file locations contain any spaces, they must be put in quotes. So a file
input might look like e.g. `"strangeland\german - version 1.trs"`.

Python 3 or higher must be available. In case you've already installed it, open the Windows Command Prompt and insert
the line above. In case you've just downloaded it somewhere and Windows doesn't know what `python` means, you must run
it with something like

```shell
my\path\to\python.exe add_prefixes.py my_translation.trs --template=template.trs
```

### Merging Behavior

In case there's a template file specified, lines will be merged the following way:

| translated version | (new) template version | merged version  | comment |
|---|---|---|---|
| `English`<br>`German`  | `&31 English`<br>` ` | `&31 English`<br>`&31 German` | prefixes got taken from the template file
| `&31 English`<br>`&31 German`  | `&31 English`<br>` ` | `&31 English`<br>`&31 German` | prefixes in the translated file do no harm
| `English`<br>` ` | `&31 English`<br>`&31 German` | `&31 English`<br>`&31 German` | if there's only a translation in the template file it will be used
| `English`<br>`German` | `&31 English`<br>`&31 Other` | `&31 English`<br>`&31 German` | in doubt the translation from  the translation file will be used

See `add_prefixes_test.py` for examples.

### Validation

The script runs some validations to ensure the files are similar enough to work with. This validation will fail if:

- the number of lines in both files isn't equal
- the English texts in both files are different (expect for missing prefixes, those are okay)
- the prefix in the translated line differs from the english one above
- other, more unlikely cases

For certain cases, interactive solving is possible (see `Validation`).

In case English texts are different, you will be asked on how to proceed, so you can fix those issues on the fly.

In general, your run will look like this:

```
(venv) C:\Users\Jonas\strangeland>python add_prefixes.py german.trs --template=english.trs
Line 2605 differs:
Because... we were already dead. (german.trs)
&287 Because... we were already condemned. (english.trs)

The translation is:
Weil ... wir schon tot sind. (german.trs)

Enter number:
(1) Keep english line from template.trs and translation from translation.trs
(2) Keep english line from template.trs and enter new custom line
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
(1) Keep english line from template.trs and translation from translation.trs
(2) Keep english line from template.trs and enter new custom line
(3) Abort
1
--------------
Line 2659 differs:
Wow. (german.trs)
&3 Wow.    (english.trs)

The translation is:
Wow. (german.trs)

Enter number:
(1) Keep english line from template.trs and translation from translation.trs
(2) Keep english line from template.trs and enter new custom line
(3) Abort
1
...
```

As you can see, most times you're gonna select option `1`, just taking the new English template line and the old
translation line. For cases like `&287 Because... we were already condemned.`, where something more has changed in
content, you can choose option `2` and write a new translation line. In case you're not sure but don't want to abort, I
to recommend taking something like `???` as the translation, so you can find and fix it later.

In case you abort at some point (option `3`), all processed lines and all decisions made up to this point will be stored
in the output file. It might be a good idea to take these and replace the regarding lines in your input file before the
next run. If you don't do that and just run the script again, all the effort you've put into merging up to this point is
lost!

## Shortcomings

- It's pure cli-tool and is not recommended if there are huge changes to be merged. Resort to another tool like
  [WinMerge](https://winmerge.org) in that case. Once all major changes have been sorted out, you can go back to this
  tool.
- There's no rewind option. If you are in a semi-trance while tapping 1 + ENTER, you might accept a translation which
  could have needed some adjustments. You have to scroll up and write it down for later, or you have to abort, merge
  your work to this point into your translation file, fix what you've forgotten and re-run the script to continue.
- It's often hard to see the differences between old and new. I know, but for now I want this script to have as little
  requirements as possible, so colored fonts or sophisticated text diff analysis have to wait until there's really
  massive need for that.

## Troubleshooting

### I get the error `Aborted: Python 3.x required`

You're using the wrong Python version. Even if you have Python 3 on your computer, it might be that the command `python`
still points to an older installment. You can run `python -v` to see which version is actually used. Adjust your `PATH`
variable accordingly. If you don't know how to do that, don't run the script with `python` but
with `full/path/to/python/with/correct/version/python.exe` (or without `.exe` on non-Windows systems).

### I get an UnicodeDecodeError

You've set a wrong encoding, e.g. a cp1252-encoded file with utf-8 encoding set. Try to run the script with the another
encoding or remove the encoding for auto-detection.

### I get weird letters displayed

You're reading a file with the wrong encoding set. Make sure that translation as well as the template file have the same
encoding. Run the script with no encoding to enable auto-detection or try to run it with the proper `--encoding`
argument. If that doesn't help, resort to the next section.

### I don't get all this encoding stuff figured out

Open the files you're using in Notepad++. Select `Encoding -> Convert to UTF-8`. Save the files. Run the script
with `--enconding=utf8`.

### The script takes years to start

Maybe the files are unreasonable large. Split them into smaller ones. Or the auto-detection of the proper encoding is
slowing down the process. Set the encoding manually.

### The command `python` isn't found

Download the latest python installer from [python.org](https://www.python.org) for your platform and run it.
