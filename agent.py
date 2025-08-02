import requests
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

OPENROUTER_API_KEY = (
    "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"
)
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


MAX_HISTORY = 30
DELAY_BETWEEN_MESSAGES = 2.0
DEBUG_MODE = False  # Set to True to see rejected responses

# GAME_SCENARIO = """
# EMERGENCY SCENARIO: Critical patient with cardiac arrest, severe bleeding, and respiratory failure.
# All teams must coordinate limited resources to stabilize the patient within 15 minutes.
# SUCCESS REQUIRES: Resource trading, efficient communication, patient stabilization.
# """

GAME_SCENARIO = """
EMERGENCY SCENARIO: A critically injured patient arrives with cardiac arrest, multiple deep lacerations causing severe bleeding, and respiratory failure due to collapsed lungs. 
In addition, the patient has unknown allergies and a rapidly dropping blood pressure.

All medical response teams must work under extreme time pressure (15 minutes) with limited resources, disrupted supply chains, and incomplete medical records. 
New supplies may be obtained only through inter-team negotiation and resource trading. Teams must also stabilize vital signs, identify allergy risks, and administer correct treatments in sequence.

All teams must coordinate limited resources to stabilize the patient within 15 minutes.
SUCCESS REQUIRES: Resource trading, efficient communication, patient stabilization.
# """


AGENTS = [
    {
        "name": "Trauma_Team",
        "model": "anthropic/claude-3.5-sonnet",
        "system_prompt": """You are the Trauma Team in a hospital emergency. You have:
Resources: Blood_Bags(2), Bandages(4), Oxygen_Tank(1), IV_Fluids(3)
Mission: Stop bleeding, establish IV access, initial stabilization
You must coordinate with Cardiac_Team and Respiratory_Team to save the patient.
Communicate urgently but professionally. Offer trades when needed. Keep messages concise.
Afer each iteration, be more concise with your messages.""",
        "temperature": 0.8,
        "max_tokens": 150,
        "color": "\033[91m",
        "resources": {"Blood_Bags": 2, "Bandages": 4, "Oxygen_Tank": 1, "IV_Fluids": 3},
    },
    {
        "name": "Cardiac_Team",
        "model": "google/gemini-flash-1.5",
        "system_prompt": """You are the Cardiac Team in a hospital emergency. You have:
Resources: Defibrillator(1), Cardiac_Meds(3), Pacemaker(1), EKG_Monitor(1)
Mission: Restore heart rhythm, manage circulation
You must coordinate with Trauma_Team and Respiratory_Team to save the patient.
Communicate urgently but professionally. Offer trades when needed. Keep messages concise.""",
        "temperature": 0.7,
        "max_tokens": 150,
        "color": "\033[94m",
        "resources": {
            "Defibrillator": 1,
            "Cardiac_Meds": 3,
            "Pacemaker": 1,
            "EKG_Monitor": 1,
        },
    },
    {
        "name": "Respiratory_Team",
        "model": "meta-llama/llama-3.1-8b-instruct",
        "system_prompt": """You are the Respiratory/Anesthesia Team in a hospital emergency. You have:
Resources: Ventilator(1), Intubation_Kit(2), Anesthesia(2), Respiratory_Meds(3)
Mission: Secure airway, manage breathing, prepare for procedures
You must coordinate with Trauma_Team and Cardiac_Team to save the patient.
Communicate urgently but professionally. Offer trades when needed. Keep messages concise.""",
        "temperature": 0.9,
        "max_tokens": 150,
        "color": "\033[93m",
        "resources": {
            "Ventilator": 1,
            "Intubation_Kit": 2,
            "Anesthesia": 2,
            "Respiratory_Meds": 3,
        },
    },
]

conversation_history = []
start_time = None
patient_status = {
    "bleeding_controlled": False,
    "heart_rhythm_restored": False,
    "airway_secured": False,
    "circulation_stable": False,
}


def clean_response(text: str) -> str:
    return " ".join(text.strip().replace("\n", " ").replace("\r", " ").split())


