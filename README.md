# llm_chat_distillation
A project to collect chat data with OpenAI API automatically.

# Advantages
- Most easy to use.
- Quick start.
- High flexibility.

# How to use
1. Download the code： `git clone https://github.com/Dandelionym/llm_chat_distillation`.
2. Set up your network, check if you can open ChatGPT website on your browser.
3. Modify the prompts and the source data path (a json file, which is simialr to the `text_only` training data on LMFlow).
4. Copy `data_workers/2_template.py` into a new python file, rename it (robot_1.py as case).
5. Create a folder on the base dir, which is the same level with README.md, named with `data_submit`.
6. Run the code in `data_workers/robot_1.py`
7. The generated text will be saved at the `data_submit` folder, then you can split the text with specific signals, as shown in this line: 
```
j.write(f"##### Extracted: \n {str(reply_q)} \n ##### AnalysisOnText: \n {str(reply_a)} #####" + "\n\n###LINE###\n\n")
```

# Contribute or Support
If you find this repo useful, the star is really welcome!
