# evalOfPASAbyChatGPT

## Overview

I evaluated the Japanese predicate argument structure analysis by using ChatGPT and Kyoto University Web Document Leads Corpus(KWLDLC). 
This repository contains the evaluation python scripts and python scripts for communicate with ChatGPT via openai api.

The evaluation details is reported in the following blog post (in Japanese).

https://meihuno.hatenablog.com/entry/2023/08/03/163316

## Existing Predicate arguments structure analysis results

The exisitng predicate argument structure analysis results which I conducted by using gpt-3.5-turbo-0301 is contained in ./ok_result_dev and ./ok_result_test. Also see AnaphoraResolutionbyUsingGPT3.ipynb.

These jsons has the following contents. The ChatGPT's response is contained in results dictionary's value indicated by the dictionary key such as ["f{id of document}"]["responce"]["content"]["choices"][0]["message"]["content"]. The ChatGPT's response is　written in table format.

```json
{
    "w201106-0000060050": {
        "status": "ok",
        "response": {
            "id": "dummy",
            "object": "chat.completion",
            "created": 1685858533,
            "model": "gpt-3.5-turbo-0301",
            "usage": {
                "prompt_tokens": 749,
                "completion_tokens": 164,
                "total_tokens": 913
            },
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "|文番号|述語|主語（ガ格）の候補|目的語（ヲ格）の候補|斜格の要素（ニ格）の候補|\n|---|---|---|---|---|\n|1|行う|不特定:人、俺たち、読者、著者|コイントス|-|\n|1|トス|不特定:人|コイン|-|\n|2|出た|表|-|-|\n|2|破壊する|不特定:状況|モンスター|-|\n|3|１度|-|-|ターン|\n|3|メイン|フェイズ|-|-|\n|3|使用する事ができる|不特定:人、著者、読者、俺たち|効果|フェイズ|"
                    },
                    "finish_reason": "stop",
                    "index": 0
                }
            ]
        },
        "phase": "dev"
    }
}
``` 

## Operationg Environment

### evaluation scripts（parse_knp_file.py/eval_conversation.py）
 Python 3.7.9 or later
### Predicate arguments structure analysis by using ChatGPT(AnaphoraResolutionbyUsingGPT3.ipynb)
 Google Colab

### Evaluation Corpus Preparation

Download KWDLC from https://github.com/ku-nlp/KWDLC in the root directory of the repository.

# How to Use
 1. Conduct the Japanese Predicate argument structure analysis in Google Colab （ See AnaphoraResolutionbyUsingGPT3.ipynb ）.
 2. Download the output jsons by ChatGPT into the root directory of the repository such as './ok_result_dev/'
 3. Making intermediate data from KWDLC to compare the correct results of KWDLC and the output jsons by ChatGPT.
``` 
parse_knp_file.py
```
Then intermediate data will be created into ./intermediate_data/

 4. Show F1 scores and comparing examples(input sentences, correct results by KWDLC, ChatGPT's responses)

```
pyhon eval_conversation.py
```
Then F1 scores will be showed in the terminal.

# How to conduct unit tests

If you change the evaluation scripts, then you should re-make the intermediate-date for unit test by the following command.

``` 
python parse_knp_file.py -p test_data
```

Then you can counduct unit test in the following commands.

``` 
python -m unittest discover -s ./test -p test_parse_knp_file.py
python -m unittest discover -s ./test -p test_eval_conversation.py
``` 


