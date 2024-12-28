from main import extract_text_from_audio, sanitise_text_with_llm, git_add_and_push_file


def test_whisper_flow():
    text, err = extract_text_from_audio("my_voice_candale.m4a")
    assert err is None
    assert "Salut" in text


def test_llm():
    text, err = sanitise_text_with_llm(
        "Salut, prietenul meu Candale! \n Sunt pe drum pe Bucuresti!"
    )
    assert err is None
    assert "Salut" in text
