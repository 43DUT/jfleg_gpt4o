import pandas as pd
import re
import csv
from openai import OpenAI

client = OpenAI()

splits = {'validation': 'data/validation-00000-of-00001.parquet', 'test': 'data/test-00000-of-00001.parquet'}
df = pd.read_parquet("hf://datasets/jhu-clsp/jfleg/" + splits["validation"])

correct_sentences_list = df['corrections'].tolist()
usable_sentences = []
correct_sentences = []
temperatures = [0.1, 0.5, 0.9]
prompts = [
    "Reply with a corrected version of the input sentence with all grammatical and spelling errors fixed. If there are no errors, reply with a copy of the original sentence. \n\n Input sentence: {x} \n Corrected sentence: ",
    "Fix the errors in this sentence: \n\n {x}",
    "Correct the following to standard English: \n\n Sentence: {x} \n Correction:",
    "Correct this to standard English: \n\n {x}", "Original sentence: {x} \n Corrected sentence:",
    "Act as an editor and fix the issues with this text: \n\n {x}", "Correct this to standard English: \n\n \"{x}\"",
    "Improve the grammar of this text: \n\n {x}", "Update to fix all grammatical and spelling errors: \n\n {x}",
    "Make this sound more fluent: \n\n {x}"]

data_collection = []


def api_request(temp, sentence):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": sentence},
        ],
        temperature=temp
    )
    return response.choices[0].message.content


def addEntryToCSV(result, sentence, api_response, api_response_formatted, corrections):
    entry = {
        "result": result,
        "sentence": sentence,
        "response": api_response,
        "response_formatted": api_response_formatted,
        "corrections": corrections
    }
    data_collection.append(entry)


def checkSolution(sentences, solutions):
    for sentence in sentences:
        for solution in solutions:
            if sentence == solution.strip():
                return "true"
    return "false"


def parseSentence(sentence):
    # Leerzeichen vor Satzzeichen hinzufügen
    formatted_sentence = re.sub(r'([?.!,:;])', r' \1 ', sentence)
    # Entfernen von doppelten Leerzeichen (falls welche entstehen)
    formatted_sentence = re.sub(r'\s+', ' ', formatted_sentence).strip()
    # print("api response: " + formatted_sentence)

    sentences = []
    sentences.append(formatted_sentence.strip())
    if ":" in formatted_sentence:
        sentences.append(formatted_sentence.split(" : ")[1].strip().replace("\"", ""))
        sentences.append(formatted_sentence.split(" : ")[1].split(" . ")[0] + " .".replace("\"", ""))
    if "\"" in formatted_sentence:
        sentences.append(re.findall('"([^"]*)"', formatted_sentence)[0].strip().replace("\"", ""))
        sentences.append(re.findall('"([^"]*)"', formatted_sentence)[0].strip().replace("\"", "").split(" .")[0] + " .")
    return sentences


item_count = 0

for i, sentence in enumerate(df['sentence'].tolist()):
    if len(sentence.split()) > 11:
        if item_count < 100:
            usable_sentences.append(sentence)
            correct_sentences.append(correct_sentences_list[i].tolist())
            item_count += 1
        else:
            break

# loop requests
for temperature in temperatures:
    for i, prompt in enumerate(prompts):
        for j, sentence in enumerate(usable_sentences):
            parsedSentences = parseSentence(api_request(temperature, prompt.replace("{x}", sentence)))
            result = checkSolution(parsedSentences, correct_sentences[j])
            addEntryToCSV(result, usable_sentences[j], parsedSentences[0], parsedSentences[1:], correct_sentences[j])

        keys = data_collection[0].keys()
        with open("D:\\" + str(temperature) + "gec_jfleg" + str(i) + ".csv", 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys, delimiter=';')
            dict_writer.writeheader()
            dict_writer.writerows(data_collection)

        data_collection = []