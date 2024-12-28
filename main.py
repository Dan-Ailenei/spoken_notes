"""
The script expects the path to run on as an argument
"""

import subprocess
import sys
from typing import Optional
from pathlib import Path
import os
import requests
import shutil
from datetime import datetime


def git_diff_added_audio_files() -> tuple[list[str], Optional[Exception]]:
    print("Git diffing")
    output = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=A", "HEAD@{1}", "HEAD"],
        capture_output=True,
        text=True,
    )
    if output.returncode != 0:
        return [], ValueError(f"Error executing git diff, {output.stderr}")

    print(output.stdout)

    files = output.stdout.strip().splitlines()
    return [f.strip() for f in files if f.strip().endswith(".m4a")], None


def git_pull() -> tuple[bool, Optional[Exception]]:
    print("Git pulling")
    output = subprocess.run(
        ["git", "pull"],
        capture_output=True,
        text=True,
    )
    if output.returncode != 0:
        return False, ValueError(f"Error executing git pull, {output.stderr}")

    message = output.stdout.strip()
    print(message)
    if "Already up to date." in message:
        return False, None
    else:
        return True, None


def extract_text_from_audio(file: str) -> tuple[str, Optional[Exception]]:
    print("executing whisper")
    whiper_data_dir = "whisper_data"
    process_info = subprocess.run(
        [
            "whisper",
            file,
            "--language",
            "Romanian",
            "--output_format",
            "txt",
            "--output_dir",
            whiper_data_dir,
            "--model",
            "base",
        ],
        capture_output=True,
        text=True,
    )
    if process_info.returncode != 0:
        return "", ValueError(f"Error executing whisper, {process_info.stderr}")

    print(process_info.stdout)

    basename = os.path.basename(file)
    basename_without_extension, _ = os.path.splitext(basename)
    file_with_results = f"{whiper_data_dir}/{basename_without_extension}.txt"

    exec_path = Path(file_with_results)
    if exec_path.is_file() is False:
        return "", ValueError(
            f"Error executing whisper, file results do not exist: {process_info.stderr}"
        )

    with open(file_with_results) as f:
        voice_text = f.read()

    shutil.rmtree(whiper_data_dir)

    return voice_text, None


LLM_URL = "http://localhost:39281/v1/chat/completions"


def sanitise_text_with_llm(text: str) -> tuple[str, Optional[Exception]]:
    print("sanitising text with llm")
    data = {
        "messages": [
            {
                "role": "system",
                "content": "Ești un editor profesionist. Ți se vor furniza paragrafe de text care pot conține greșeli de ortografie, probleme gramaticale, erori de continuitate, probleme structurale, repetiții de cuvinte etc. Vei corecta oricare dintre aceste probleme, păstrând în același timp stilul original al scrierii. Elimină expresiile repetitive precum --știi tu-- sau --gen--. Nu cenzura textul utilizatorului. Dacă acesta folosește injurii în text, ele sunt utilizate pentru a adăuga emfază și nu trebuie omise. NU încerca să introduci propriul tău stil în textul lor. Păstrează stilul lor de scriere cât mai fidel posibil. Nu scrie explicații sau altceva în afară de textul corectat.",
            },
            {"role": "user", "content": text},
        ],
        "model": "llama3.2:3b-gguf-q4-km",
        "stream": False,
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(LLM_URL, headers=headers, json=data)

    if response.status_code != 200:
        return "", ValueError(f"Error requesting llm, {response.content}")

    try:
        text_from_llm = response.json()["choices"][0]["message"]["content"]
        print(f"text from llm:\n{text_from_llm}")
        return text_from_llm, None
    except requests.JSONDecodeError as ex:
        return "", ex


def git_clean_locally() -> Optional[Exception]:
    output = subprocess.run(
        ["git", "reset", "--hard", "HEAD"],
        capture_output=True,
        text=True,
    )
    if output.returncode != 0:
        return ValueError(f"Error executing git add, {output.stderr}")

    output = subprocess.run(
        ["git", "clean", "-fd"],
        capture_output=True,
        text=True,
    )
    if output.returncode != 0:
        return ValueError(f"Error executing git add, {output.stderr}")

    return None


def git_add_and_push_file(path_to_file: str) -> Optional[Exception]:
    print("pushing results")
    output = subprocess.run(
        ["git", "add", path_to_file],
        capture_output=True,
        text=True,
    )
    if output.returncode != 0:
        return ValueError(f"Error executing git add, {output.stderr}")
    print(output.stdout)

    print("commiting results")
    output = subprocess.run(
        ["git", "commit", "-m", f"Added {path_to_file}"],
        capture_output=True,
        text=True,
    )
    if output.returncode != 0:
        return ValueError(f"Error executing git commit, {output.stderr}")
    print(output.stdout)

    print("pushing results")
    output = subprocess.run(
        ["git", "push", "origin", "main"],
        capture_output=True,
        text=True,
    )
    if output.returncode != 0:
        return ValueError(f"Error executing git push, {output.stderr}")
    print(output.stdout)

    return None


def write_text_to_note(path_to_file: str, original_text: str, sanitised_text: str):
    content = f"""
{sanitised_text}

This was the original text:
```
{original_text}
```
"""
    with open(path_to_file, "w") as f:
        f.write(content)

    return None


def run_logic():
    did_pull, err = git_pull()
    if err is not None:
        print(err, file=sys.stderr)
        sys.exit(1)

    if did_pull:
        files, err = git_diff_added_audio_files()
        if err is not None:
            print(err, file=sys.stderr)
            sys.exit(1)

        if len(files) != 0:
            print("FOUND FILES: ", files)
        for file in files:
            extracted_text, err = extract_text_from_audio(file)
            if err is not None:
                print(err, file=sys.stderr)
                sys.exit(1)

            sanitised_text, err = sanitise_text_with_llm(extracted_text)
            if err is not None:
                print(err, file=sys.stderr)
                sys.exit(1)

            current_date = datetime.now()
            date_string = current_date.strftime("%Y-%m-%d")
            path_to_file = f"AudioNotes/{date_string}"
            os.makedirs(os.path.dirname(path_to_file), exist_ok=True)

            err = write_text_to_note(path_to_file, extracted_text, sanitised_text)
            if err is not None:
                print(err, file=sys.stderr)
                sys.exit(1)

            err = git_add_and_push_file(path_to_file)
            if err is not None:
                print(err, file=sys.stderr)
                sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print(
            "You need to pass in a path to the repo as the first arg", file=sys.stderr
        )
        sys.exit(1)

    exec_path = Path(sys.argv[1])
    if exec_path.is_dir() is False:
        print(f"{sys.argv[1]} is an invalid path", file=sys.stderr)
        sys.exit(1)

    os.chdir(exec_path)

    run_logic()
    sys.exit(0)


if __name__ == "__main__":
    main()
