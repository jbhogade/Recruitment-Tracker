# ==========================================================================
# File : tracker/dummy_data.py
# What : FAKE candidate records used while there is no database.
#        Fields follow the HR team's current Excel sheet:
#        Sr. No., Candidate Name, Education, Department, Position,
#        Fresher / Experienced, Contact No., Date of Interview,
#        Interview Status, Interviewer Name, Reference/Source,
#        Month & Year, Remark, Final Status, Expected CTC
# Note  : this file now only creates the FIRST set of demo data (see
#         tracker/data_store.py). After that, the pages read data/candidates.json.
# Later : SQL Server replaces data_store.py. Keep the dictionary keys below
#         unchanged so the pages keep working.
# ==========================================================================

#-------------- Start Code for Imports and allowed values -----------------
from datetime import date, timedelta

# Allowed values (also used to build dropdowns on the future Add/Edit form).
INTERVIEW_STATUSES = ["Scheduled", "Rescheduled", "Completed", "No Show"]
FINAL_STATUSES = ["Pending", "On Hold", "Selected", "Joined", "Rejected"]

INTERVIEWERS = [
    "Rahul Deshmukh", "Sneha Kulkarni", "Amit Patil", "Priya Joshi", "Vikas Shinde",
]

# Fake employee names used for demo candidates whose source is "Employee Referral".
REFERRERS = ["Anil Pawar", "Kiran Jagdale", "Sunita More", "Rajesh Thakur"]
#-------------- End of the code ------------------------------


#-------------- Start Code for Raw dummy rows (edit / add rows here) -----------------
# Column order of each tuple:
#  (name, education, department, position, fresher_or_experienced,
#   days_from_today, interview_status, source, remark, final_status,
#   expected_ctc_in_lakh_per_annum)
# "days_from_today": -10 = interview was 10 days ago, 3 = interview in 3 days.
# Using relative days keeps "Upcoming interviews" meaningful whenever you run it.
_RAW_ROWS = [
    ("Aarav Kulkarni",   "B.E. (Computer)",  "IT",         "Software Developer",        "Experienced", -148, "Completed",   "Naukri",            "Strong in Python and SQL",        "Joined",   6.5),
    ("Sneha Patil",      "B.Com",            "Accounts",   "Accountant",                "Experienced", -140, "Completed",   "Employee Referral", "Good knowledge of GST",           "Joined",   3.8),
    ("Rohan Jadhav",     "B.B.A",            "Sales",      "Sales Executive",           "Fresher",     -133, "Completed",   "Walk-in",           "Communication needs work",        "Rejected", 2.4),
    ("Pooja Shinde",     "MBA (HR)",         "HR",         "Recruiter",                 "Fresher",     -126, "Completed",   "Campus",            "Confident and quick learner",     "Joined",   2.2),
    ("Vikram Deshpande", "Diploma (Mech.)",  "Production", "Production Supervisor",     "Experienced", -119, "Completed",   "Consultancy",       "10 years on shop floor",          "Joined",   4.5),
    ("Neha Gaikwad",     "MBA (Marketing)",  "Marketing",  "Digital Marketing Executive","Experienced", -112, "Completed",   "LinkedIn",          "Salary expectation too high",     "Rejected", 4.2),
    ("Aditya More",      "B.Sc (IT)",        "IT",         "System Administrator",      "Experienced", -105, "Completed",   "Naukri",            "Handled Windows Server and AD",   "Joined",   5.2),
    ("Kavita Pawar",     "B.A",              "Admin",      "Receptionist",              "Fresher",     -98,  "No Show",     "Walk-in",           "Did not attend",                  "Rejected", 1.8),
    ("Sandeep Chavan",   "B.Com",            "Operations", "Operations Executive",      "Experienced", -91,  "Completed",   "Employee Referral", "Good with MIS reports",           "Joined",   3.5),
    ("Anjali Bhosale",   "B.Com",            "Accounts",   "Accounts Executive",        "Fresher",     -84,  "Completed",   "Campus",            "Weak in Tally",                   "Rejected", 2.0),
    ("Mayur Salunkhe",   "B.E. (E&TC)",      "IT",         "Network Engineer",          "Experienced", -77,  "Completed",   "Indeed",            "Waiting for budget approval",     "On Hold",  4.8),
    ("Swati Kamble",     "MBA (Sales)",      "Sales",      "Area Sales Manager",        "Experienced", -70,  "Completed",   "LinkedIn",          "Handled 3 districts earlier",     "Joined",   7.2),
    ("Nikhil Gaikwad",   "ITI (Fitter)",     "Production", "Quality Inspector",         "Fresher",     -63,  "Completed",   "Consultancy",       "Willing to work in shifts",       "Joined",   2.1),
    ("Rutuja Mane",      "B.A",              "Admin",      "Office Coordinator",        "Experienced", -56,  "Completed",   "Naukri",            "Not a good fit for the role",     "Rejected", 3.0),
    ("Harshad Thorat",   "B.E. (Computer)",  "IT",         "Software Developer",        "Fresher",     -49,  "Completed",   "Campus",            "Joining after notice period",     "Selected", 3.0),
    ("Prachi Wagh",      "MBA (HR)",         "HR",         "HR Executive",              "Experienced", -42,  "Completed",   "Employee Referral", "Good knowledge of labour law",    "Joined",   3.9),
    ("Tushar Sawant",    "B.Com",            "Sales",      "Sales Executive",           "Experienced", -38,  "Completed",   "Walk-in",           "Decision pending with manager",   "On Hold",  3.2),
    ("Ritika Dange",     "B.B.A",            "Marketing",  "Digital Marketing Executive","Fresher",     -35,  "Completed",   "Indeed",            "Portfolio not strong",            "Rejected", 2.5),
    ("Omkar Phadtare",   "B.Com",            "Operations", "Store Keeper",              "Experienced", -31,  "Completed",   "Consultancy",       "Documents verification pending",  "Selected", 3.0),
    ("Shruti Jagtap",    "M.Com",            "Accounts",   "Accountant",                "Experienced", -28,  "Completed",   "Naukri",            "Strong in Tally Prime",           "Selected", 4.0),
    ("Yash Mhatre",      "Diploma (Mech.)",  "Production", "Production Supervisor",     "Experienced", -24,  "Completed",   "Employee Referral", "Shift flexibility issue",         "Rejected", 4.0),
    ("Divya Nair",       "B.Sc (IT)",        "IT",         "System Administrator",      "Fresher",     -21,  "Completed",   "LinkedIn",          "Keep as backup candidate",        "On Hold",  3.4),
    ("Kunal Bagal",      "MBA (Sales)",      "Sales",      "Area Sales Manager",        "Experienced", -17,  "No Show",     "Naukri",            "Did not attend",                  "Rejected", 6.8),
    ("Madhuri Lokhande", "MBA (HR)",         "HR",         "Recruiter",                 "Experienced", -14,  "Completed",   "Walk-in",           "Good sourcing skills",            "Selected", 3.6),
    ("Siddharth Rane",   "B.E. (Computer)",  "IT",         "Software Developer",        "Experienced", -10,  "Completed",   "Naukri",            "Second round pending",            "Pending",  7.0),
    ("Gauri Kadam",      "B.A",              "Admin",      "Receptionist",              "Fresher",     -7,   "Completed",   "Walk-in",           "Feedback awaited",                "Pending",  1.9),
    ("Akash Ingle",      "B.Com",            "Operations", "Operations Executive",      "Fresher",     -4,   "Completed",   "Campus",            "Feedback awaited",                "Pending",  2.4),
    ("Bhakti Ghadge",    "B.Com",            "Accounts",   "Accounts Executive",        "Experienced", -2,   "Completed",   "Indeed",            "Feedback awaited",                "Pending",  3.3),
    ("Tejas Kolhe",      "B.E. (E&TC)",      "IT",         "Network Engineer",          "Experienced", 1,    "Scheduled",   "LinkedIn",          "",                                "Pending",  5.0),
    ("Varsha Dhumal",    "MBA (Marketing)",  "Marketing",  "Digital Marketing Executive","Experienced", 2,    "Scheduled",   "Naukri",            "",                                "Pending",  4.0),
    ("Rahul Sutar",      "ITI (Fitter)",     "Production", "Quality Inspector",         "Fresher",     3,    "Rescheduled", "Consultancy",       "Asked to move by one day",        "Pending",  2.2),
    ("Mansi Tambe",      "MBA (HR)",         "HR",         "HR Executive",              "Fresher",     5,    "Scheduled",   "Campus",            "",                                "Pending",  2.3),
    ("Pranav Gore",      "B.B.A",            "Sales",      "Sales Executive",           "Experienced", 6,    "Scheduled",   "Employee Referral", "",                                "Pending",  3.8),
    ("Komal Yadav",      "B.A",              "Admin",      "Office Coordinator",        "Experienced", 9,    "Scheduled",   "Walk-in",           "",                                "Pending",  2.8),
]
#-------------- End of the code ------------------------------


