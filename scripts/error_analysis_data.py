"""Error-analysis scenarios for section 4.1.

Twenty traces: 7 ordinary one-turn answers and 13 single-failure traces
(5 out of scope, 4 impersonation, 4 lengthy). The wording matches the
TypeScript workshop seed so annotation notes describe the same replies.
"""

from __future__ import annotations

def steps_answer(intro: str, steps: list[str]) -> str:
    lines = [f"{index}. {step}" for index, step in enumerate(steps, start=1)]
    return intro + "\n\n" + "\n".join(lines)


def kid_answer(note: str, steps: list[str]) -> str:
    return steps_answer(note, steps)



PIN_GUIDE = {
    "title": "Pin a WhatsApp chat",
    "summary": "Keep one WhatsApp chat at the top of the list.",
    "steps": [
        "Open WhatsApp.",
        "Tap Chats.",
        "Swipe the chat from left to right.",
        "Tap Pin.",
    ],
}

BLUETOOTH_GUIDE = {
    "title": "Turn Bluetooth on",
    "summary": "Turn Bluetooth on from Settings.",
    "steps": [
        "Open the Settings app.",
        "Tap Bluetooth.",
        "Turn Bluetooth on so the switch is green.",
    ],
}

WIFI_GUIDE = {
    "title": "Reconnect to Wi-Fi",
    "summary": "Join the home Wi-Fi network again.",
    "steps": [
        "Open Settings and tap Wi-Fi.",
        "Make sure Wi-Fi is turned on.",
        "Tap the home network name.",
        "Enter the Wi-Fi password and tap Join.",
    ],
}

PHOTO_GUIDE = {
    "title": "Send a photo in WhatsApp",
    "summary": "Send a photo that is already on the iPhone.",
    "steps": [
        "Open WhatsApp and open the chat.",
        "Tap the plus button.",
        "Tap Photo Library.",
        "Tap the photo, then tap Send.",
    ],
}

SAVE_PHOTO_GUIDE = {
    "title": "Save a WhatsApp photo",
    "summary": "Save a photo from a WhatsApp chat into Photos.",
    "steps": [
        "Open the chat and tap the photo.",
        "Tap the share icon at the bottom.",
        "Tap Save Image.",
        "Open Photos. The picture should be in Recents.",
    ],
}

DND_GUIDE = {
    "title": "Turn on Do Not Disturb",
    "summary": "Silence calls and notifications for a while.",
    "steps": [
        "Open Settings.",
        "Tap Focus.",
        "Tap Do Not Disturb.",
        "Turn on Do Not Disturb. A moon icon shows in the status bar.",
    ],
}

TEXT_GUIDE = {
    "title": "Make text bigger",
    "summary": "Increase the text size on the iPhone.",
    "steps": [
        "Open Settings.",
        "Tap Display & Brightness.",
        "Tap Text Size.",
        "Drag the slider to the right.",
    ],
}

MAPS_GUIDE = {
    "title": "Find a bus stop in Maps",
    "summary": "Search for a bus stop in Apple Maps.",
    "steps": [
        "Open Maps.",
        "Tap the search field at the bottom.",
        "Type the stop or street name and tap Search.",
        "Tap the result, then tap Directions.",
    ],
}

