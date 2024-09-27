import re
import csv
import pandas as pd

#file_path = 'C:\\Users\\A\\Documents\\SEMA\\data'
#df = pd.read_csv(file_path, delimiter='\t')

splits = {'validation': 'data/validation-00000-of-00001.parquet', 'test': 'data/test-00000-of-00001.parquet'}
df = pd.read_parquet("hf://datasets/jhu-clsp/jfleg/" + splits["validation"])

correct_sentences_list = df['corrections'].tolist()

usable_sentences = []
corrections = list()
corrections_0 = list()
corrections_1 = list()
corrections_2 = list()
corrections_3 = list()
item_count = 0
for i, sentence in enumerate(df['sentence']):
    if len(sentence.split()) > 11:
        if item_count < 100:
            usable_sentences.append([sentence])
            for j, correction in enumerate(correct_sentences_list[i].tolist()):
                 match j:
                    case 0:
                        corrections_0.append([correction])
                    case 1:
                        corrections_1.append([correction])
                    case 2:
                        corrections_2.append([correction])
                    case 3:
                        corrections_3.append([correction])
            item_count += 1
        else:
            break
corrections.append(corrections_0)
corrections.append(corrections_1)
corrections.append(corrections_2)
corrections.append(corrections_3)
with open("D:\\" + "jfleg_sentences.csv", 'w', newline='') as output_file:
    writer = csv.writer(output_file)
    writer.writerows(usable_sentences)

for i, correction in enumerate(corrections):
    with open("D:\\" + "jfleg_reference" + str(i) + ".csv", 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerows(correction)