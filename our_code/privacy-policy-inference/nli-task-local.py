from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

import sys
import datetime
import os, re, csv, time
import spacy
import pandas as pd
nlp = spacy.load('en_core_web_sm')
import requests
from os import walk


def nli_scope(premise, hypothesis, max_length=500):
    if premise[-1] != ".":
        premise += '.'

    tokenized_input_seq_pair = tokenizer.encode_plus(premise, hypothesis,
                                                     max_length=max_length,
                                                     return_token_type_ids=True, truncation=True)

    input_ids = torch.Tensor(tokenized_input_seq_pair['input_ids']).long().unsqueeze(0)
    # remember bart doesn't have 'token_type_ids', remove the line below if you are using bart.
    token_type_ids = torch.Tensor(tokenized_input_seq_pair['token_type_ids']).long().unsqueeze(0)
    attention_mask = torch.Tensor(tokenized_input_seq_pair['attention_mask']).long().unsqueeze(0)

    outputs = model(input_ids,
                    attention_mask=attention_mask,
                    token_type_ids=token_type_ids,
                    labels=None)
    # Note:
    # "id2label": {
    #     "0": "entailment",
    #     "1": "neutral",
    #     "2": "contradiction"
    # },

    predicted_probability = torch.softmax(outputs[0], dim=1)[0].tolist()  # batch_size only one

    # For debugging purposes
    print("Premise:", premise, "\nHypothesis:", hypothesis, "\nEntailment:", 
        predicted_probability[0], "\nNeutral:", predicted_probability[1],
        "\nContradiction:", predicted_probability[2])

    return predicted_probability



def nli_scope_multiple_attempt(premise,hypothesis,tries = 3):
    predicted_probability = None
    for i in range(tries):
        try:
            predicted_probability = nli_scope(premise,hypothesis)
            if (predicted_probability is None) and (i < tries - 1): # i is zero indexed
                time.sleep(3)
                continue
        except:
            print("  >> ERROR OCCURRED")
            pass
        if (predicted_probability is None) and (i < tries - 1): # i is zero indexed
            time.sleep(3)
            continue
        break
    return predicted_probability


def read_hypothese(filename='sentiments.csv'):
    hypotheses = dict()
    with open(filename) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        next(csv_reader, None) # Skip the header row
        count_data_type = 0
        for row in csv_reader:
            if len(row) == 5:
                count_data_type += 1
                data_type_key = str(count_data_type) + " " + row[0].strip() 
                action_phrase = row[1].strip() 
                sentiment_yes = row[2].replace("@", action_phrase).strip()  
                sentiment_irr = row[3].replace("@", action_phrase).strip()
                sentiment_no = row[4].replace("@", action_phrase).strip() 
                hypotheses[data_type_key] = [sentiment_yes, sentiment_irr, sentiment_no]
        print("Hypotheses for", count_data_type, "data types have been read.")
    return hypotheses