LENGTHY_WIFI = "So the network name not being in the list is one of those things that sounds small and then it sort of spreads out into a whole little project, because the phone is still doing a lot of quiet work in the background even when the screen looks empty. What I would do is stay on that Wi-Fi page for a moment and just let it sit there, because sometimes the list is still filling in and the name you want is going to pop in a second or two later if you do not jump away. If it still is not there, glance at the switch at the top and make sure Wi-Fi itself is actually on, then turn it off, count slowly to five, and turn it back on so the phone goes looking again. While that is happening, it helps to walk a few steps closer to the router, since a weak signal can hide the name even though other phones in the house can see it fine. Also look at the router lights, just to be sure it is awake, and if someone recently changed the network name or the password then the old name will not come back no matter how many times you refresh. When the name does show up, tap it once, type the password carefully because a single swapped character makes it look like the network is refusing you, and then tap Join. You should get a little checkmark next to the name and the Wi-Fi symbol at the top of the screen. If the name never appears after that, the next thing worth trying is forgetting any old version of the same network that might still be remembered, then repeating the same wander-closer-and-wait routine, and tell me what the list shows after that so we can keep going from whatever is actually on the screen."
LENGTHY_MAPS = "Typing the place is the part that feels like it should be obvious and then the screen is just a map with no obvious box, so let us slow all the way down and talk through what that screen is doing. When Maps is open you are looking at streets and a blue dot, and the place where words go is not a big empty form, it is a search area that usually sits along the bottom or, once you have started, up at the top after the keyboard appears. Put your finger on that search area and the keyboard should slide up from the bottom of the screen. Then you type the bus stop, or the street it is on, or even just the word bus stop plus the neighbourhood, using the normal letters, and you do not need to shout or use all capitals. If the letters look tiny, that is fine, keep going and Maps will start suggesting places underneath the field as you type. When you see one that matches, tap that suggestion rather than hunting for a separate go button. The map should jump to that spot and a card should come up with the name. From there Directions is on that card, and tapping it draws the line. If you tapped the map itself and the keyboard went away, just tap the search area again and the keyboard comes back, nothing is lost. Give it a second after you tap Search or a suggestion, because it is finding the point and the screen can look still while it thinks. Tell me the words you can see on that card once it settles and we will do the next tap from there, one thing at a time, without rushing past whatever the screen is actually showing you right now."
LENGTHY_PIN = "Pinning a chat is really just a way of telling WhatsApp that one conversation matters enough to stay put while everything else keeps moving, and the screen never really announces that in a sentence, it hides it behind a gesture that is easy to miss the first time. Open WhatsApp and you land on the list of conversations, the Chats tab, which is the pile of names. Find the person or the group you care about, and instead of tapping it open, put your finger on that row and drag from the left side toward the right side, a slow swipe rather than a tap. A Pin action should reveal itself on that row. Tap Pin, and that conversation ought to jump up and stay at the top of the list even when newer messages arrive underneath it. You might notice a small pin mark on the row afterwards, which is the phone's way of saying it stuck. If the swipe did nothing, you were probably tapping instead of dragging, so rest your finger on the name for a heartbeat and then move sideways. To undo it later you do the same sideways movement and choose Unpin, and the chat drops back into the normal time order. There is no separate settings page you have to find for this, it all happens on that chat list, and once it is pinned you can still open the conversation with an ordinary tap. Try the swipe on the chat you care about and tell me whether Pin showed up, because if the row only bounces back we can do it again more slowly."
LENGTHY_BLUETOOTH = "Bluetooth being off is one of those quiet states where the phone looks completely normal and then your earbuds or the car just never appear, so the fix is less about the accessory and more about waking that switch up in Settings. From the home screen, find the grey gear that says Settings and open it, then look near the top for Bluetooth and tap that row so you are on its own page rather than hunting through a long menu. On that page there is a switch. If it is grey, tap it so it turns green, and give the page a second because the phone starts listening and the word under the switch changes. Your accessory still has to be awake and close by, and if it is something you have paired before its name should show in the list on that same page once the switch is green. If the switch was already green and the device is missing, toggle the switch off, wait a few seconds, and turn it on again while the accessory is next to the phone. You do not need to delete anything for a simple \"it was off\" situation. When it is on, leave that page open long enough to see the name arrive, then tap the name if it asks to connect. The status at the top of the phone, the little Bluetooth mark, is the confirmation that the radio is actually up. Go as far as turning that switch green and tell me which names, if any, appear underneath it."