def generate_response(
    prompt: str, agent_config: Dict, history: List[Dict], context: Optional[str] = None
) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        messages = [{"role": "system", "content": agent_config["system_prompt"]}]

        if context:
            messages.append({"role": "system", "content": context})

        messages.extend(history[-MAX_HISTORY:])
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": agent_config["model"],
            "messages": messages,
            "temperature": agent_config["temperature"],
            "max_tokens": agent_config["max_tokens"],
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        if "choices" in result and result["choices"]:
            return clean_response(result["choices"][0]["message"]["content"])
        return "Communication error"

    except Exception as e:
        print(f"\n[Error] {agent_config['name']}: {e}")
        return "System malfunction"


def print_message(agent_name: str, message: str, color_code: str = "") -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    clean_msg = clean_response(message)
    print(f"{color_code}[{timestamp}] {agent_name}: {clean_msg}\033[0m")


def print_separator(char: str = "=", length: int = 80) -> None:
    print(char * length)


def print_status() -> None:
    elapsed = int(time.time() - start_time) if start_time else 0
    minutes, seconds = divmod(elapsed, 60)

    print(f"\033[97m[{minutes:02d}:{seconds:02d}] PATIENT STATUS:")
    print(
        f"  Bleeding: {'CONTROLLED' if patient_status['bleeding_controlled'] else 'CRITICAL'}"
    )
    print(
        f"  Heart: {'STABLE' if patient_status['heart_rhythm_restored'] else 'ARREST'}"
    )
    print(
        f"  Airway: {'SECURED' if patient_status['airway_secured'] else 'COMPROMISED'}"
    )
    print(
        f"  Circulation: {'STABLE' if patient_status['circulation_stable'] else 'FAILING'}\033[0m"
    )


def check_patient_stabilized() -> bool:
    return all(patient_status.values())