def analyze_document(hypotheses, pp_filename='sample_pp.txt', threshold=0.5):
    summary_data_collected = []

    with open(pp_filename, 'r', encoding='utf-8') as f:
        doc_content = f.read()
        f.close()

    pp_doc = nlp(doc_content)

    with open("log.md", "a+", encoding='utf-8') as log:
        print(pp_filename + ", " + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
        log.write("\n" + pp_filename + ", " + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") + "\n")

        for index, sent in enumerate(pp_doc.sents):
            #rint(" >>> So far this doc has collected: ",summary_data_collected)

            clean_sentence = re.sub('\s+', ' ', str(sent))
            clean_sentence_print = clean_sentence

            if len(clean_sentence) > 50:
                clean_sentence_print = clean_sentence[:50] + "..."

            # Exclude a sentense less than 5 words
            if len(clean_sentence.split(" ")) <= 5:
                print(str(index) + " " + clean_sentence_print + " -> Skipped due to too short sentence.")
                continue
            
            # Exclude a sentense without key verbs 
            skip = True

            if len(key_verbs) == 0: # Full mode (all sentences to be analyzed)
                skip = False
            else: # Demo mode (only sentences with a candidate verb will be analyzed)
                for verb in key_verbs:
                    if verb in clean_sentence:
                        skip = False
                        break
            if skip: 
                print(str(index) + " " + clean_sentence_print + " -> Skipped due to no key verb found in it.")
                continue

            log.write(str(index) + " " + clean_sentence_print + ", ")     
            print(str(index) + " " + clean_sentence_print, end=" ")

            # Now test our heypothesese
            for key in hypotheses:
                sentiments = hypotheses[key]
                entailment_score_list = []

                # Iterate three sentiments (yes, irrelevant, no) and query the NLI model
                for hypo in sentiments:
                    predicted_probability = nli_scope_multiple_attempt(clean_sentence, hypo)
                    #print(predicted_probability)
                    if predicted_probability is None:
                        print("Skipped due to None received.")
                        continue
                    entailment_score = predicted_probability[0] # We only choose the entailment score
                    entailment_score_list.append("{:.2f}".format(entailment_score))

                # We only consider collection behavior if and only if the YES score is greater than IRRELEVANT and NO at the same time.
                # Also, since the score is the prediction probability, we only consider the score greater than the pre-defined threshold value.
                if float(entailment_score_list[0]) > float(entailment_score_list[1]) and \
                    float(entailment_score_list[0]) > float(entailment_score_list[2]) and \
                        float(entailment_score_list[0]) > threshold:
                    #print("  >> [" + key + "] YES -", entailment_score_list[0], ", IRRELEVANT -", entailment_score_list[1], ", NO -", entailment_score_list[2])
                    print("(" + str(key) + " " + u'\u2713' + ")", end=" ")
                    log.write(key + ", " + str(entailment_score_list[0]) + ", " + str(entailment_score_list[1]) + ", " + str(entailment_score_list[2]) + ", ")
                    if not key in summary_data_collected:
                        summary_data_collected.append(key)
                #else:
                #    print("(" + str(key) + " " + u'\u2717' + ")", end=" ")
            log.write("\n")
            print("")  
        summary_data_collected.sort()
        log.write(str(summary_data_collected))
        #log.write("\n")  
        
        log.close()
        print(" >>> In the end this doc has collected: ",summary_data_collected)
    return summary_data_collected

if __name__ == '__main__':

    # We create a key_verb for a demo purpose. If this list is not empty, our privacy policy inference 
    #  will only process sentences from a privacy policy that contains at least one verb included. For
    #  those sentences do not containt those verbs, we will skip it. This can speed up the inference.
    # If you want to fully process the privacy policy, just leave the list empty. 
    key_verbs=['access', 'collect', 'need', 'provide', 'read', 'require', 'request', 'share', 'upload']

    # Initialize the model    
    hg_model_hub_name = "ynie/roberta-large-snli_mnli_fever_anli_R1_R2_R3-nli"

    tokenizer = AutoTokenizer.from_pretrained(hg_model_hub_name)
    model = AutoModelForSequenceClassification.from_pretrained(hg_model_hub_name)

    # Read all sentiments corresponding to their data types
    hypotheses = read_hypothese('sentiments.csv')

    # privacy policies are uploaded in a dedicated directory
    # please make sure you have replace the "path_pps" with the acutal path where all privacy policies are located in  
    path_pps = "privacy_policy" 
    pp_filenames = []

    dir_list = os.listdir(path_pps)
    for file in dir_list:
        if file.endswith(".txt"):
            pp_filenames.append(os.path.join(path_pps, file))

    num_pps = len(pp_filenames)
    print(str(num_pps) + " privacy policies found.")

    for index, filepath in enumerate(pp_filenames):
        print("Analysis progress: " + str(index + 1) + "/" + str(num_pps) + "..." )
        data_collected = analyze_document(hypotheses, filepath)
        print(data_collected)

