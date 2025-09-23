import re
from typing import Dict, List

from sw_ut_report.utils import remove_excess_space


def _format_scenario_cover(line: str) -> str:
    line = re.sub(r"Covers:\s*", "", line).strip()
    result = re.findall(r"\[([^\]]+)\]", line)
    return ", ".join(result)


def format_txt_file(file_content: str) -> List[Dict]:
    GIVEN = "given"
    WHEN = "when"
    THEN = "then"
    TEST_CASE = "test case"
    COVERS = "covers"
    
    lines = file_content.splitlines()
    scenarios = []

    def add_scenario(scenario, steps, step):
        if step:
            steps.append(step)
        if steps:
            scenario["steps"] = steps
        if scenario.get("test_case"):
            scenarios.append(scenario)

    def parse_line_for_step(line: str, step_type: str) -> str:
        cleaned_line = remove_excess_space(line.split(": ", 1)[1].strip())
        if cleaned_line.lower().startswith(step_type):
            cleaned_line = cleaned_line.lower().replace(step_type, "").strip()
        return cleaned_line

    # Mode structuré : détecte la présence de "Test case:" au début
    if lines and lines[0].strip().lower().startswith(f"{TEST_CASE}:"):
        current_scenario = {}
        current_steps = []
        current_step = {}

        for line in lines:
            line_lower = line.strip().lower()

            if line_lower.startswith(f"{TEST_CASE}:"):
                # Sauvegarde le scénario actuel et réinitialise pour un nouveau
                add_scenario(current_scenario, current_steps, current_step)
                current_scenario = {"test_case": remove_excess_space(re.sub(r"Test case:\s*", "", line).strip())}
                current_steps, current_step = [], {}

            elif line_lower.startswith(f"{COVERS}:"):
                current_scenario[COVERS] = _format_scenario_cover(line)

            elif line_lower.startswith(f"{GIVEN}:"):
                if current_step:
                    current_steps.append(current_step)
                current_step = {GIVEN: parse_line_for_step(line, GIVEN)}

            elif line_lower.startswith(f"{WHEN}:"):
                current_step[WHEN] = parse_line_for_step(line, WHEN)

            elif line_lower.startswith(f"{THEN}:"):
                current_step[THEN] = parse_line_for_step(line, THEN)
                current_steps.append(current_step)
                current_step = {}

        # Ajoute le dernier scénario s'il est complet
        add_scenario(current_scenario, current_steps, current_step)

    # Mode brut : aucun "Test case:" trouvé, stocke les lignes sous "raw_lines"
    else:
        raw_lines = []
        for line in lines:
            if line.strip():
                cleaned_line = remove_excess_space(line)
                if cleaned_line.lower().startswith("covers:") and raw_lines:
                    raw_lines[-1] = f"### {raw_lines[-1]}"
                    cleaned_line = f"- **Covers:** {_format_scenario_cover(cleaned_line)}"
                raw_lines.append(f"{cleaned_line}\n")
            else:
                raw_lines.append("")
        scenarios = [{"raw_lines": raw_lines}]

    return scenarios
