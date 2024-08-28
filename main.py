import csv
import pandas as pd
from urllib.request import urlopen
import os
import random

class SchoolAssessmentAnalyzer:
    def __init__(self, file_path, student_name):
        self.file_path = file_path
        self.student_name = student_name
        self.data = pd.DataFrame()
        self.compare_data = pd.DataFrame()
        self.summary={"name":"", "class":"", "semester":"", "courses":0,
                      "average":0, "A":0, "best_course":"", "worst_course":"",
                      "web_time_spent":'0', "improve_course":"", "percent":0.0,
                      "0bcourse":""}
        self.coure_list = ["Math",
                           "Physics",
                           "Chemistry",
                           "Biology",
                           "English",
                           "History",
                           "Geography",
                           "Literature",
                           "Philosophy",
                           "Art"]    
    def process_file(self):
        try:
            # Open and read the content of the file
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(self.file_path)
                if semesters == "semester2":
                    self.compare_data = pd.read_csv(f"semester1\\{class_room}.csv")
            elif file_path.endswith('.xlsx'):
                self.data = pd.read_excel(self.file_path)
            elif file_path.endswith('.txt'):
                self.data = pd.read_csv(self.file_path, delimiter='\t')
        except FileNotFoundError:
            print("Please Enter a valid class name")
            exit()

    def transfer_data(self, criteria, destination_file):
        split_criteria = criteria.split()
        try:
            if '<' in split_criteria:
                self.data = self.data[self.data['Average'] < int(split_criteria[1])]
            elif '>' in split_criteria:
                self.data = self.data[self.data['Average'] > int(split_criteria[1])]
            elif '=' in split_criteria:
                self.data = self.data[self.data['Average'] == int(split_criteria[1])]
            # Save the filtered data to a new file
            self.data.to_csv(destination_file, index=False)

        except Exception:
            print("Invalid criteria")

    def fetch_web_data(self, url):
        try:
            time_list =[]
            with urlopen(url) as response:
                time_spend = pd.read_csv(response)
                student_time = time_spend[time_spend['Name'] == self.student_name]
                for i in range(len(student_time)):
                    time_list.append(int(student_time["Time Spent"].values[i].replace("m", "")))
            time = sum(time_list)

            self.summary["web_time_spent"] =str(time) + " minutes"
        except Exception:
            self.summary['web_time_spent']= "Not accessible might be the link is broken."


    def analyze_content(self):
        try:
            if self.student_name in self.data['Name'].values:
                student_data = self.data[self.data['Name'] == self.student_name]
                if semesters == "semester2":
                    url="https://raw.githubusercontent.com/altradCS/CSB-Python-Fall2024-FileSystem/main/semester%201/web%20log.csv"
                    sd_compare = self.compare_data[self.compare_data['Name'] == self.student_name]
                else:
                    url="https://raw.githubusercontent.com/altradCS/CSB-Python-Fall2024-FileSystem/main/semester%202/web%20log.csv"
                self.summary['name'] = self.student_name
                self.summary['class'] = class_room
                self.summary['semester'] = semesters
                # chek if the student has taken all the courses
                for i in self.coure_list:
                    tem =str(student_data[i].values[0])
                    if tem.isdigit():
                        self.summary['courses'] += 1
                # calculate the average
                self.summary['average'] = student_data[self.coure_list].mean().mean()
                # calculate the number of A
                self.get_A(self.data)
                self.summary["best_course"] = student_data[self.coure_list].mean().idxmax()
                self.summary["worst_course"] = student_data[self.coure_list].mean().idxmin()
                if semesters == "semester2":
                    tem_improve={}
                    for i in self.coure_list:
                        if sd_compare[i].values[0] < student_data[i].values[0]:
                            tem_improve[i]= (student_data[i].values[0] - sd_compare[i].values[0])
                    if len(tem_improve) > 0:
                        improve_cs = random.choice(list(tem_improve.keys()))
                        self.summary["percent"] = (tem_improve[improve_cs]/sd_compare[improve_cs].values[0])*100
                        self.summary["improve_course"] = improve_cs + f": Improved by {self.summary['percent'].round(2)}% compared to the last semester"
                       
                        max_improve = max(tem_improve.values())
                        for i in tem_improve.keys():
                            if tem_improve[i] == max_improve:
                                self.summary["0bcourse"] = f"Semester 2 shows a significant improvement in {i}"
                    else:
                        self.summary["improve_course"] = "Student did do any better than the previous semester"
                        self.summary["0bcourse"] = "Semester 2 do not show any significant improvement at any course"           
                self.fetch_web_data(url)
            else:
                print(f"Student name {self.student_name} not found in the data")
                exit()
        except KeyError:
            print("Invalid file format")
            exit()

    def generate_summary(self):
        file_path = 'format.txt' if semesters in ['semester1', "Not known"] else 'format1.txt'
        if file_path == 'format.txt':
        
        # Create a dictionary with named placeholders
            summary_data = {
                'name': self.summary['name'],
                'class': self.summary['class'],
                'semester': self.summary['semester'],
                'courses': self.summary['courses'],
                'average': self.summary['average'],
                'A': self.summary['A'],
                'best_course': self.summary['best_course'],
                'worst_course': self.summary['worst_course'],
                "web_time_spent": self.summary["web_time_spent"],
                "time":pd.Timestamp.now().strftime('%Y-%m-%d')
            }
        elif file_path == 'format1.txt':
            
            summary_data = {
                'name': self.summary['name'],
                'class': self.summary['class'],
                'semester': self.summary['semester'],
                'courses': self.summary['courses'],
                'average': self.summary['average'],
                'A': self.summary['A'],
                'best_course': self.summary['best_course'],
                'worst_course': self.summary['worst_course'],
                "improve_course": self.summary["improve_course"],
                "obcourse": self.summary["0bcourse"],
                "web_time_spent": self.summary["web_time_spent"],
                "time":pd.Timestamp.now().strftime('%Y-%m-%d')
            }
        with open(file_path, 'r') as file:
                format_str = file.read()
        formatted_summary = format_str.format(**summary_data)
        print(formatted_summary)
        with open(f"{self.student_name}_{class_room}_{semesters}_summary.txt", 'w') as file:
            file.write(formatted_summary)


    def get_A(self,student_data):
        for i in self.coure_list:
            if student_data[i].values[0] > 90:
                self.summary['A'] += 1
