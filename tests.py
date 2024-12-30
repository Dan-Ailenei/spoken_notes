from main import extract_text_from_audio, sanitise_text_with_llm, git_add_and_push_file
from prompts import get_prompt1, get_prompt2


def test_whisper_flow():
    text, err = extract_text_from_audio("my_voice_candale.m4a")
    assert err is None
    assert "Salut" in text


def test_llm():
    sanitised1, err = sanitise_text_with_llm(
        get_prompt1(
            "I wake up to the sound of my alarm, groggily reaching for my phone to check the time and scroll through notifications. After a quick shower and breakfast—usually something simple like toast or cereal—I head off to work, spending most of my day tackling tasks, attending meetings, or responding to emails. During lunch, I either eat something packed or grab a quick bite at a nearby spot. After work, I unwind by watching a show, catching up with friends, or hitting the gym. The day ends with some quiet time—reading or scrolling through my phone—before finally drifting off to sleep."
        )
    )
    assert err is None

    _, err = sanitise_text_with_llm(get_prompt2(sanitised1))
    assert err is None


def test_whisper_with_llm():
    whisper_text, err = extract_text_from_audio(
        "./static_files/Recording 20241229145916.m4a"
    )
    assert err is None

    _, err = sanitise_text_with_llm(whisper_text)
    assert err is None


test_llm()
