from argparse import ArgumentParser, Namespace

from table_plans.main import table_main
from table_plans.pdf_read import PlanReaderType
from topology_plans.main import topology_main

DEFAULT_ZIP = "../../Planungen_PT1/2019-10-30_PT1_ÄM02.zip"


def parse_args() -> Namespace:
    parse = ArgumentParser()
    parse.add_argument("--topo", help="File that contains the topology plan as PDF or PNG/JPG/...")
    parse.add_argument(
        "--topo_example", help="Slug of the example topology plan hardcoded in the program"
    )
    parse.add_argument("--table", help="ZIP file that contains the plan tables (as PDFs)")
    parse.add_argument(
        "--default_table", action="store_true", help="Whether to use the default plan table ZIP"
    )
    parse.add_argument(
        "--table_reader", help="Which table reader type to use (pdf/img_uopt/img_opt)"
    )
    parse.add_argument(
        "--table_import",
        help="Basename of the CSV files that should be used for importing table data instead of OCR",
    )
    return parse.parse_args()


def main():
    args = parse_args()

    if args.topo is not None or args.topo_example is not None:
        topology_main(args.topo, args.topo_example)

    if args.table is not None:
        plan_reader_type = PlanReaderType.IMAGE_OPTIMIZED
        if args.table_reader == "pdf":
            plan_reader_type = PlanReaderType.PDF_TEXT
        elif args.table_reader == "img_uopt":
            plan_reader_type = PlanReaderType.IMAGE_UNOPTIMIZED
        table_main(
            DEFAULT_ZIP if args.default_table else args.table, plan_reader_type, args.table_import
        )


if __name__ == "__main__":
    main()
