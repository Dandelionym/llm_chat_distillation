import json
import os
import time
import openai
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"
# If you use Clash for Windows, please do not remove above proxy.

class Bot:
    """
        A bot that can collect conversations from API with prompts and fixed task size and contents.
        Usage:
            1. Automatically refine the source text data.
            2. Create training sets from OpenAI API Key.
    """
    def __init__(self, api_key, gpt_model_type, task_target_lst, submit_dir, temperature, prompt_Instruction, prompt_Follow, submit_filename="", name=None, max_attmp=10):
        self.api_key = api_key
        openai.api_key = api_key
        self.BOTNAME = name
        self.task = task_target_lst
        self.TEMPERATURE = temperature
        self.model = gpt_model_type
        self.submit_target = os.path.join(submit_dir, submit_filename)
        self.prompt_Instruction = prompt_Instruction
        self.prompt_Following = prompt_Follow
        self.max_attmp = max_attmp

    def work(self):
        for i, text_qa_obj in enumerate(self.task):
                print(f"============================== Operate Source Text {self.BOTNAME} [{i}/{len(self.task)}] ==============================\n{text_qa_obj[0:120]}")
                time.sleep(20.5)    # for 5$ Key, which has the rate limitation.

                # Return 1
                reply_q = None
                num_attempt = 1
                while not reply_q:
                    try:
                        messages = [{"role": "user", "content": self.prompt_Instruction + f"{text_qa_obj}"}]
                        reply_q = openai.ChatCompletion.create(model=self.model, messages=messages, temperature=self.TEMPERATURE)['choices'][0]['message']['content']
                    except Exception as E:
                        print("[Retrying...] ", E)
                        num_attempt += 1
                        time.sleep(num_attempt)
                    finally:
                        if not reply_q and num_attempt > self.max_attmp:
                            exit(7)

                print(f"+-----++-----++-----++-----+ First Turbo Reply [{i}/{len(self.task)}] +-----++-----++-----++-----+\n{reply_q}")
                time.sleep(20.5)    # for 5$ Key, which has the rate limitation.

                # Return 2
                reply_a = None
                num_attempt = 1
                while not reply_a:
                    try:
                        messages = [{"role": "user", "content": self.prompt_Following + f"{reply_q}"}]
                        reply_a = openai.ChatCompletion.create(model=self.model, messages=messages, temperature=self.TEMPERATURE)['choices'][0]['message']['content']
                    except Exception as E:
                        print("[Retrying...] ", E)
                        num_attempt += 1
                        time.sleep(num_attempt)
                    finally:
                        if not reply_a and num_attempt > self.max_attmp:
                            exit(8)

                print(f"+-----++-----++-----++-----+ Second Turbo Reply [{i}/{len(self.task)}] +-----++-----++-----++-----+\n{reply_q}")

                # Gather Infomation
                with open(self.submit_target, encoding='utf-8', mode='a') as j:
                    j.write(f"##### Extracted: \n {str(reply_q)} \n ##### AnalysisOnText: \n {str(reply_a)} #####" + "\n\n###LINE###\n\n")


RANDOM_SEED = 98797645
WORK_DIR = '../data'
TAREGT_LABEL_OR_SOURCE_JSONFILE_NAME = "target_0.json"      # The input data, please reformat the source data with the style of the 'text_only' provided by LMFlow.
GROUP_OR_ROBOT_NUM = 2  # Only for miltiple settings.
API_KEY_LIST = [
    "sk-...",
    "sk-...",
]  # Note that this script only support one robot settings, if you need multiple robots, you need to use multi-thread by modifying the code.

# Prompt for instruction, such as: let the model ask a question on this text or reformat the text with the specific style.
PROMPT_INSTRUCTION = """
        I want you to act as a highly intelligent and experienced .... You should adaptively adopt the skills of ..., including:

        1. ...
        2. ...
        3. ...

            The ... problem is that ... \n\n To ..., the key insights are ...

        You should be full of conviction, intelligence, enthusiasm and truth-seeking with your strong divergent thinking, strong systematic thinking and high-quality logical thinking, you should only give me the  refined text without any other explanation: 

        """

# Prompt for usage of the refined text, such as answering the question proposed by the first prompt (the result of the prompt request).
PROMPT_FOLLOWING = """
        I want you to act as a ...

        You should ...

        You are full of conviction, intelligence, enthusiasm and truth-seeking with your strong divergent thinking, strong systematic thinking and high-quality logical thinking, you should ... 

        Now I give you the ..., I need you to tell me:
        1. ...
        2. ...
        3. ...
        
        Here is an example:
            ...

        
        You should answer these questions step-by-step and detail-by-detail, you should give me the ... with a standard table form, make it precise into the detail, and you may need to seek more ... and then answer them detail-by-detail and hit the nail on the head, the given ... is:   
        
        """

if __name__ == '__main__':
    import random
    random.seed(RANDOM_SEED)

    def create_equal_groups(ls, k):
        n = len(ls)
        size = n // k
        return [ls[i:i + size] for i in range(0, n, size)]

    # Load all source data.
    ALL_DATA, ALL_TASK_SOURCE_ITEM = [], []
    robots_or_task_num = 1
    for abs_path in [os.path.join(WORK_DIR, _) for _ in os.listdir(WORK_DIR)]:
        if TAREGT_LABEL_OR_SOURCE_JSONFILE_NAME in abs_path:
            with open(abs_path, mode='r', encoding='utf-8') as f:
                data = json.load(f)['instances']
                ALL_DATA += data

    ALL_DATA = [_['text'] for _ in ALL_DATA]
    GROUPS = create_equal_groups(ALL_DATA, GROUP_OR_ROBOT_NUM)

    # Create tasks in group level.
    for task in GROUPS:
        for idx, text_obj in enumerate(task):
            text_i = text_obj.split(" \n ")[0].strip()
            ALL_TASK_SOURCE_ITEM.append((text_i, ))

    EACH_ROBOT_SOURCE = []

    for robot_id in range(GROUP_OR_ROBOT_NUM):
        EACH_ROBOT_SOURCE = []
        num_per_robot = int(len(ALL_TASK_SOURCE_ITEM) / GROUP_OR_ROBOT_NUM)

        while len(ALL_TASK_SOURCE_ITEM) > 1 and len(EACH_ROBOT_SOURCE) < num_per_robot:
            io_tuple = random.choice(ALL_TASK_SOURCE_ITEM)
            ALL_TASK_SOURCE_ITEM.remove(io_tuple)
            EACH_ROBOT_SOURCE.append(io_tuple)
            num_per_robot += 1

        Bot(
            api_key=API_KEY_LIST[robot_id],
            gpt_model_type="gpt-3.5-turbo",
            task_target_lst=EACH_ROBOT_SOURCE,
            submit_dir=f"../data_submit",
            submit_filename=f"robot{robot_id}.txt",
            temperature=0.89,
            prompt_Instruction=PROMPT_INSTRUCTION,
            prompt_Follow=PROMPT_FOLLOWING,
            name= f" Robot-{str(robot_id)} "
        ).work()
        print(f"Bot {robot_id} is working...")