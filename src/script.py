import re
import requests
import json
import argparse
from bs4 import BeautifulSoup
import os
import shutil

base_url = "https://leetcode.com/graphql"

problem_details_query = """
query getProblem($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    title
    content
    difficulty
  }
}
"""

code_snippets_query = """
query questionHints($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        title
        codeSnippets {
            lang
            langSlug
            code
        }
    }
}
"""

parser = argparse.ArgumentParser()

parser.add_argument(
    "--titleSlug",
    required=True,
    help="Slug of the problem title"
)

args = parser.parse_args()

variables = {
    "titleSlug": args.titleSlug
}

headers = {
    "Content-Type": "application/json"
}

# ------------------------------
# IMPORTANT PATH FIX
# ------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

testcase_dir = os.path.join(
    BASE_DIR,
    "testcases"
)

os.makedirs(testcase_dir, exist_ok=True)

# ------------------------------
# CLEAN OLD TESTCASES
# ------------------------------

try:
    for file in os.listdir(testcase_dir):

        file_path = os.path.join(
            testcase_dir,
            file
        )

        if os.path.isfile(file_path):
            os.remove(file_path)

except Exception:
    pass


def save_code_snippets_to_files(
    output,
    testcase_dir
):

    if "codeSnippets" not in output:
        raise KeyError(
            "The key 'codeSnippets' is missing."
        )

    for lang, code in output["codeSnippets"].items():

        if lang == "C++":

            boilerplate = """
#include <bits/stdc++.h>
using namespace std;

typedef long long ll;

void solve() {

}

int main() {
    solve();
    return 0;
}
"""

            code = boilerplate.strip()

        elif lang == "Python3":

            code = """
def solve():
    pass


if __name__ == "__main__":
    solve()
"""

        if lang == "Python3":

            snippet_file_path = os.path.join(
                testcase_dir,
                "python3.py"
            )

        elif lang == "C++":

            snippet_file_path = os.path.join(
                testcase_dir,
                "c++.cpp"
            )

        else:
            continue

        with open(
            snippet_file_path,
            "w",
            encoding="utf-8"
        ) as snippet_file:

            snippet_file.write(code)


def fetch_data(query, variables):

    response = requests.post(
        base_url,
        json={
            "query": query,
            "variables": variables
        },
        headers=headers
    )

    if response.status_code == 200:
        return response.json()

    raise Exception(
        f"Error: HTTP {response.status_code}, {response.text}"
    )


def extract_data_structure(code, lang):

    data_structure = {}

    if lang == 'C++':

        pattern = r'\((.*?)\)'

        match = re.search(pattern, code)

        if match:

            params = match.group(1)

            variables = params.split(',')

            for var in variables:

                var = var.strip()

                if var:

                    type_and_name = var.split()

                    if len(type_and_name) >= 2:

                        var_type = type_and_name[0]
                        var_name = type_and_name[1]

                        data_structure[var_name] = var_type

    elif lang == 'Python3':

        pattern = r'\((.*?)\)'

        match = re.search(pattern, code)

        if match:

            params = match.group(1)

            variables = params.split(',')

            for var in variables:

                var = var.strip()

                if var and "self" not in var:

                    type_and_name = var.split(":")

                    if len(type_and_name) == 2:

                        var_name = type_and_name[0].strip()
                        var_type = type_and_name[1].strip()

                        data_structure[var_name] = var_type

    return data_structure


problem_data = fetch_data(
    problem_details_query,
    variables
)

code_snippet_data = fetch_data(
    code_snippets_query,
    variables
)

output = {}

question = (
    problem_data
    .get("data", {})
    .get("question", {})
)

if question:

    question_id = question.get("questionId")

    title = question.get("title")

    content_html = question.get("content", "")

    difficulty = question.get("difficulty")

    soup = BeautifulSoup(
        content_html,
        "html.parser"
    )

    examples = {}

    description_parts = []

    example_counter = 1

    for example_tag in soup.find_all("pre"):

        example_text = example_tag.get_text()

        if "Explanation:" in example_text:

            example_text = (
                example_text
                .split("Explanation:", 1)[0]
                .strip()
            )

        examples[
            f"Example {example_counter}"
        ] = example_text

        example_counter += 1

    for element in soup.find_all(
        ["p", "strong"],
        recursive=False
    ):

        description_parts.append(
            element.get_text(strip=True)
        )

    description_clean = " ".join(description_parts)

    code_snippets = {}

    snippet_question = (
        code_snippet_data
        .get("data", {})
        .get("question", {})
    )

    data_structures = {}

    if snippet_question:

        for snippet in snippet_question.get(
            "codeSnippets",
            []
        ):

            lang = snippet.get("lang")

            code = snippet.get("code")

            code_snippets[lang] = code

            if lang in ["C++", "Python3"]:

                data_structures[lang] = (
                    extract_data_structure(
                        code,
                        lang
                    )
                )

    input_counter = 1

    for example_key, example_text in examples.items():

        parts = example_text.split("Output:", 1)

        if len(parts) == 2:

            input_text = (
                parts[0]
                .replace("Input:", "")
                .strip()
            )

            input_lines = input_text.split(", ")

            formatted_input = []

            vector_size = 0

            for line in input_lines:

                line = line.replace('"', '')

                if "[" in line and "]" in line:

                    line = line.split("=")[1].strip()

                    line = (
                        line
                        .replace("[", "")
                        .replace("]", "")
                    )

                    line = line.replace(",", " ")

                    vector_size = len(line.split())

                else:

                    line = line.split("=")[1].strip()

                formatted_input.append(line.strip())

            formatted_input.insert(
                0,
                str(vector_size)
            )

            input_text = "\n".join(formatted_input)

            output_text = (
                parts[1]
                .strip()
                .split("Explanation:", 1)[0]
                .strip()
            )

            output_text = output_text.replace('"', '')

            if "[" in output_text and "]" in output_text:

                output_text = (
                    output_text
                    .replace("[", "")
                    .replace("]", "")
                    .replace(",", " ")
                    .strip()
                )

            input_file = os.path.join(
                testcase_dir,
                f"input_{input_counter}.txt"
            )

            output_file = os.path.join(
                testcase_dir,
                f"output_{input_counter}.txt"
            )

            with open(
                input_file,
                "w",
                encoding="utf-8"
            ) as infile:

                infile.write(input_text)

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as outfile:

                outfile.write(output_text)

            input_counter += 1

    question_file = os.path.join(
        testcase_dir,
        "question.txt"
    )

    with open(
        question_file,
        "w",
        encoding="utf-8"
    ) as qf:

        qf.write(description_clean)

    output = {
        "id": question_id,
        "title": title,
        "description": description_clean.strip(),
        "difficulty": difficulty,
        "examples": examples,
        "codeSnippets": code_snippets,
        "dataStructures": data_structures,
    }

    save_code_snippets_to_files(
        output,
        testcase_dir
    )

else:

    output = {
        "error": "No question data found."
    }

print(json.dumps(output, indent=2))