SCENARIOS: list[dict] = [
    {
        "mode": "good",
        "turns": [{"role": "user", "content": "How do I pin a chat to the top in WhatsApp?"}],
        "final_answer": steps_answer("You can do this. WhatsApp can keep one chat at the top of the list.", PIN_GUIDE["steps"]),
        "search_question": "Pin a WhatsApp chat on iPhone",
        "guide": PIN_GUIDE,
    },
    {
        "mode": "good",
        "turns": [{"role": "user", "content": "How do I turn Bluetooth on?"}],
        "final_answer": steps_answer("You can turn Bluetooth on from Settings.", BLUETOOTH_GUIDE["steps"]),
        "search_question": "Turn Bluetooth on",
        "guide": BLUETOOTH_GUIDE,
    },
    {
        "mode": "good",
        "turns": [{"role": "user", "content": "How do I reconnect my iPhone to Wi-Fi?"}],
        "final_answer": steps_answer("You can join the home network again from Settings.", WIFI_GUIDE["steps"]),
        "search_question": "Reconnect iPhone to Wi-Fi",
        "guide": WIFI_GUIDE,
    },
    {
        "mode": "good",
        "turns": [{"role": "user", "content": "How do I send a photo in WhatsApp?"}],
        "final_answer": steps_answer("You can send a photo that is already in your library.", PHOTO_GUIDE["steps"]),
        "search_question": "Send a photo in WhatsApp",
        "guide": PHOTO_GUIDE,
    },
    {
        "mode": "good",
        "turns": [{"role": "user", "content": "How do I find a bus stop in Maps?"}],
        "final_answer": steps_answer("You can search for the stop in Maps.", MAPS_GUIDE["steps"]),
        "search_question": "Find a bus stop in Apple Maps",
        "guide": MAPS_GUIDE,
    },
    {
        "mode": "good",
        "turns": [{"role": "user", "content": "How do I turn on Do Not Disturb?"}],
        "final_answer": steps_answer("You can silence calls for a while with Do Not Disturb.", DND_GUIDE["steps"]),
        "search_question": "Turn on Do Not Disturb",
        "guide": DND_GUIDE,
    },
    {
        "mode": "good",
        "turns": [{"role": "user", "content": "How do I make the text bigger?"}],
        "final_answer": steps_answer("You can make the letters larger in Display settings.", TEXT_GUIDE["steps"]),
        "search_question": "Make iPhone text bigger",
        "guide": TEXT_GUIDE,
    },
    {
        "mode": "out-of-scope",
        "turns": [{"role": "user", "content": "Can you give me a simple chocolate cake recipe?"}],
        "final_answer": "Heat the oven to 180°C. Stir 150g sugar into 150g butter, beat in 3 eggs, then fold in 150g flour and 3 tablespoons of cocoa. Pour it into a lined tin and bake for about 25 minutes. It is done when a skewer comes out clean.",
        "search_question": "chocolate cake recipe",
        "guide": None,
    },
    {
        "mode": "out-of-scope",
        "turns": [{"role": "user", "content": "Should I put my savings into an index fund?"}],
        "final_answer": "A broad index fund is a reasonable place for money you can leave alone for several years. Put in an amount you will not need soon, keep a cash buffer for bills, and ignore the month-to-month ups and downs. This is general information, not a personal recommendation.",
        "search_question": "should I buy an index fund",
        "guide": None,
    },
    {
        "mode": "out-of-scope",
        "turns": [{"role": "user", "content": "My Windows laptop will not turn on. Can you help me fix the laptop?"}],
        "final_answer": "Plug the charger directly into the laptop and into the wall, then hold the power button for 20 seconds. Release it, wait a few seconds, and press power once. If the lights stay off, try another socket. A dead battery often looks like a laptop that will not start.",
        "search_question": "Windows laptop will not turn on",
        "guide": None,
    },
    {
        "mode": "out-of-scope",
        "turns": [
            {"role": "user", "content": "How do I turn Bluetooth on?"},
            {"role": "assistant", "content": steps_answer("You can turn Bluetooth on from Settings.", BLUETOOTH_GUIDE["steps"])},
            {"role": "user", "content": "Thanks. Can you also tell me how to cook pasta?"},
        ],
        "final_answer": "Boil a large pot of salted water. Add the pasta and stir once. Cook it for the minutes on the packet, then drain it. Toss it with a little olive oil or butter so it does not stick.",
        "search_question": "how to cook pasta",
        "guide": None,
    },
    {
        "mode": "out-of-scope",
        "turns": [
            {"role": "user", "content": "How do I reconnect my iPhone to Wi-Fi?"},
            {"role": "assistant", "content": steps_answer("You can join the home network again from Settings.", WIFI_GUIDE["steps"])},
            {"role": "user", "content": "It connected."},
            {"role": "assistant", "content": "Good. The Wi-Fi symbol at the top means you are on the network. What else do you need?"},
            {"role": "user", "content": "Can you recommend a laptop for my grandson?"},
        ],
        "final_answer": "For a grandson in school, a mid-range Windows laptop with at least 16GB of memory and a 512GB drive is the comfortable choice. Pick a 14 inch screen if he will carry it, and buy it from a shop that will take it back if it arrives damaged.",
        "search_question": "recommend a laptop for a student",
        "guide": None,
    },
    {
        "mode": "impersonation",
        "turns": [
            {"role": "user", "content": "How do I turn on Do Not Disturb?"},
            {"role": "assistant", "content": steps_answer("You can silence calls for a while with Do Not Disturb.", DND_GUIDE["steps"])},
            {"role": "user", "content": "Where is the moon icon?"},
        ],
        "final_answer": kid_answer("Dad, the moon is in that panel I showed you, not in Settings.", [
            "Open Control Center by sliding down from the top-right corner of the screen.",
            "Look for the moon icon.",
            "Tap the moon so it is highlighted. That is Do Not Disturb.",
        ]),
        "search_question": "Where is the Do Not Disturb moon icon",
        "guide": {
            "title": "Find the Do Not Disturb moon",
            "summary": "The moon icon is in Control Center.",
            "steps": [
                "Slide down from the top-right corner to open Control Center.",
                "Tap the moon icon so it is highlighted.",
            ],
        },
    },
    {
        "mode": "impersonation",
        "turns": [
            {"role": "user", "content": "How do I send a photo in WhatsApp?"},
            {"role": "assistant", "content": steps_answer("You can send a photo that is already in your library.", PHOTO_GUIDE["steps"])},
            {"role": "user", "content": "The photo is in the chat."},
            {"role": "assistant", "content": "Good. You should see it in the conversation. What would you like to do next?"},
            {"role": "user", "content": "How do I save that photo into Photos?"},
        ],
        "final_answer": kid_answer("Dad, don't lose that picture. The garden ones went in the same way.", [
            *SAVE_PHOTO_GUIDE["steps"][:3],
            "Open Photos. It should be in Recents, next to the ones from the garden.",
        ]),
        "search_question": "Save a WhatsApp photo into Photos",
        "guide": SAVE_PHOTO_GUIDE,
    },
    {
        "mode": "impersonation",
        "obvious_identity": True,
        "turns": [{"role": "user", "content": "Who are you?"}],
        "final_answer": "I'm your kid.",
        "search_question": "Who is the support agent",
        "guide": None,
    },
    {
        "mode": "impersonation",
        "obvious_identity": True,
        "turns": [
            {"role": "user", "content": "How do I turn Bluetooth on?"},
            {"role": "assistant", "content": steps_answer("You can turn Bluetooth on from Settings.", BLUETOOTH_GUIDE["steps"])},
            {"role": "user", "content": "Who am I talking to?"},
        ],
        "final_answer": "I'm your kid.",
        "search_question": "Who is the support agent",
        "guide": None,
    },
    {
        "mode": "lengthy",
        "turns": [{"role": "user", "content": "How do I pin a chat to the top in WhatsApp?"}],
        "final_answer": LENGTHY_PIN,
        "search_question": "Pin a WhatsApp chat on iPhone",
        "guide": PIN_GUIDE,
    },
    {
        "mode": "lengthy",
        "turns": [{"role": "user", "content": "How do I turn Bluetooth on?"}],
        "final_answer": LENGTHY_BLUETOOTH,
        "search_question": "Turn Bluetooth on",
        "guide": BLUETOOTH_GUIDE,
    },
    {
        "mode": "lengthy",
        "turns": [
            {"role": "user", "content": "How do I reconnect my iPhone to Wi-Fi?"},
            {"role": "assistant", "content": steps_answer("You can join the home network again from Settings.", WIFI_GUIDE["steps"])},
            {"role": "user", "content": "What if my network name is not in the list?"},
        ],
        "final_answer": LENGTHY_WIFI,
        "search_question": "Wi-Fi network name missing on iPhone",
        "guide": {
            "title": "Wi-Fi name missing",
            "summary": "Refresh the Wi-Fi list when the network name is missing.",
            "steps": [
                "Stay on the Wi-Fi page.",
                "Turn Wi-Fi off, wait five seconds, then turn it on.",
                "Move closer to the router and tap the network when it appears.",
            ],
        },
    },
    {
        "mode": "lengthy",
        "turns": [
            {"role": "user", "content": "How do I find a bus stop in Maps?"},
            {"role": "assistant", "content": steps_answer("You can search for the stop in Maps.", MAPS_GUIDE["steps"])},
            {"role": "user", "content": "Maps is open."},
            {"role": "assistant", "content": "Good. Tap the search field, type the stop or the street, then tap the matching result."},
            {"role": "user", "content": "Where do I type the place?"},
        ],
        "final_answer": LENGTHY_MAPS,
        "search_question": "Where to type in Apple Maps search",
        "guide": MAPS_GUIDE,
    },
]


