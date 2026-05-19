from time_table_service import time_table_maker

if __name__ == '__main__':
    # Test 1
    print("* Runing test 1:")
    teachers = {
        "T1": {"name": "استاد کرمانیان", "teacher_available_times": [0, 1, 2, 4, 5, 8, 9, 10]},
        "T2": {"name": "استاد علوی", "teacher_available_times": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]},
        "T3": {"name": "استاد رضایی", "teacher_available_times": [12, 13, 14, 15, 16, 17, 18, 19]}
    }
    
    courses = {
        "C1": {"name": "ساختمان داده", "credits": 3, "cohort": "1403", "teachers": ["T1"]},
        "C2": {"name": "برنامه‌نویسی پیشرفته", "credits": 4, "cohort": "1404", "teachers": ["T2"]},
        "C3": {"name": "ریاضیات گسسته", "credits": 3, "cohort": "1404", "teachers": ["T1", "T3"]},
        "C4": {"name": "هوش مصنوعی", "credits": 2, "cohort": "1402", "teachers": ["T3"]},
        "C5": {"name": "هوش مصنوعی", "credits": 3, "cohort": "1402", "teachers": ["T1"]},
        "C6": {"name": "آزمایشگاه فیزیک", "credits": 1, "cohort": "1405", "teachers": ["T3"]}
    }
    cohorts = ["1402", "1403", "1404", "1405"]
    days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday"]
    
    time_table_maker(teachers=teachers, courses=courses, print_result=True, cohorts=cohorts, days=days)
    print("* Test 1 done.")
    
    # Test 2
    print("* Runing test 2:")
    teachers = {
        "T1": {"name": "Prof. A","teacher_available_times":list(range(20))},                                           
        "T2": {"name": "Prof. B","teacher_available_times":[0, 1, 2, 3, 4, 5, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19]},  
        "T3": {"name": "Prof. C","teacher_available_times":list(range(20))},
        "T4": {"name": "Prof. D","teacher_available_times":[2, 3, 4, 5, 6, 7, 10, 11, 14, 15, 16, 17, 18, 19]},                                           
        "T5": {"name": "Prof. E","teacher_available_times":list(range(20))},
        "T6": {"name": "Prof. F","teacher_available_times":[0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17]}, 
        "T7": {"name": "Prof. G","teacher_available_times":list(range(20))},
    }

    courses = {
        # ================= Cohort 2026 =================
        "C26_1":  {"name": "C26_Course_1", "cohort": "2026", "credits": 3, "teachers": ["T1"]},
        "C26_2":  {"name": "C26_Course_2", "cohort": "2026", "credits": 3, "teachers": ["T4"]},
        "C26_3":  {"name": "C26_Course_3", "cohort": "2026", "credits": 1, "teachers": ["T1"]},
        "C26_4":  {"name": "C26_Course_4", "cohort": "2026", "credits": 2, "teachers": ["T7"]},
        "C26_5":  {"name": "C26_Course_5", "cohort": "2026", "credits": 3, "teachers": ["T2"]},
        "C26_6":  {"name": "C26_Course_6", "cohort": "2026", "credits": 1, "teachers": ["T2"]},
        "C26_7":  {"name": "C26_Course_7", "cohort": "2026", "credits": 2, "teachers": ["T3"]},
        "C26_8":  {"name": "C26_Course_8", "cohort": "2026", "credits": 3, "teachers": ["T4"]},
        "C26_9":  {"name": "C26_Course_9", "cohort": "2026", "credits": 1, "teachers": ["T5"]},
        "C26_10": {"name": "C26_Course_10", "cohort": "2026", "credits": 2, "teachers": ["T7"]},

        # ================= Cohort 2025 =================
        "C25_1":  {"name": "C25_Course_1", "cohort": "2025", "credits": 3, "teachers": ["T1"]},
        "C25_2":  {"name": "C25_Course_2", "cohort": "2025", "credits": 3, "teachers": ["T2"]},
        "C25_3":  {"name": "C25_Course_3", "cohort": "2025", "credits": 2, "teachers": ["T4"]},
        "C25_4":  {"name": "C25_Course_4", "cohort": "2025", "credits": 1, "teachers": ["T5"]},
        "C25_5":  {"name": "C25_Course_5", "cohort": "2025", "credits": 3, "teachers": ["T7"]},
        "C25_6":  {"name": "C25_Course_6", "cohort": "2025", "credits": 2, "teachers": ["T1"]},
        "C25_7":  {"name": "C25_Course_7", "cohort": "2025", "credits": 1, "teachers": ["T2"]},
        "C25_8":  {"name": "C25_Course_8", "cohort": "2025", "credits": 3, "teachers": ["T3"]},
        "C25_9":  {"name": "C25_Course_9", "cohort": "2025", "credits": 2, "teachers": ["T6"]},
        "C25_10": {"name": "C25_Course_10", "cohort": "2025", "credits": 1, "teachers": ["T7"]},

        # ================= Cohort 2024 =================
        "C24_1":  {"name": "C24_Course_1", "cohort": "2024", "credits": 3, "teachers": ["T3"]},
        "C24_2":  {"name": "C24_Course_2", "cohort": "2024", "credits": 3, "teachers": ["T4"]},
        "C24_3":  {"name": "C24_Course_3", "cohort": "2024", "credits": 2, "teachers": ["T5"]},
        "C24_4":  {"name": "C24_Course_4", "cohort": "2024", "credits": 1, "teachers": ["T6"]},
        "C24_5":  {"name": "C24_Course_5", "cohort": "2024", "credits": 3, "teachers": ["T2"]},
        "C24_6":  {"name": "C24_Course_6", "cohort": "2024", "credits": 2, "teachers": ["T3"]},
        "C24_7":  {"name": "C24_Course_7", "cohort": "2024", "credits": 1, "teachers": ["T1"]},
        "C24_8":  {"name": "C24_Course_8", "cohort": "2024", "credits": 3, "teachers": ["T4"]},
        "C24_9":  {"name": "C24_Course_9", "cohort": "2024", "credits": 2, "teachers": ["T5"]},
        "C24_10": {"name": "C24_Course_10", "cohort": "2024", "credits": 1, "teachers": ["T2"]},

        # ================= Cohort 2023 =================
        "C23_1":  {"name": "C23_Course_1", "cohort": "2023", "credits": 3, "teachers": ["T6"]},
        "C23_2":  {"name": "C23_Course_2", "cohort": "2023", "credits": 3, "teachers": ["T7"]},
        "C23_3":  {"name": "C23_Course_3", "cohort": "2023", "credits": 2, "teachers": ["T1"]},
        "C23_4":  {"name": "C23_Course_4", "cohort": "2023", "credits": 1, "teachers": ["T2"]},
        "C23_5":  {"name": "C23_Course_5", "cohort": "2023", "credits": 3, "teachers": ["T4"]},
        "C23_6":  {"name": "C23_Course_6", "cohort": "2023", "credits": 2, "teachers": ["T5"]},
        "C23_7":  {"name": "C23_Course_7", "cohort": "2023", "credits": 1, "teachers": ["T6"]},
        "C23_8":  {"name": "C23_Course_8", "cohort": "2023", "credits": 3, "teachers": ["T7"]},
        "C23_9":  {"name": "C23_Course_9", "cohort": "2023", "credits": 2, "teachers": ["T3"]},
        "C23_10": {"name": "C23_Course_10", "cohort": "2023", "credits": 1, "teachers": ["T4"]}
    }
    time_table_maker(teachers=teachers, courses=courses, print_result=True)
    print("* Test 2 done.")
    
    
    