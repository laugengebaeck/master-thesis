from plans.plans_load import load_plans
from plans.plans_read import PlanReaderType

def main():
    zip_file = "../../Planungen_PT1/2019-10-30_PT1_ÄM02.zip"
    # export_plan_name = None
    export_plan_name = "P-Hausen"
    load_plans(zip_file, PlanReaderType.IMAGE_OPTIMIZED, export_plan_name)

if __name__ == "__main__":
    main()