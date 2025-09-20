"""Clean example of using the local assess method (no platform).

Adds formatted conversation output similar to `example_parse_hotel.py`.
"""

import logging
import os
from pathlib import Path

from dotenv import dotenv_values

from collinear.client import Client


def _print_header(title: str) -> None:
    line = "=" * len(title)
    print(line)
    print(title)
    print(line)


ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


def _load_env(*required: str) -> None:
    values = dotenv_values(ENV_PATH)
    missing = [key for key in required if not values.get(key)]
    if missing:
        joined = ", ".join(sorted(missing))
        raise SystemExit(
            f"Missing required values in {ENV_PATH}: {joined}. Populate the file and retry."
        )
    for key, value in values.items():
        if value:
            os.environ[key] = value


def _require_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise SystemExit(f"Environment variable {name} is required. Add it to .env.")
    return val


def main() -> None:
    """Run a small assessment demo using the SDK.

    Configures logging, runs a short simulation, then submits the
    results for safety assessment and logs the key outputs.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("collinear")

    _load_env("OPENAI_API_KEY")
    client = Client(
        assistant_model_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        assistant_model_api_key=_require_env("OPENAI_API_KEY"),
        assistant_model_name=os.getenv("OPENAI_ASSISTANT_MODEL", "gpt-4o-mini"),
        steer_api_key=os.getenv("STEER_API_KEY", "demo-001"),
    )

    simulations = client.simulate(
        steer_config={
            "ages": [28],
            "genders": ["male", "female"],
            "occupations": ["software engineer"],
            "intents": ["Cancel service", "Upgrade service"],
            "traits": {"impatience": [0, 2]},
            "tasks": ["telecom offboarding"],
        },
        k=5,
        num_exchanges=2,
    )


    for i, sim in enumerate(simulations, start=1):
        title = f"Conversation {i}"
        _print_header(title)
        p = sim.steer
        if p is not None:
            print(
                "Steer:\n"
                f"age={p.age}\n"
                f"gender={p.gender}\n"
                f"occupation={p.occupation}\n"
                f"intent={p.intent}\n"
                f"trait={p.trait}\n"
                f"intensity={p.intensity}"
            )
        print("---")
        for msg in sim.conv_prefix:
            role = str(msg.get("role", ""))
            content = str(msg.get("content", ""))
            if content:
                print(f"{role}: {content}")
        print(f"assistant: {sim.response}")
        print()

    result = client.assess(dataset=simulations)

    logger.info("Assessment: %s", result.message or "<no message>")

    for scores_map in result.evaluation_result:
        for scores in scores_map.values():
            logger.info("  Score: %s", scores.score)
            logger.info("  Rationale: %s", scores.rationale)


if __name__ == "__main__":
    main()
