import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

import requests
import yaml

try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)


class AgentConfig:
    def __init__(self, cfg: Dict):
        backend = cfg.get("backend", {})
        agent = cfg.get("agent", {})
        self.base_url: str = backend.get("base_url", "http://127.0.0.1:8080").rstrip("/")
        self.username: Optional[str] = backend.get("username")
        self.application: Optional[str] = backend.get("application")
        self.os_type: str = backend.get("os", "windows").lower()
        self.source: str = agent.get("source", "python-agent")
        self.poll_interval: int = int(agent.get("poll_interval", 60))


class GestureAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.mapping: Dict[str, Dict] = {}

    def sync_config(self) -> None:
        """拉取后端配置"""
        params = {
            "username": self.config.username,
            "application": self.config.application,
            "os": self.config.os_type,
        }
        logging.info("Fetching config from %s", self.config.base_url)
        resp = requests.get(f"{self.config.base_url}/api/config", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        mappings = data.get("mappings", [])
        self.mapping = {}
        for item in mappings:
            action = item.get("action") or {}
            self.mapping[item.get("code")] = {
                "type": action.get("type"),
                "value": action.get("value"),
                "os": action.get("osType"),
                "description": action.get("description"),
                "payload": action.get("payloadJson"),
            }
        logging.info("Loaded %d gesture mappings", len(self.mapping))

    def perform_action(self, gesture_code: str) -> bool:
        """根据配置执行动作"""
        action = self.mapping.get(gesture_code)
        if not action:
            logging.warning("Gesture '%s' not found in mapping", gesture_code)
            return False

        action_type = (action.get("type") or "").lower()
        action_value = action.get("value") or ""

        success = False
        message = ""
        try:
            if action_type == "hotkey":
                success, message = self._execute_hotkey(action_value)
            else:
                message = f"Action type '{action_type}' not supported yet"
                logging.warning(message)
        except Exception as exc:  # pragma: no cover
            message = f"Execution failed: {exc}"
            logging.exception("Failed to perform action for %s", gesture_code)

        self.post_log(
            gesture_code=gesture_code,
            action_type=action_type,
            action_value=action_value,
            status="success" if success else "failure",
            message=message or ("Executed" if success else "No action executed"),
        )
        return success

    def _execute_hotkey(self, value: str):
        if not value:
            return False, "Empty hotkey value"
        keys = [k.strip() for k in value.replace("+", " ").split() if k.strip()]
        if not keys:
            return False, "Invalid hotkey definition"

        if pyautogui is None:  # pragma: no cover
            msg = "pyautogui not installed; skip actual key press"
            logging.warning(msg)
            return False, msg

        logging.info("Pressing hotkey: %s", "+".join(keys))
        pyautogui.hotkey(*keys)
        return True, f"Hotkey {value} sent"

    def post_log(
        self,
        gesture_code: str,
        action_type: str,
        action_value: str,
        status: str,
        message: str,
    ) -> None:
        payload = {
            "username": self.config.username,
            "application": self.config.application,
            "gestureCode": gesture_code,
            "actionType": action_type,
            "actionValue": action_value,
            "status": status,
            "message": message,
            "sourceAgent": self.config.source,
        }
        try:
            resp = requests.post(
                f"{self.config.base_url}/api/audit/log",
                json=payload,
                timeout=10,
            )
            resp.raise_for_status()
            logging.info("Log posted: %s", resp.json())
        except Exception as exc:  # pragma: no cover
            logging.error("Failed to post log: %s", exc)

    def send_event(self, event_type: str, payload: Optional[dict] = None) -> None:
        body = {
            "eventType": event_type,
            "username": self.config.username,
            "application": self.config.application,
            "payload": json.dumps(payload or {}),
        }
        try:
            resp = requests.post(f"{self.config.base_url}/api/event", json=body, timeout=10)
            resp.raise_for_status()
            logging.info("Event acknowledged: %s", resp.json())
        except Exception as exc:  # pragma: no cover
            logging.error("Failed to send event: %s", exc)


def load_config(path: Path) -> AgentConfig:
    if not path.exists():
        logging.error("Config file %s not found", path)
        sys.exit(1)
    with path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return AgentConfig(cfg)


def interactive_loop(agent: GestureAgent):
    logging.info("Entering interactive mode. Type 'quit' to exit.")
    while True:
        try:
            raw = input("Gesture code> ").strip()
        except (EOFError, KeyboardInterrupt):  # pragma: no cover
            print()
            break
        if not raw:
            continue
        if raw.lower() in {"quit", "exit"}:
            break
        if raw.startswith("event:"):
            _, evt = raw.split(":", 1)
            agent.send_event(evt.strip() or "custom_event")
            continue
        agent.perform_action(raw)
    logging.info("Interactive mode exited.")


def main():
    parser = argparse.ArgumentParser(description="Gesture control agent (minimal skeleton)")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--sync", action="store_true", help="Only sync config and exit")
    parser.add_argument("--watch", action="store_true", help="Sync config then enter interactive loop")
    parser.add_argument("--gesture", help="Single gesture code to execute once")
    parser.add_argument("--event", help="Send an eventType to /api/event")
    args = parser.parse_args()

    cfg = load_config(Path(args.config))
    agent = GestureAgent(cfg)

    try:
        agent.sync_config()
    except Exception as exc:  # pragma: no cover
        logging.error("Unable to fetch config: %s", exc)
        sys.exit(1)

    if args.sync and not args.watch and not args.gesture and not args.event:
        logging.info("Config sync finished.")
        return

    if args.event:
        agent.send_event(args.event)

    if args.gesture:
        agent.perform_action(args.gesture)

    if args.watch or (not args.sync and not args.gesture and not args.event):
        interactive_loop(agent)


if __name__ == "__main__":
    main()