#-------------- Start Code for Function that builds full records -----------------
def get_candidates(today=None):
    """Return the dummy candidates as a list of dictionaries (one per Excel row).

    The keys match the HR Excel columns, converted to simple names:
      sr_no, name, education, department, position, experience, contact,
      interview_date, interview_status, interviewer, source, referred_by, month_year,
      remark, final_status, expected_ctc
    """
    today = today or date.today()
    candidates = []
    referral_count = 0                       # used to hand out the demo referrer names in turn
    for index, row in enumerate(_RAW_ROWS, start=1):
        (name, education, department, position, experience,
         day_offset, interview_status, source, remark, final_status, ctc) = row
        interview_date = today + timedelta(days=day_offset)
        referred_by = ""
        if source == "Employee Referral":
            referred_by = REFERRERS[referral_count % len(REFERRERS)]
            referral_count += 1
        candidates.append({
            "sr_no": index,
            "name": name,
            "education": education,
            "department": department,
            "position": position,
            "experience": experience,                       # Fresher / Experienced
            "contact": f"90000 {index:05d}",                # fake phone number
            "interview_date": interview_date,
            "interview_status": interview_status,
            "interviewer": INTERVIEWERS[index % len(INTERVIEWERS)],
            "source": source,
            "referred_by": referred_by,                     # employee who referred (Employee Referral only)
            "month_year": interview_date.strftime("%b %Y"), # e.g. "Oct 2026"
            "remark": remark,
            "final_status": final_status,
            "expected_ctc": ctc,                            # in lakh per annum
        })
    return candidates
#-------------- End of the code ------------------------------
