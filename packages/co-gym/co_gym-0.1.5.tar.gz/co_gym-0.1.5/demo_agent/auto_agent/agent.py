import argparse
import json
import logging
import os
import re
from typing import Dict, List

import knowledge_storm
import toml
import yaml
from aact.cli.launch.launch import _sync_run_node
from aact.cli.reader import NodeConfig
from aact.cli.reader.dataflow_reader import NodeArgs
from knowledge_storm.lm import LitellmModel

from collaborative_gym.utils.context_processing import ContextProcessor
from collaborative_gym.utils.utils import prepare_lm_kwargs
from demo_agent.utils.memory import Scratchpad

logging.basicConfig(
    level=logging.INFO, format="%(name)s : %(levelname)-8s : %(message)s"
)
logger = logging.getLogger(__name__)


class ReactAutoAgent:
    """A fully autonomous agent implemented with ReAct prompting strategy.
    This agent only interacts with the environment to complete the task and does not consider collaborating with human.

    The agent is enhanced with a scratchpad. The agent decides whether to update the scratchpad after each action.
    """

    def __init__(
        self,
        lm: knowledge_storm.lm.LM,
        add_task_demo,
        prompt_path="demo_agent/auto_agent/prompts.yaml",
    ):
        self.name = None
        self.task_description = None
        self.task_action_space_description = None
        self.lm = lm
        self.scratchpad = Scratchpad()
        self.action_history = []

        self.add_task_demo = add_task_demo
        self.task_demo = None

        with open(prompt_path, "r") as f:
            prompts = yaml.safe_load(f)

        self.act_prompt_template = "\n\n".join(
            [
                prompts["system_template"],
                prompts["action_history_template"],
                prompts["take_next_task_action_template"],
            ]
        )
        self.update_scratchpad_prompt_template = "\n\n".join(
            [
                prompts["system_template"],
                prompts["update_scratchpad_template"],
            ]
        )

        self.context_processor = ContextProcessor()

    def format_act_prompt(self, obs: Dict, action_space_description: str):
        return self.act_prompt_template.format(
            name=self.name,
            task_description=self.task_description,
            action_space_description=action_space_description,
            scratchpad=self.scratchpad.to_str(),
            observation=self.context_processor.observation_to_str(obs),
            action_history=self.context_processor.action_history_to_str(
                self.action_history
            ),
        )

    def format_update_scratchpad_prompt(self, obs: Dict):
        return self.update_scratchpad_prompt_template.format(
            name=self.name,
            task_description=self.task_description,
            scratchpad=self.scratchpad.to_str(),
            observation=self.context_processor.observation_to_str(obs),
            scratchpad_action_space_description=self.scratchpad.get_action_space_description(),
        )

    def start(
        self,
        name: str,
        team_members: List[str],
        task_description: str,
        action_space: dict,
        example_question: str,
        example_trajectory: List,
    ):
        """Start the agent with the given task information.

        This function will be called by collaborative_gym.nodes_agent_interface when the agent is started.
        """
        self.name = name
        # This is a fully autonomous agent, so it does not use `team_members`.
        self.task_description = task_description
        self.task_action_space_description = self.context_processor.action_space_to_str(
            action_space=action_space, excluded_action_names=[]
        )
        self.task_demo = self.context_processor.task_example_to_str(
            example_question=example_question, example_trajectory=example_trajectory
        )
        if self.add_task_demo:
            self.act_prompt_template = "\n\n".join(
                [
                    self.act_prompt_template,
                    self.task_demo,
                    'Now give your output starting with "Thought:".',
                ]
            )

        logger.info("Fully Autonomous Agent started.")

    def get_action(self, observation: Dict, chat_history: list):
        """Get the next action from the agent.

        This function will be called by collaborative_gym.nodes_agent_interface when the node receives a new observation from
        the environment.
        """
        # Update the scratchpad
        scratchpad_update_prompt = self.format_update_scratchpad_prompt(obs=observation)
        scratchpad_update_prompt_response = self.lm(
            prompt=scratchpad_update_prompt, temperature=0, max_tokens=4000
        )
        scratchpad_update = scratchpad_update_prompt_response[0].strip()
        scratchpad_update = scratchpad_update[
            scratchpad_update.find("Action:") + len("Action:") :
        ].strip()
        self.scratchpad.execute_action(scratchpad_update)

        # Take the next action
        if len(chat_history) > 0:
            observation["environment_message"] = [c["message"] for c in chat_history]
        act_prompt = self.format_act_prompt(
            obs=observation,
            action_space_description=self.task_action_space_description,
        )
        act_prompt_response = self.lm(prompt=act_prompt, temperature=0, max_tokens=4000)
        action = act_prompt_response[0].strip()
        action = action[action.find("Action:") + len("Action:") :].strip()
        # Hacky post-processing:
        # Assume the action is in a function call format and the function name starts with a capital letter.
        if "\nThought:" in action:
            action = action[: action.find("\nThought:")].strip()
        match = re.search(r"[A-Z]", action)
        if match:
            action = action[match.start() :]
        if action[-1] != ")":
            action = action[: action.rfind(")") + 1]
        action = action.replace("\(", "(").replace("\)", ")")

        # Claude tend to generate code that leads to syntax error in jupyter notebook
        # Handle notebook code transformations
        action = action.replace('print("\n', 'print("').replace('print("\\n', 'print("')

        logger.info(f"Fully Autonomous Agent action: {action}")
        self.action_history.append(action)

        return action

    def end(self, result_dir: str):
        os.makedirs(os.path.join(result_dir, self.name), exist_ok=True)
        with open(os.path.join(result_dir, self.name, "info.json"), "w") as f:
            info = {
                "lm": self.lm.model,
                "token_usage": self.get_token_usage(),
            }
            json.dump(info, f, indent=4)
        with open(os.path.join(result_dir, self.name, "scratchpad.json"), "w") as f:
            json.dump(self.scratchpad.notes, f, indent=4)
        with open(
            os.path.join(result_dir, self.name, "llm_call_history.jsonl"), "w"
        ) as f:
            for call in self.lm.history:
                f.write(
                    json.dumps({"prompt": call["prompt"], "response": call["response"]})
                    + "\n"
                )
        logger.info("Fully Autonomous Agent ended.")

    def get_token_usage(self):
        return {
            "prompt_tokens": self.lm.prompt_tokens,
            "completion_tokens": self.lm.completion_tokens,
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-name",
        type=str,
        default="gpt-4o-2024-08-06",
        help="We use LiteLLM to dispatch the request to the correct model."
        "Please ensure the model name matches the naming convention in LiteLLM."
        "https://docs.litellm.ai/docs/providers",
    )
    parser.add_argument(
        "--wait-time",
        type=int,
        default=5,
        help="Time to wait for the agent to respond. This is useful when coordinating with human.",
    )
    parser.add_argument("--node-name", type=str, required=True)
    parser.add_argument("--env-uuid", type=str, required=True)
    parser.add_argument("--redis-url", type=str, default="redis://localhost:6379/0")
    parser.add_argument("--add-task-demo", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    secrets = toml.load("secrets.toml")
    for k in secrets:
        os.environ[k] = secrets[k]

    lm_kwargs = prepare_lm_kwargs(args.model_name)
    lm = LitellmModel(**lm_kwargs)

    if args.debug:
        agent = ReactAutoAgent(
            lm=lm, add_task_demo=args.add_task_demo, prompt_path=args.prompt_path
        )

        import pdb

        pdb.set_trace()
    else:
        _sync_run_node(
            NodeConfig(
                node_name=args.node_name,
                node_class="agent",
                node_args=NodeArgs(
                    env_uuid=args.env_uuid,
                    node_name=args.node_name,
                    agent=ReactAutoAgent(
                        lm=lm,
                        add_task_demo=args.add_task_demo,
                        prompt_path=args.prompt_path,
                    ),
                    wait_time=args.wait_time,
                ),
            ),
            args.redis_url,
        )
