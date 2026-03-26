import os

content1 = ""
if os.path.exists("Cathay_Data_v1.2.md"):
    with open("Cathay_Data_v1.2.md", "r") as f:
        content1 = f.read()

content2 = ""
if os.path.exists("uber-hk-asia-miles-report.md"):
    with open("uber-hk-asia-miles-report.md", "r") as f:
        content2 = f.read()

combined = content1 + "\n\n---\n\n# ADDITIONAL RESEARCH: UBER & SPECIFIC VENDORS\n\n" + content2

with open("Cathay_Engine_Knowledge_Base.md", "w") as f:
    f.write(combined)