if __name__ == "__main__":
    print("============================================================")
    print("=========== Welcome to School Assessment Analyzer ==========")
    print("============================================================")
    print("")
    print("Select an option to continue:")
    print("")
    print(" 1. Semester 1                        2. Semester 2   ")
    print("")
    print(" 3. Use a different file              4. Exit the program")
    print("============================================================")
    sem = input("")
    os.system('cls')
    if sem not in ["1", "2","3"] or sem == "4":
        if sem !="4":
            print("Invalid input")
        exit()
    if sem!="3":
        semesters = "semester1" if sem == "1" else "semester2"
        print("[10A, 10B, 10C, 10D, 10E, 10F, 10G, 10H]")
        print("")
        class_room = input("Enter class name: ").upper()
        file_path = f"{semesters}\\{class_room}.csv"
        print("")
    else:
        print(r"Example: path\to\file")
        print('')
        file_path = input("Enter file path: ")
        semesters ="Not known"
        class_room = "Not known"
        if '"' in file_path:
            file_path = file_path.replace('"', "")
    student_name = input("Enter student name: ").capitalize()
    print("")
    os.system('cls')

    sa =SchoolAssessmentAnalyzer(file_path, student_name)
    sa.process_file()
    sa.analyze_content()
    sa.generate_summary()
    print("============================================================")
    print("============= Summary generated successfully ===============")
    print("")
    t=input('Do you want to transfer data based on a criteria? (Y/n) ').lower()

    if t=='y':
        criteria = input("Enter criteria score (<,>,=):  ").replace(" ", "")
        destination_file = input("Enter destination file: ").replace(" ", "")
        sa.transfer_data(criteria, destination_file)
        print("Data transfer successful")
        print("Thank you for using School Assessment Analyzer")
        exit()
    elif t=='n':
        print("Thank you for using School Assessment Analyzer")
        exit()
    else:
        print("Invalid input: ")
        exit()