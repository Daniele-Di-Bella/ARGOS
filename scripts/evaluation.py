import argparse
import csv
import os

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams, LLMTestCase
from API_keys import TDarkRAG_API_key, LANGCHAIN_TRACING_V2, LANGCHAIN_ENDPOINT, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT

# Set API keys as environment variables
os.environ["OPENAI_API_KEY"] = TDarkRAG_API_key
os.environ["LANGCHAIN_TRACING_V2"] = LANGCHAIN_TRACING_V2
os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT


# GEval metric
def calculate_geval_correctness(question: str, to_be_evaluated: str, reference_text: str, keyword: str, csv_YN: bool):
    with open(to_be_evaluated, 'r', encoding='utf-8') as file:
        actual_output = file.read().split("## References")[0].strip()
        # file.read() reads the entire content of the file as a single string.
        # split("References") splits the content into a list of strings, separating the text at the first occurrence of "References".
        # [0] takes the part before the "References" section.
        # strip() removes any leading and trailing whitespace from the text.

    with open(reference_text, 'r', encoding='utf-8') as file:
        expected_output = file.read()

    test_case = LLMTestCase(
        input=question,
        actual_output=actual_output,
        expected_output=expected_output
    )

    correctness_metric_4o = GEval(
        name="Correctness",
        criteria="The expected output is the real Wikipedia page on a given topic, while the actual output is a "
                 "potential Wikipedia page on the same topic: Your goal is to determine "
                 "whether the actual output is a good Wikipedia page based on the expected output. You should put "
                 "particular attention on the accuracy of the facts and data cited in the actual output with respect"
                 "to the ones cited in the expected output.",
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        model="gpt-4o"
    )

    correctness_metric_4o_mini = GEval(
        name="Correctness",
        criteria="The expected output is the real Wikipedia page on a given topic, while the actual output is a "
                 "potential Wikipedia page on the same topic: Your goal is to determine "
                 "whether the actual output is a good Wikipedia page based on the expected output. You should put "
                 "particular attention on the accuracy of the facts and data cited in the actual output with respect"
                 "to the ones cited in the expected output.",
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        model="gpt-4o-mini"
    )

    correctness_metric_4o.measure(test_case)
    correctness_metric_4o_mini.measure(test_case)

    with open(to_be_evaluated, 'r', encoding='utf-8') as file:
        original_content = file.read()

    with open(f"{to_be_evaluated.removesuffix('.md')}[Eval].md", "w", encoding='utf-8') as file:
        file.write(original_content)
        file.write(f"# Evaluation\n"
                   f"GEval 4o correctness score: {correctness_metric_4o.score}<br>"
                   f"Reason: {correctness_metric_4o.reason}\n\n"
                   f"GEval 4o-mini correctness score: {correctness_metric_4o_mini.score}<br>"
                   f"Reason: {correctness_metric_4o_mini.reason}\n\n")

    # Report the GEval score also in a .csv that will be used for statistical analysis
    if csv_YN:
        with open("evaluation.csv", 'a+', newline='', encoding='utf-8') as file:
            # Move the cursor to the beginning to read any existing content
            file.seek(0)
            reader = csv.reader(file)
            rows = list(reader)  # Read existing rows (if any)

            # Check if the file is empty, and if necessary, write the header
            if not rows:
                writer = csv.writer(file)
                writer.writerow(["Topic", "GEval 4o score", "GEval 4o-mini score"])

            # Add new rows
            writer = csv.writer(file)
            writer.writerow([keyword, correctness_metric_4o.score, correctness_metric_4o_mini.score])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Estimate the quality of the generated text through GEval metric.")
    parser.add_argument("--question", required=True, help="Question that the RAG system has to answer")
    parser.add_argument("--to_be_evaluated", required=True, help="Path to the generated file")
    parser.add_argument("--reference_text", required=True, help="Path to the reference file")
    parser.add_argument("--keyword", required=True, help="Entry for the CSV row in which the score will be stored."
                                                         "It's the same keyword that was used to retrieve the sources for the RAG")
    parser.add_argument("--csv_YN", required=True, help="The scores will be stored in a csv? Y/N")

    args = parser.parse_args()

    calculate_geval_correctness(args.question, args.to_be_evaluated, args.reference_text, args.keyword, args.csv_YN)