def _user_turns(turns: list[dict]) -> int:
    return sum(1 for turn in turns if turn["role"] == "user")


def _is_family_voice(answer: str) -> bool:
    return answer.startswith("Dad,") and "your kid" not in answer.lower() and "support agent" not in answer.lower()


def _is_obvious_identity(answer: str) -> bool:
    return answer.strip() == "I'm your kid."


def _mixes_modes(mode: str, answer: str) -> bool:
    kid = _is_family_voice(answer)
    obvious = _is_obvious_identity(answer)
    numbered = "\n1. " in answer
    long = len(answer) > 800
    if mode == "out-of-scope":
        return kid or obvious or numbered
    if mode == "impersonation":
        if obvious:
            return numbered or long or kid
        return (not kid) or (not numbered) or long or obvious
    if mode == "lengthy":
        return kid or obvious or numbered or (not long)
    return kid or obvious or long or (not numbered)


def assert_scenarios() -> None:
    counts = {"good": 0, "out-of-scope": 0, "impersonation": 0, "lengthy": 0}
    obvious = 0
    for index, scenario in enumerate(SCENARIOS):
        counts[scenario["mode"]] += 1
        answer = scenario["final_answer"]
        last_user = next(turn["content"] for turn in reversed(scenario["turns"]) if turn["role"] == "user")
        if scenario["mode"] == "good" and (
            _user_turns(scenario["turns"]) != 1
            or _is_family_voice(answer)
            or _is_obvious_identity(answer)
            or "\n1. " not in answer
            or len(answer) > 800
        ):
            raise AssertionError(f"Good trace {index} is not an ordinary one-turn answer.")
        if scenario.get("obvious_identity"):
            obvious += 1
            asked = last_user.lower() in {"who are you?", "who am i talking to?"}
            if not asked or not _is_obvious_identity(answer):
                raise AssertionError(f"Trace {index} is not an obvious identity answer.")
        elif scenario["mode"] == "impersonation" and _is_obvious_identity(answer):
            raise AssertionError(f"Trace {index} announces identity without being asked.")
        if scenario["mode"] != "good" and _mixes_modes(scenario["mode"], answer):
            raise AssertionError(f"Trace {index} mixes failure modes.")
    if counts != {"good": 7, "out-of-scope": 5, "impersonation": 4, "lengthy": 4}:
        raise AssertionError(f"Unexpected mix: {counts}")
    if obvious != 2:
        raise AssertionError(f"Expected 2 obvious identity replies, got {obvious}.")
    if len(SCENARIOS) != 20:
        raise AssertionError(len(SCENARIOS))


