from plans.plans_detect import detect_plans

def main():
    zip_file = '../../Planungen_PT1/2019-10-30_PT1_ÄM02.zip'
    detect_plans(zip_file)

if __name__ == "__main__":
    main()