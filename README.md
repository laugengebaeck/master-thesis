# master-thesis

This repository contains the prototype implementation for my master thesis. In `app/src/app`, it contains code for the digitalisation of topology plans / "schematischer Übersichtsplan" (`topology_plans/`), for the digitalisation of table plans (`table_plans/`) and utility functions for both (`util/`). Both can be run via a shared main program (`main.py`).

## Setup

1. Install Python and the [Poetry dependency management tool](https://python-poetry.org/docs/#installation).
2. Install the PDF library [Poppler](https://poppler.freedesktop.org/) via the package manager of your OS.
3. Install all project dependencies using `poetry install` (if that doesn't work, try `poetry lock` beforehand).

## Usage

Run the main program from the `app` directory via `poetry run src/app/main.py [ARGUMENTS]`. The allowed arguments can be printed using `poetry run src/app/main.py --help`, but are also given here for reference.

```
usage: main.py [-h] [--topo TOPO] [--topo_example TOPO_EXAMPLE] [--table TABLE] [--default_table] [--table_reader TABLE_READER] [--table_import TABLE_IMPORT]

options:
  -h, --help            show this help message and exit
  --topo TOPO           File that contains the topology plan as PDF or PNG/JPG/...
  --topo_example TOPO_EXAMPLE
                        Slug of the example topology plan hardcoded in the program
  --table TABLE         ZIP file that contains the plan tables (as PDFs)
  --default_table       Whether to use the default plan table ZIP
  --table_reader TABLE_READER
                        Which table reader type to use (pdf/img_uopt/img_opt)
  --table_import TABLE_IMPORT
                        Basename of the CSV files that should be used for importing table data instead of OCR
```

Please note that `--topo_example` and `--default_table` rely on having the example plans (not included in the repo) at exactly the same location in your file system as on my machine, since the paths are hardcoded. These arguments are only provided as shortcuts and in most cases it makes more sense to use `--topo` and `--table`.

Also note that for the `--table_import` argument to be respected, exactly one of `--table` and `--default_table` also has to be set.

## Thesis document

You can probably find my thesis in the [OSM Bookshelf](https://osm.hpi.de/bookshelf/) by searching for

> Automatisierte Bestandsplandigitalisierung in der Eisenbahninfrastrukturplanung

It contains more explanations about how this implementation and the algorithms used in it work. If you don't have access to the OSM Bookshelf, you can request the thesis via e-mail (address in profile).