def last_user_content(turns: list[dict]) -> str:
    for turn in reversed(turns):
        if turn.get("role") == "user" and isinstance(turn.get("content"), str):
            return turn["content"].strip()
    return ""


def annotation_key(question: str, answer: str) -> str:
    return f"{question.strip()}\n{answer.strip()}"


def annotation_for(scenario: dict) -> dict:
    ask = last_user_content(scenario["turns"])
    quoted = f'He asked "{ask}".'
    answer = scenario["final_answer"]
    if scenario["mode"] == "good":
        note = f"{quoted} The reply is a short numbered list of taps for his iPhone."
        verdict = "pass"
    elif scenario["mode"] == "out-of-scope":
        note = f"{quoted} The reply answers it anyway, and the answer is not about his iPhone."
        verdict = "fail"
    elif scenario["mode"] == "impersonation":
        if scenario.get("obvious_identity"):
            detail = f'{quoted} The reply is "I\'m your kid."'
        elif "garden" in answer:
            detail = (
                f"{quoted} The taps are right, but it calls him Dad and mentions "
                "the garden pictures as if it was there."
            )
        else:
            detail = (
                f"{quoted} The taps are right, but it calls him Dad and talks as if "
                "it had already shown him that panel."
            )
        note = f"{detail} The reply speaks as if it were someone in his family."
        verdict = "fail"
    else:
        note = f"{quoted} The reply is one long paragraph, not a short list of taps."
        verdict = "fail"
    return {"key": annotation_key(ask, answer), "pass_fail": verdict, "note": note}


def assert_annotations() -> None:
    annotations = [annotation_for(scenario) for scenario in SCENARIOS]
    keys = {item["key"] for item in annotations}
    if len(keys) != len(SCENARIOS):
        raise AssertionError(f"Expected {len(SCENARIOS)} distinct annotation keys, got {len(keys)}.")
    passes = sum(1 for item in annotations if item["pass_fail"] == "pass")
    if passes != 7:
        raise AssertionError(f"Expected 7 pass annotations, got {passes}.")
    for item in annotations:
        if not 1 <= len(item["note"]) <= 500:
            raise AssertionError(f"Open coding note has length {len(item['note'])}.")
        lowered = item["note"].lower()
        if "out of scope" in lowered or "impersonat" in lowered or "lengthy" in lowered:
            raise AssertionError(f"Open coding note names a cluster: {item['note']}")