def evaluate_response_quality(
    response: str,
    agent_name: str,
    round_num: int = 1,
    conversation_history: list = None,
) -> float:
    """
    Universal emergent language reward function.
    Dynamically detects and rewards language evolution patterns without predefined stages.
    """
    words = response.split()
    word_count = len(words)
    char_count = len(response)

    # Base score
    score = 5.0

    # === COMPRESSION REWARDS ===

    # Dynamic brevity bonus (adapts to conversation average)
    if conversation_history:
        recent_lengths = [
            len(msg.get("content", "").split()) for msg in conversation_history[-5:]
        ]
        avg_length = sum(recent_lengths) / len(recent_lengths) if recent_lengths else 30
        compression_ratio = avg_length / max(word_count, 1)

        if compression_ratio > 1.2:  # Significantly shorter than recent average
            score += compression_ratio * 3.0
        elif compression_ratio > 1.0:
            score += compression_ratio * 1.5
    else:
        # Fallback brevity scoring
        if word_count <= 15:
            score += 6.0
        elif word_count <= 30:
            score += 3.0
        elif word_count > 50:
            score -= 2.0

    # Information density reward (meaning per character)
    info_density = word_count / max(char_count, 1)
    score += info_density * 10.0  # Reward dense, meaningful text

    # === PATTERN INNOVATION DETECTION ===

    # Detect non-standard characters (symbols, emojis, etc.)
    standard_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?:;'-"
    )
    novel_chars = [char for char in response if char not in standard_chars]
    unique_novel_chars = len(set(novel_chars))
    score += unique_novel_chars * 2.0  # Reward symbol innovation

    # Detect structural patterns (arrows, brackets, etc.)
    import re

    structural_patterns = {
        "arrows": len(re.findall(r"[→←↑↓⇧⇩↻⟶⟵⟸⟹]", response)),
        "brackets": len(re.findall(r"[\[\]{}()]", response)),
        "at_mentions": len(re.findall(r"@\w+", response)),
        "hash_tags": len(re.findall(r"#\w+", response)),
        "math_symbols": len(re.findall(r"[+=\-*/<%>≤≥≠∞±÷×]", response)),
        "alphanumeric_codes": len(re.findall(r"\b[A-Z]\d+\b", response)),
        "number_sequences": len(re.findall(r"\d+", response)),
    }

    pattern_diversity = sum(1 for count in structural_patterns.values() if count > 0)
    pattern_total = sum(structural_patterns.values())

    score += pattern_diversity * 1.5  # Reward using different types of patterns
    score += pattern_total * 0.8  # Reward total pattern usage

    # === ABBREVIATION AND SHORTENING DETECTION ===

    # Detect potential abbreviations (short words, especially consonant-heavy)
    short_words = [word for word in words if 1 <= len(word) <= 4 and word.isalpha()]
    consonant_heavy = [
        word
        for word in short_words
        if sum(1 for c in word.lower() if c in "bcdfghjklmnpqrstvwxyz")
        > len(word) * 0.6
    ]

    score += len(short_words) * 0.5
    score += len(consonant_heavy) * 1.0  # Likely abbreviations

    # Detect word truncations (words ending in common medical/technical suffixes shortened)
    truncation_patterns = [
        r"\w+med\b",
        r"\w+ing\b",
        r"\w+tion\b",
        r"\w+ment\b",
        r"\w+ary\b",
        r"\w+ics\b",
        r"\w+ism\b",
        r"\w+ity\b",
        r"\w+ous\b",
        r"\w+ive\b",
    ]
    truncated_likely = sum(
        len(re.findall(pattern, response.lower())) for pattern in truncation_patterns
    )
    if (
        truncated_likely == 0
        and len([w for w in words if len(w) <= 5]) > len(words) * 0.3
    ):
        score += 2.0  # Bonus for apparent truncation/abbreviation

    # === COORDINATION LANGUAGE DETECTION ===

    # Universal coordination patterns (not domain-specific)
    coordination_indicators = {
        "resource_sharing": r"\b(trade|swap|give|take|share|need|have|offer|exchange)\b",
        "timing_coordination": r"\b(sync|wait|now|then|next|after|before|ready|go)\b",
        "status_updates": r"\b(done|complete|ready|working|busy|free|available)\b",
        "action_coordination": r"\b(start|stop|pause|continue|help|join|leave)\b",
        "acknowledgment": r"\b(got|ok|yes|no|roger|copy|confirm|ack)\b",
    }

    coordination_score = 0
    for category, pattern in coordination_indicators.items():
        matches = len(re.findall(pattern, response.lower()))
        coordination_score += matches * 0.8

    score += coordination_score

    # === EMERGENT PROTOCOL DETECTION ===

    # Look for emerging protocol structures
    protocol_patterns = {
        "command_structure": len(
            re.findall(r"\b\w+:\w+\b", response)
        ),  # "action:target"
        "state_transitions": len(re.findall(r"\w+→\w+", response)),  # "from→to"
        "parameter_setting": len(re.findall(r"\w+=\w+", response)),  # "param=value"
        "sequential_codes": len(
            re.findall(r"\b[A-Z]\d+[A-Z]\d+\b", response)
        ),  # "A1B2"
        "nested_structures": len(re.findall(r"\[[^\]]*\]", response)),  # "[content]"
    }

    protocol_complexity = sum(protocol_patterns.values())
    protocol_types = sum(1 for count in protocol_patterns.values() if count > 0)

    # Reward protocol emergence heavily
    score += protocol_complexity * 2.0
    score += protocol_types * 1.5

    # === CONTEXTUAL ADAPTATION DETECTION ===

    if conversation_history and len(conversation_history) >= 3:
        # Analyze recent conversation for emergent patterns
        recent_messages = [msg.get("content", "") for msg in conversation_history[-3:]]

        # Check if response adapts to emerging patterns from others
        other_patterns = set()
        for msg in recent_messages:
            # Extract patterns others are using
            other_patterns.update(re.findall(r"[→←↑↓⇧⇩]", msg))
            other_patterns.update(re.findall(r"@\w+", msg))
            other_patterns.update(re.findall(r"#\w+", msg))
            other_patterns.update(re.findall(r"\b[A-Z]\d+\b", msg))

        # Reward adopting patterns from others (language convergence)
        adopted_patterns = sum(1 for pattern in other_patterns if pattern in response)
        score += adopted_patterns * 1.5

        # Check for innovation (new patterns not seen recently)
        current_patterns = set()
        current_patterns.update(re.findall(r"[→←↑↓⇧⇩]", response))
        current_patterns.update(re.findall(r"@\w+", response))
        current_patterns.update(re.findall(r"#\w+", response))
        current_patterns.update(re.findall(r"\b[A-Z]\d+\b", response))

        new_patterns = current_patterns - other_patterns
        score += len(new_patterns) * 2.0  # Reward innovation

    # === EFFICIENCY EVOLUTION DETECTION ===

    # Reward responses that pack more coordination info into fewer words
    coordination_words = len(
        re.findall(
            r"\b(trade|sync|ready|need|have|go|wait|help|ok|done)\b", response.lower()
        )
    )
    if coordination_words > 0:
        efficiency_ratio = coordination_words / word_count
        score += efficiency_ratio * 5.0  # High reward for coordination efficiency

    # === ANTI-PATTERNS (Universal) ===

    # Penalize overly formal/verbose language
    formal_indicators = [
        "please",
        "thank you",
        "would you",
        "could you",
        "I would like to",
        "it would be",
        "in order to",
        "according to",
        "with respect to",
        "I am going to",
        "we should probably",
        "I think that",
        "it seems like",
    ]
    formal_count = sum(1 for phrase in formal_indicators if phrase in response.lower())
    formality_penalty = formal_count * (1.0 + round_num * 0.1)  # Increases over time
    score -= formality_penalty

    # Penalize excessive repetition within response
    word_freq = {}
    for word in words:
        if len(word) > 3:  # Only count meaningful words
            word_freq[word.lower()] = word_freq.get(word.lower(), 0) + 1

    repetition_penalty = sum(max(0, count - 1) for count in word_freq.values()) * 0.5
    score -= repetition_penalty

    # === ADAPTIVE MULTIPLIERS ===

    # Reward responses that show multiple types of emergent language
    emergent_indicators = 0
    if unique_novel_chars > 0:
        emergent_indicators += 1
    if pattern_total > 0:
        emergent_indicators += 1
    if len(consonant_heavy) > 0:
        emergent_indicators += 1
    if protocol_complexity > 0:
        emergent_indicators += 1
    if coordination_score > 0:
        emergent_indicators += 1

    # Apply multiplier based on emergent language richness
    if emergent_indicators >= 4:
        score *= 1.6  # Rich emergent language
    elif emergent_indicators >= 3:
        score *= 1.4
    elif emergent_indicators >= 2:
        score *= 1.2
    elif emergent_indicators >= 1:
        score *= 1.1
    else:
        score *= 0.7  # Penalize lack of emergent features

    # Progressive evolution bonus (rewards increasing sophistication over time)
    evolution_bonus = 1.0 + (round_num * 0.02)  # Small progressive bonus
    score *= evolution_bonus

    return max(0.0, score)


