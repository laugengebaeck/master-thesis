from tables.table_crop import pdf_get_table_images
from tables.table_ocr import tables_perform_ocr

def main():
    pdf_file = '../../Planungen_PT1/2019-10-30_PT1_ÄM02/P-Hausen_Sig1_ÄM02.pdf'
    table_images = pdf_get_table_images(pdf_file)
    table_dfs = tables_perform_ocr(table_images, min_confidence=30)
    for df in table_dfs:
        print(df)

if __name__ == "__main__":
    main()