from itertools import groupby

import pandas as pd
import json
import torch
from farm.evaluation.metrics import squad_EM, squad_f1
from farm.infer import QAInferencer
from farm.modeling.predictions import QACandidate

from model_pipeline.config_qa_farm_train import (
    QAModelConfig,
    QATrainingConfig,
    QAFileConfig,
    QATokenizerConfig,
    QAProcessorConfig,
    QAInferConfig,
)
from model_pipeline.utils.qa_metrics import relaxed_squad_f1


def read_squad_file(filename):
    """Read a SQuAD json file"""
    with open(filename, "r", encoding="utf-8") as reader:
        input_data = json.load(reader)["data"]
    return input_data


def split_into_pos_neg(all_dicts):
    _all_pos_dicts = []
    _all_neg_dicts = []
    for _dict in all_dicts:
        pos_dict = {"context": _dict["context"]}
        neg_dict = {"context": _dict["context"]}
        pos_qas = []
        neg_qas = []
        for q in _dict["qas"]:
            if q["is_impossible"]:
                neg_qas.append(q)
            else:
                pos_qas.append(q)
        if len(pos_qas) > 0:
            pos_dict["qas"] = pos_qas
            _all_pos_dicts.append(pos_dict)
        if len(neg_qas) > 0:
            neg_dict["qas"] = neg_qas
            _all_neg_dicts.append(neg_dict)
    return _all_pos_dicts, _all_neg_dicts


def single_result_to_qa_candidate(single_result):
    answer = single_result["predictions"][0]["answers"][0]
    qa_candidate = QACandidate(
        offset_answer_start=answer["offset_answer_start_token"],
        offset_answer_end=answer["offset_answer_end_token"],
        score=answer["score"],
        answer_type="span",
        offset_unit="token",
        aggregation_level="doc",
    )
    return [[qa_candidate]]


def single_result_to_label(single_result):
    _ground_truth = single_result["predictions"][0]["ground_truth"][0]
    start_idx = _ground_truth["offset_answer_start_token"]
    end_idx = _ground_truth["offset_answer_end_token"]
    return [(start_idx, end_idx)]


def keyfunc(x):
    q = x['predictions'][0]['question'].split(" in year")[0]
    if not q.endswith("?"):
        q = q + "?"
    return q


file_config = QAFileConfig()
train_config = QATrainingConfig()
model_config = QAModelConfig()
processor_config = QAProcessorConfig()
tokenizer_config = QATokenizerConfig()
infer_config = QAInferConfig()

model_path = file_config.saved_models_dir
model = QAInferencer.load(
    model_path, batch_size=infer_config.batch_size, gpu=torch.cuda.is_available()
)

dev_file_path = file_config.dev_filename
nested_dicts = read_squad_file(filename=dev_file_path)
dicts = [y for x in nested_dicts for y in x["paragraphs"]]
# Separating pos and neg to report individual metrics
all_pos_dicts, all_neg_dicts = split_into_pos_neg(dicts)

# Positive Examples
all_results = []
fail_counter = 0

# Running inference one paragraph at a time and finding the start and end tokens for both ground truth and predictions
# This is done one by one since there is no way to retrieve the paragraph text once inference is done
for i, single_dict in enumerate(all_pos_dicts):
    context = single_dict["context"]
    try:
        results = model.inference_from_dicts(dicts=[single_dict])
    except Exception as e:
        print(e)
        fail_counter += 1
        continue
    for res in results:

        # Converting the ground truth character indices to token indices
        ground_truth = res["predictions"][0]["ground_truth"]
        gt_start_char_idx = ground_truth[0]["offset"]
        gt_start_token_idx = len(context[0:gt_start_char_idx].split())
        gt_end_token_idx = gt_start_token_idx + len(ground_truth[0]["text"].split())
        ground_truth[0]["offset_answer_start_token"] = gt_start_token_idx
        ground_truth[0]["offset_answer_end_token"] = gt_end_token_idx

        # Converting the predictions character indices to token indices
        answers = res["predictions"][0]["answers"]
        for ans in answers:
            start_char_idx = ans["offset_answer_start"]
            end_char_idx = ans["offset_answer_end"]
            ans["offset_answer_start_token"] = len(context[0:start_char_idx].split())
            ans["offset_answer_end_token"] = ans["offset_answer_start_token"] + len(
                context[start_char_idx:end_char_idx].split()
            )
        all_results.append(res)

print("Failed to get inference results for {} paragraphs".format(fail_counter))

results_per_question = []
unique_questions = []
for k, g in groupby(sorted(all_results, key=keyfunc), keyfunc):
    results_per_question.append(list(g))  # Store group iterator as a list
    unique_questions.append(k)

print("*********************")
print("Results for Positive Examples:")
positive_summary = []
for kpi, results in zip(unique_questions, results_per_question):
    preds = [single_result_to_qa_candidate(res) for res in results]
    labels = [single_result_to_label(res) for res in results]
    em = squad_EM(preds, labels)
    f1 = squad_f1(preds, labels)
    relaxed_f1 = relaxed_squad_f1(preds, labels)
    print("KPI:", kpi)
    print("\tSupport:", len(results))
    print("\tEM:", em)
    print("\tF1:", f1)
    print("\tRelaxed F1:", relaxed_f1)
    positive_summary.append(
        {
            "KPI": kpi,
            "Support": len(results),
            "EM": em,
            "F1": f1,
            "Relaxed F1": relaxed_f1,
        }
    )
df_positive_summary = pd.DataFrame(positive_summary)
df_positive_summary.to_csv("positive_summary.csv")

# Negative Examples
all_negative_predictions = model.inference_from_dicts(dicts=all_neg_dicts)
results_per_question = []
unique_questions = []
for k, g in groupby(sorted(all_negative_predictions, key=keyfunc), keyfunc):
    results_per_question.append(list(g))  # Store group iterator as a list
    unique_questions.append(k)

negative_summary = []
for kpi, results in zip(unique_questions, results_per_question):
    n_all_neg = len(results)
    n_cor_pred = 0
    for neg_pred in results:
        if neg_pred["predictions"][0]["answers"][0]["answer"] == "no_answer":
            n_cor_pred += 1
    accuracy = 100 * n_cor_pred / n_all_neg
    print("KPI:", kpi)
    print("\tSupport:", n_all_neg)
    print("\tAccuracy:", accuracy)
    negative_summary.append({"KPI": kpi, "Support": n_all_neg, "Accuracy": accuracy})
df_negative_summary = pd.DataFrame(negative_summary)
df_negative_summary.to_csv("negative_summary.csv")