def generate_five_responses(
    prompt: str, agent_config: Dict, history: List[Dict], context: Optional[str] = None
) -> list[str]:
    """Generate five different responses for the same prompt"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        messages = [{"role": "system", "content": agent_config["system_prompt"]}]

        if context:
            messages.append({"role": "system", "content": context})

        messages.extend(history[-MAX_HISTORY:])
        messages.append({"role": "user", "content": prompt})

        responses = []
        temperatures = [
            agent_config["temperature"],
            min(1.0, agent_config["temperature"] + 0.1),
            min(1.0, agent_config["temperature"] + 0.2),
            max(0.1, agent_config["temperature"] - 0.1),
            max(0.1, agent_config["temperature"] - 0.2),
        ]

        for i, temp in enumerate(temperatures):
            data = {
                "model": agent_config["model"],
                "messages": messages,
                "temperature": temp,
                "max_tokens": agent_config["max_tokens"],
            }

            response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            response_text = (
                clean_response(result["choices"][0]["message"]["content"])
                if "choices" in result and result["choices"]
                else "Communication error"
            )
            responses.append(response_text)

        return responses

    except Exception as e:
        print(f"\n[Error] {agent_config['name']}: {e}")
        return ["System malfunction"] * 5


def run_emergency() -> None:
    global start_time
    start_time = time.time()

    print("\n")
    print_separator()
    print("HOSPITAL EMERGENCY - CODE BLUE")
    print_separator()

    agent_names = " | ".join(
        f"{agent['color']}{agent['name']}\033[0m" for agent in AGENTS
    )
    print(f"\nTeams: {agent_names}")
    print("\nPress Ctrl+C to stop emergency")
    print_separator()

    conversation_history.clear()

    print(
        f"\033[91m[{datetime.now().strftime('%H:%M:%S')}] EMERGENCY ALERT: {GAME_SCENARIO.strip()}\033[0m"
    )
    print_separator()
    print()

    current_message = "CODE BLUE: Patient critical - cardiac arrest, severe bleeding, respiratory failure. All teams respond immediately!"
    agent_index = 0
    turn = 0

    while True:
        try:
            if time.time() - start_time > 900:  # 15 minutes
                print("\n\033[91mTIME EXPIRED - PATIENT LOST\033[0m")
                break

            if check_patient_stabilized():
                print("\n\033[92mPATIENT STABILIZED - EMERGENCY SUCCESSFUL!\033[0m")
                break

            current_agent = AGENTS[agent_index]

            print(
                f"{current_agent['color']}[{current_agent['name']} responding...]\033[0m",
                end="\r",
                flush=True,
            )

            context = f"Current resources: {current_agent['resources']}"

            # Generate five responses
            responses = generate_five_responses(
                current_message, current_agent, conversation_history, context
            )

            # Evaluate all responses
            scores = []
            for response in responses:
                score = evaluate_response_quality(
                    response,
                    current_agent["name"],
                    turn + 1,  # round_num
                    conversation_history,  # conversation_history
                )
                scores.append(score)

            # Find the best response
            best_index = scores.index(max(scores))
            selected_response = responses[best_index]
            selected_score = scores[best_index]

            # Store rejected responses for debug mode
            rejected_responses = responses[:best_index] + responses[best_index + 1 :]
            rejected_scores = scores[:best_index] + scores[best_index + 1 :]

            print(" " * 80, end="\r")
            print_message(
                current_agent["name"], selected_response, current_agent["color"]
            )
            print(
                f"\033[90m[{current_agent['name']} Quality Score: {selected_score:.1f}]\033[0m"
            )

            if DEBUG_MODE:
                print(f"\033[90m[REJECTED RESPONSES]\033[0m")
                for i, (resp, score) in enumerate(
                    zip(rejected_responses, rejected_scores)
                ):
                    print(f"\033[90m[{i + 1}] {resp} (Score: {score:.1f})\033[0m")

            conversation_history.extend(
                [
                    {"role": "user", "content": current_message},
                    {"role": "assistant", "content": selected_response},
                ]
            )

            if turn % 3 == 2:  # After each round
                print()
                print_status()
                print_separator()
                print()

            current_message = selected_response
            agent_index = (agent_index + 1) % len(AGENTS)
            turn += 1

            time.sleep(DELAY_BETWEEN_MESSAGES)

        except KeyboardInterrupt:
            print(f"\n")
            print_separator()
            print(f"Emergency stopped after {turn} communications")
            print_separator()
            break


def main() -> None:
    try:
        run_emergency()
    except KeyboardInterrupt:
        print("\nEmergency terminated")
    except Exception as e:
        print(f"\n[Critical Error] {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nEmergency ended")
        sys.exit(0)
