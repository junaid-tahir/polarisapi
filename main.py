from flask import Flask, request, render_template, request
import cv2
import pytesseract
from PyPDF2 import PdfReader
import openai
from itertools import zip_longest

app = Flask(__name__)
openai.api_key='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'


def gpt3(stext):
    response=openai.Completion.create(
        engine="davinci-instruct-beta",
        prompt=stext,
        max_tokens=1000,
        top_p=1,    
        frequency_penalty=0,
        presence_penalty=0
        )
    
    content=response.choices[0].text.split('.')
    #print(content)
    return response.choices[0].text



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.form.files['image']
        # Save the uploaded file to a temporary location
        file.save('temp.jpg')

        # Load the image
        img = cv2.imread('temp.jpg')

        # ...

        # OCR the image
        text = pytesseract.image_to_string(img)

        clauses = text.split("\n\n")
        list1 = []
        count = 1
        for i in range(len(clauses)):
            if len(clauses[i]) > 100:
                list1.append(str(count) + " " + clauses[i])
                count = count + 1

        Finaltext = ['Please Classify the following legal clause as either "Risky", "Partially Risky", "Safe": \n\n']
        list1 = [item.replace('\n', '') for item in list1]
        list2 = []
        for i in range(len(list1)):
            list2.append(list1[i] + "\n\n")

        risky_notrisky = ['RISKY', 'PARTIALLY RISKY', 'SAFE']

        FINAL_RESULT = []

        for i in range(len(list2)):
            Finaltext.append(list2[i])
            text2 = ''.join(Finaltext)
            while True:
                response = openai.Completion.create(
                    engine="davinci-instruct-beta",
                    prompt=text2,
                    max_tokens=1000,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                Text3 = response.choices[0].text.upper()
                if 'PARTIALLY RISKY' in Text3:
                    FINAL_RESULT.append('PARTIALLY RISKY')
                    break
                elif 'RISKY' in Text3:
                    FINAL_RESULT.append('RISKY')
                    break
                elif 'SAFE' in Text3:
                    FINAL_RESULT.append('SAFE')
                    break
            


            Finaltext.pop()

        Finaltext.append(text)
        text2 = ''.join(Finaltext)
        print(text2)
        while True:
                response = openai.Completion.create(
                    engine="davinci-instruct-beta",
                    prompt=text2,
                    max_tokens=1000,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                summary_output = response.choices[0].text.upper()
                if 'PARTIALLY RISKY' in summary_output:
                    Summary_Analyse='PARTIALLY RISKY'
                    break
                elif 'RISKY' in summary_output:
                    Summary_Analyse='RISKY'
                    break
                elif 'SAFE' in summary_output:
                    Summary_Analyse='SAFE'
                    break

        Sum_Tex=['Find the summary of the paragraph in 250 words :']
        Sum_Tex.append(text)
        Summary_Text = ''.join(Sum_Tex)

        while(True):    
            response = openai.Completion.create(
                        engine="davinci-instruct-beta",
                        prompt=Summary_Text,
                        max_tokens=1000,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0
                    )
            Summary_Text1 = response.choices[0].text.upper()
            if(len(Summary_Text1)>250):
                break

        return render_template('index.html', clauses=list2, result=FINAL_RESULT, S_O=summary_output, S_A=Summary_Analyse,Summary_Text1=Summary_Text1, zip=zip_longest)


    return render_template('index.html')


def gpt3(stext):
    response=openai.Completion.create(
        engine="davinci-instruct-beta",
        prompt=stext,
        max_tokens=1000,
        top_p=1,    
        frequency_penalty=0,
        presence_penalty=0
        )
    
    content=response.choices[0].text.split('.')
    #print(content)
    return response.choices[0].text

@app.route("/pdf", methods=["GET", "POST"])
def check():
    if request.method == "POST":
        file = request.files["pdf_file"]
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
            if(len(text)>2000):
                break

        sumarize='Sumarize it'
        summarizing_pdf=gpt3(sumarize+text)

        Finaltext=['Please Classify the following legal clause as either "Risky", "Partially Risky", "Safe": \n\n']
        Finaltext = ' '.join([str(elem) for elem in Finaltext])

        while(True):
            Text3=gpt3(Finaltext+summarizing_pdf)
            Text4=Text3.upper()
            if 'PARTIALLY RISKY' in Text4:
                Text3='PARTIALLY RISKY'
                break
            elif 'RISKY' in Text4:
                Text3='RISKY'
                break
            elif 'SAFE' in Text4:
                Text3='SAFE'
                break

        return render_template("index.html", summarizing_pdf=summarizing_pdf, Text3=Text3)

    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)



