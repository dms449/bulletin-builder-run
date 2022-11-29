from flask import Flask, request, make_response
import os
import subprocess
import logging
import datetime
from  pathlib import Path
from flask import make_response
from google.cloud import error_reporting
client = error_reporting.Client()

PROJECT_DIR = os.getcwd()
FILE_PATH = 'generated/this_weeks_bulletin.tex'

def latex_safe(s, chars=["\\", '&', '$']):
    s = str(s)
    for c in chars:
        s = s.replace(c, "\\"+c)
    return s

def get_benediction(benediction_str):
    benediction = latex_safe(benediction_str)
    benediction_split = benediction.rfind('.')
    if benediction_split == -1:
        logging.warning("No period found in benediction")
    else:
        benediction_split += 1
        benediction = benediction[:benediction_split] + "\\\ \\hfill{" + benediction[benediction_split:] +"}"
    return benediction

def get_creed(creed_str):
    if (creed_str.lower() not in ["nicene", "apostles"]): raise Exception(f"creed `{creed_str}` is not recognized")
    return creed_str

def build_pdf():
    """

    """
    os.chdir(Path(FILE_PATH).parent)
    logging.debug(f"cwd = {os.getcwd()}")

    # NOTE: run the process twice (I dont' know why but sometimes the spacing
    #       is messed up until the second time it is run)
    filename = Path(FILE_PATH).name
    subprocess.run(["../bin/pdflatex", filename])
    if subprocess.run(["../bin/pdflatex", filename]).returncode != 0:
        raise Exception("Failed to generate pdf from latex file 1")
    os.chdir(PROJECT_DIR)

def build_latex_file(data):
    """

    """
    sunday = datetime.date.fromisoformat(data['date'])

    if sunday.weekday() != 6:
        raise Exception(f"Date provided ({sunday}) is not a sunday")

    # setup temporary files
    os.makedirs(Path(FILE_PATH).parent.resolve(), exist_ok=True)
    f = open(FILE_PATH,"w+")
    f.write("\\input{../templates/ordo_header_wide} \n")

    # variables
    print(data['benediction'])
    benediction = get_benediction(data['benediction'])
    print(benediction)
    creed = get_creed(data['creed'])
    new_members = latex_safe(data['newMembers'])
    baptisms = latex_safe(data['baptisms'])

    # add the hymn variables
    # for hymn in data['hymns']:
    #     logging.info(hymn['hymn_string'])
    #     f.write(f"\\newcommand{{\\hymn{hymn['hymn_role']}}}{{{latex_safe(hymn['hymn_string'])}}} \n")

    f.write("\\newcommand{\\coverdate}{" + latex_safe(sunday.strftime("%B %d, %Y")) +  "} \n")
    f.write("\\newcommand{\\scriptureCalltoWorship}{" + latex_safe(data['scripture']) +  "} \n")
    f.write("\\newcommand{\\confession}{" + latex_safe(data['confessionVerse']) +  "} \n")
    f.write("\\newcommand{\\creedPath}{" + f"../templates/{creed}_creed.tex" + "} \n")
    f.write("\\newcommand{\\assurance}{" + latex_safe(data['assuranceVerse']) +  "} \n")
    f.write("\\newcommand{\\OTreading}{" + latex_safe(data['oldTestamentReading']) +  "} \n")
    f.write("\\newcommand{\\NTreading}{" + latex_safe(data['newTestamentReading']) +  "} \n")
    f.write("\\newcommand{\\preacher}{" + latex_safe(data['preacher']) +  "} \n")
    f.write("\\newcommand{\\benediction}{" + benediction +  "} \n")
    f.write("\\newcommand{\\thecollect}{" + latex_safe(data['collect']) +  "} \n")

    # get the first half of the ordo as a string
    # ____________________Body1_______________________
    ordo_body1_str = ""
    with open("templates/ordo_body1.tex","r") as f1:
        ordo_body1_str = f1.read()
    f.write(ordo_body1_str)

    # ____________________New Members_______________________
    if new_members.strip() != '-':
        logging.info(f"New Members present")
        f.write(f"\n\nAdmission of New Members: {latex_safe(new_members)}")
        f.write("\\vspace{3mm}")

    # ____________________Baptisms_______________________
    if baptisms.strip() != '-':
        logging.info(f"Baptisms present")
        f.write(f"\n\nHousehold Baptisms: {latex_safe(baptisms)}"+"""
    \\begin{leftbar}
        \\vspace{-0.8em}
        Little child, for you Jesus Christ came to this earth,\\
        struggled and suffered; for your sake He crossed Gethsemane\\
        and went through the darkness of Calvary;\\
        for your sake He cried: ``It is finished''; for your sake He died\\
        and for your sake He overcame death; indeed for your sake,\\
        little child, and you---still---know nothing of it.\\
        And thus the word of the apostle is confirmed: ``We love God,\\
        for He loved us first.''
    \end{leftbar}""")

    # get the second half of the ordo
    # ______________________Body2_____________________
    ordo_body2_str = ""
    with open("templates/ordo_body2.tex","r") as f2:
        ordo_body2_str = f2.read()
    f.write(ordo_body2_str)

    f.close()

    logging.info(f"Saved Bulletin to {FILE_PATH}")

app = Flask(__name__)
@app.route("/", methods=['POST'])
def build_bulletin():
    try:
        data = request.get_json()

        build_latex_file(data)
        build_pdf()

        pdf_filepath = FILE_PATH.split('.')[0] + '.pdf'

        response = make_response()
        response.headers.set('Content-Disposition', 'attachment', filename=pdf_filepath)
        response.headers.set('Content-Type', 'application/pdf')
        return response
    except Exception as e:
        client.report_exception()
        print(e)
    finally:
        os.chdir(PROJECT_DIR)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
