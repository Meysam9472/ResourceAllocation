from ortools.sat.python import cp_model

def time_table_maker(number_of_rooms:int=3, cohorts:list=["2023", "2024", "2025", "2026"], 
         days:list=["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday"],
         hours:list=["8:00 AM", "10:00 AM", "14:00 PM", "16:00 PM"], teachers:dict={}, courses:dict={}):
    
    number_of_rooms = number_of_rooms
    cohorts = cohorts
    
    days = days
    hours = hours
    day_slots = len(days) * len(hours)
    
    def get_time_str(time_slot_number):
        """
        :param time_slot_number: A value between 0 and len(days) * len(hours). For 4 day times and 5 days
                                 this value is from 0 to 19.
        """
        day = days[time_slot_number // 4]
        hour = hours[time_slot_number % 4]
        return f"{day} at {hour}"
    
    model = cp_model.CpModel()
    
    # X is a dict for saving decision variables,
    # if X[(c_id, s, t, tr)] == 1 means the session==s(1 or 2(in fact 0 or 1)) of course==c_id at time==t will be holded
    # by teacher==tr.
    X = {}
    
    # Calculating number of sessions for each course. For 3 or 4 units courses there are 2 class times in a 
    # week and for 1 or 2 units there is 1 class time in a week.
    courses_number_of_sessions_dict = {}
    for c_id, c_data in courses.items():
        courses_number_of_sessions_dict[c_id] = 2 if c_data["credits"] >= 3 else 1
    
    # Defining valid variables for X
    for c_id, c_data in courses.items():
        for s in range(courses_number_of_sessions_dict[c_id]):
            for tr_id in c_data["teachers"]:
                for tr_av_times in teachers[tr_id]["teacher_available_times"]:
                    X[(c_id, s, tr_av_times, tr_id)] = model.NewBoolVar(f'X_c{c_id}_s{s}_tr_av_times{tr_av_times}_tr{tr_id}')
    
    # Constraint 1: Each session of each course should be held by one teacher at one time.
    for c_id, c_data in courses.items():
        for s in range(courses_number_of_sessions_dict[c_id]):
            valid_vars = []
            for tr_id in c_data["teachers"]:
                for tr_avail_time in teachers[tr_id]["teacher_available_times"]:
                    valid_vars.append(X[(c_id, s, tr_avail_time, tr_id)])
            if len(valid_vars) == 0:
                print(f"Timetable is not able to be created because for {c_data['name']} course we don't have\
                      any teacher.")
                return
            
            model.AddExactlyOne(valid_vars) # Only one value should be 1 and other values should be 0s.
    
    # Constraint 2: If a course has 2 sessions, the SAME teacher must teach both
    for c_id, c_data in courses.items():
        if courses_number_of_sessions_dict[c_id] == 2:
            for tr_id in c_data["teachers"]:
                 # Number of times teacher 'tr_id' teaches session 0 for a course
                teaches_s0 = sum(X[(c_id, 0, t, tr_id)] for t in teachers[tr_id]["teacher_available_times"])
                 # Number of times teacher 'tr_id' teaches session 1 for a course
                teaches_s1 = sum(X[(c_id, 1, t, tr_id)] for t in teachers[tr_id]["teacher_available_times"])
                # Both sessions should be same(for a teacher both of them must be 0 or 1)
                model.Add(teaches_s0 == teaches_s1)

    # Constraint 3: No cohort overlap (A cohort cannot have 2 classes at the same time)
    for cohort in cohorts:
        cohort_courses = [c_id for c_id, c_data in courses.items() if c_data["cohort"] == cohort]
        for t in range(day_slots):
            t_vars = [] # All related variables for having a class at this time slot. We must have 0 or 1 classes at this time.
            for c_id in cohort_courses:
                for s in range(courses_number_of_sessions_dict[c_id]):
                    for tr_id in courses[c_id]["teachers"]:
                        if t in teachers[tr_id]["teacher_available_times"]:
                            t_vars.append(X[(c_id, s, t, tr_id)])
            model.Add(sum(t_vars) <= 1)
    
    # Constraint 4: No teacher overlap (A teacher cannot teach 2 classes at the same time)
    for tr_id, th_data in teachers.items():
        for t in th_data["teacher_available_times"]:
            t_vars = [] 
            for c_id, c_data in courses.items():
                if tr_id in c_data["teachers"]:
                    for s in range(courses_number_of_sessions_dict[c_id]):
                        t_vars.append(X[(c_id, s, t, tr_id)])
            # The total number of classes for this teacher at time 't' must be <= 1
            if t_vars:
                model.Add(sum(t_vars) <= 1)

    # Constraint 5: Room limit (Total classes at any time 't' cannot exceed number_of_rooms)
    for t in range(day_slots):
        all_active_classes_at_t = []
        for c_id, c_data in courses.items():
            for s in range(courses_number_of_sessions_dict[c_id]):
                for tr_id in c_data["teachers"]:
                    if t in teachers[tr_id]["teacher_available_times"]:
                        all_active_classes_at_t.append(X[(c_id, s, t, tr_id)])
        if all_active_classes_at_t:
            model.Add(sum(all_active_classes_at_t) <= number_of_rooms)

    # Constraint 6: No same-day sessions for 3-4 credit courses (courses with >1 sessions)
    for c_id, c_data in courses.items():
        if courses_number_of_sessions_dict[c_id] == 2:
            for day in range(5):
                # Slots for this specific day(for day=0 slots are 0,1,2,3)
                day_slots = [day * 4 + i for i in range(4)]
                
                classes_tris_day = []
                for s in range(2):
                    for tr_id in c_data["teachers"]:
                        for t in day_slots:
                            if t in teachers[tr_id]["teacher_available_times"]:
                                classes_tris_day.append(X[(c_id, s, t, tr_id)])
                # Maximum 1 session of this course per day
                if classes_tris_day:
                    model.Add(sum(classes_tris_day) <= 1)

    # 4.SOLVE AND PRINT RESULTS
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Schedule generated successfully!\n")
        print("="*60)
        
        # Find all scheduled sessions for this cohort
        for cohort in cohorts:
            print(f"--- Cohort {cohort} scheduled ---")
            cohort_has_class = False
            
            # Sorting by time for better exhibition
            schedule = []
            for c_id, c_data in courses.items():
                if c_data["cohort"] != cohort:
                    continue
                for s in range(courses_number_of_sessions_dict[c_id]):
                    for tr_id in c_data["teachers"]:
                        for t in teachers[tr_id]["teacher_available_times"]:
                            if solver.Value(X[(c_id, s, t, tr_id)]) == 1:
                                schedule.append({
                                    "time_idx": t,
                                    "time_str": get_time_str(t),
                                    "course": c_data["name"],
                                    "teacher": teachers[tr_id]["name"]
                                })
            
            schedule = sorted(schedule, key=lambda k: k["time_idx"])
            
            for item in schedule:
                cohort_has_class = True
                print(f"Time: {item['time_str']:<20} | Course: {item['course']:<20} | Teacher: {item['teacher']}")
                
            if not cohort_has_class:
                print("For this cohort there is no course.")
            print("-" * 40)
    else:
        print("No feasible schedule could be found. Constraints might be too tight.")


if __name__ == '__main__':
    # teachers = {
    #     "T1": {"name": "استاد کرمانیان", "teacher_available_times": [0, 1, 2, 4, 5, 8, 9, 10]},
    #     "T2": {"name": "استاد علوی", "teacher_available_times": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]},
    #     "T3": {"name": "استاد رضایی", "teacher_available_times": [12, 13, 14, 15, 16, 17, 18, 19]}
    # }


    # courses = {
    #     "C1": {"name": "ساختمان داده", "credits": 3, "cohort": "1403", "teachers": ["T1", "T2"]},
    #     "C2": {"name": "برنامه‌نویسی پیشرفته", "credits": 4, "cohort": "1404", "teachers": ["T2"]},
    #     "C3": {"name": "ریاضیات گسسته", "credits": 3, "cohort": "1404", "teachers": ["T1", "T3"]},
    #     "C4": {"name": "هوش مصنوعی", "credits": 2, "cohort": "1402", "teachers": ["T3"]},
    #     "C5": {"name": "هوش مصنوعی", "credits": 3, "cohort": "1402", "teachers": ["T1", "T2"]},
    #     "C6": {"name": "آزمایشگاه فیزیک", "credits": 1, "cohort": "1405", "teachers": ["T3"]}
    # }
    
    
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
        "C26_2":  {"name": "C26_Course_2", "cohort": "2026", "credits": 3, "teachers": ["T3"]},
        "C26_3":  {"name": "C26_Course_3", "cohort": "2026", "credits": 1, "teachers": ["T4"]},
        "C26_4":  {"name": "C26_Course_4", "cohort": "2026", "credits": 2, "teachers": ["T6"]},
        "C26_5":  {"name": "C26_Course_5", "cohort": "2026", "credits": 3, "teachers": ["T7"]},
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
    
    
    time_table_maker(teachers=teachers, courses=courses)