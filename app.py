import os
import pdfplumber
from flask import Flask
import re
import pandas as pd

app = Flask(__name__)
folder_path = "payslips/"
data = {
    "january": [],
    "february": [],
    "march" : [],
    "april" : [],
    "may" : [],
    "june" : [],
    "july" : [],
    "august" : [],
    "september" : [],
    "october" : [],
    "november" : [],
    "december" : []
}
#basic patterns, weekly to extract "weekly" part from pdf
weekly_pattern_iris = r"Week No\..*?(?=Details To-Date)"
date_pattern_iris = r"(?i)(date|process date)\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})"
date_pattern_sage = r"(?i)[a-zA-Z\s]+(\d{2}-\d{2}-\d{4})"
a_months = ['january','february','march','april','may','june','july','august','september','october','november','december']
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".pdf"):
        #joins folder and filepath
        file_path = os.path.join(folder_path, filename)
        
        with pdfplumber.open(file_path) as pdf:
            text = pdf.pages[0].extract_text()
            
            #extract only weekly data
            weekly_text_match = re.search(weekly_pattern_iris, text, re.DOTALL)
            
            if weekly_text_match:
                weekly_text = weekly_text_match.group()
            else:
                weekly_text = text 
                
            #Patterns to store data into variables
            #gross taxable
            gross_match = re.search(r"(?i)Gross\s+Taxable\s+(\d+\.\d{2})", weekly_text)
            gross_taxable = float(gross_match.group(1)) if gross_match else None
            #total payments
            total_payments_match = re.search(r"(?i)Total\s+Payments\s+(\d+\.\d{2})", weekly_text)
            total_payments = float(total_payments_match.group(1)) if total_payments_match else None
            #total deductions
            total_deductions_match = re.search(r"(?i)Total\s+Deductions\s+(\d+\.\d{2})", weekly_text)
            total_deductions = float(total_deductions_match.group(1)) if total_deductions_match else None
            #tax
            tax_match = re.search(r"(?i)PAYE\s+Tax\s+(\d+\.\d{2})", weekly_text)
            tax = float(tax_match.group(1)) if tax_match else None
            #NIC (insurance)
            nic_match = re.search(r"(?i)NIC\s+(\d+\.\d{2})", weekly_text)
            nic = float(nic_match.group(1)) if nic_match else None
            #pension "pru"
            pension_match = re.search(r"(?i)(Pru\s+AE\s+EEs|Pension)\s+(\d+\.\d{2})", weekly_text)
            pension = float(pension_match.group(2)) if pension_match else None
            #net pay
            net_match = re.search(r"(?i)Net\s+Pay\s+(\d+\.\d{2})", weekly_text)
            net = float(net_match.group(1)) if net_match else None
            
            #check for date pattern
            date_matches_iris = re.findall(date_pattern_iris, weekly_text)
            date_matches_sage = re.findall(date_pattern_sage, weekly_text)
            
            if date_matches_iris:
                label, date_str = date_matches_iris[0]
                month_num = int(date_str.split('/')[1])
                month_name = a_months[ month_num - 1]
                if not any(entry['filename'] == filename for entry in data[month_name]):
                    data[month_name].append({
                        "filename": filename,
                        "date" : date_str,
                        "total payments" : total_payments,
                        "gross taxable" : gross_taxable,
                        "tax" : tax,
                        "NIC" : nic,
                        "pension": pension,
                        "total deductions" : total_deductions,
                        "NET" : net
        
                        })
            elif date_matches_sage:
                date_str = date_matches_sage[0]
                month_num = int(date_str.split('-')[1])
                month_name = a_months[month_num - 1]
                
                #need to use different patterns for Sage payslip formating
                total_payments_match = re.search(r"(?i)Total\s+Gross\s+Pay\s*(\d+\.\d{2})", weekly_text)
                total_payments = float(total_payments_match.group(1)) if total_payments_match else None
                    
                gross_match = re.search(r"(?i)Gross\s+for\s+Tax\s+(\d+\.\d{2})", weekly_text)
                gross_taxable = float(gross_match.group(1)) if gross_match else None
                    
                tax_match = re.search(r"PAYE Tax\s*(\d+\.\d{2})|Tax Paid\s*(\d+\.\d{2})", weekly_text) 
                tax = float(tax_match.group(1)) if tax_match else None
                    
                pension_match = re.search(r"Pension\s*(\d+\.\d{2})", weekly_text)
                pension = float(pension_match.group(1)) if pension_match else None
                    
                nic_match = re.search(r"National Insurance\s*(\d+\.\d{2})", weekly_text)
                nic = float(nic_match.group(1)) if nic_match else None
                    
                net_match = re.search(r"Employer\s+APC\s+TD\s+\d+\.\d{2}\s*(\d+\.\d{2})", weekly_text)
                net = float(net_match.group(1)) if net_match else None
                    
                                       
                    
                data[month_name].append({
                    "filename": filename,
                    "date" : date_str,
                    "total payments" : total_payments,
                    "gross taxable" : gross_taxable,
                    "tax" : tax,
                    "NIC": nic,
                    "pension" : pension,
                    "total deductions": sum([nic or 0, pension or 0, tax or 0]),
                    "NET" : net
                })
            else:
                print(f"The app works with Iris or Sage payslips")

#function to calculate monthly values 
def calculate_annually(magic):
    annual_total = {
        "total payments" : 0.0,
        "gross taxable" : 0.0,
        "tax" : 0.0,
        "NIC" : 0.0,
        "pension": 0.0,
        "total deductions" : 0.0,
        "NET": 0.0
    }
    for month_data in magic.values():
        for key in annual_total:
            value = month_data.get(key)
            if value is not None and isinstance(value, (int,float)): 
                annual_total[key] += value
    return annual_total

def calculate_month(data):
    monthly_totals = {}
    
    for month, payslips in data.items():
        totals = {
            "total payments" : 0.0,
            "gross taxable" : 0.0,
            "tax" : 0.0,
            "NIC" : 0.0,
            "pension" : 0.0,
            "total deductions": 0.0,
            "NET" : 0.0
        }
        for slip in payslips:
            for key in totals:
                value = slip.get(key)#get value for "totals".key from payslips(data.items.values)
                if value is not None:
                    if isinstance(value, (int, float)):
                        totals[key] += value
                    else:
                        print(f"Invalid value type for {key} in {month}")
        monthly_totals[month] = totals
    return monthly_totals


magic = calculate_month(data)
yearly = calculate_annually(magic)


#fill the annuall into txt
with open("annually.txt", "w") as file:
    file.write("Annualy:\n")
    for i, j in yearly.items():
        file.write(f"{i.title():<20} {j:>12.2f}\n")

#fill the monthly into txt  
with open("monthly.txt", "w") as file1:
    for i, j in magic.items():
        file1.write(f"\n{i.title()}\n")
        for key, total in j.items():
            file1.write(f"{key.title():<20} {total:>11.2f}\n")   

#formating data for excel import
#montly,first column "month" 
monthly_df = pd.DataFrame.from_dict(magic, orient="index")
monthly_df.index.name = "Month"
monthly_df.reset_index(inplace=True)
monthly_df["Month"] = monthly_df["Month"].str.title()


#yearly
yearly_df = pd.DataFrame(list(yearly.items()), columns=["Category", "Amount"])

#import into excel, leave some space between monthly-yearly
with pd.ExcelWriter("output_in_excel.xlsx", engine="openpyxl") as writer:
    monthly_df.to_excel(writer, index=False, startrow=0)
    yearly_df.to_excel(writer, index=False, startrow=17)