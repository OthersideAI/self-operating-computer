# Contributing
We appreciate your contributions!

## Process
1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

## Modifying and Running Code
1. Make changes in `operate/main.py`
2. Run `pip install .` again
3. Run `operate` to see your changes

## Testing Changes
**After making significant changes, it's important to verify that SOC can still successfully perform a set of common test cases.**
In the root directory of the project, run:
```
python3 evaluate.py
```   
This will automatically prompt `operate` to perform several simple objectives.   
Upon completion of each objective, GPT-4v will give an evaluation and determine if the objective was successfully reached.   

`evaluate.py` will print out if each test case `[PASSED]` or `[FAILED]`. In addition, a justification will be given on why the pass/fail was given.   

It is recommended that a screenshot of the `evaluate.py` output is included in any PR which could impact the performance of SOC.

## Contribution Ideas
- **Improve performance by finding optimal screenshot grid**: A primary element of the framework is that it overlays a percentage grid on the screenshot which GPT-4v uses to estimate click locations. If someone is able to find the optimal grid and some evaluation metrics to confirm it is an improvement on the current method then we will merge that PR. 
- **Improve the `SUMMARY_PROMPT`**
- **Improve Linux and Windows compatibility**: There are still some issues with Linux and Windows compatibility. PRs to fix the issues are encouraged. 
- **Adding New Multimodal Models**: Integration of new multimodal models is welcomed. If you have a specific model in mind that you believe would be a valuable addition, please feel free to integrate it and submit a PR.
- **Iterate `--accurate` flag functionality**: Look at https://github.com/OthersideAI/self-operating-computer/pull/57 for previous iteration
- **Enhanced Security**: A feature request to implement a _robust security feature_ that prompts users for _confirmation before executing potentially harmful actions_. This feature aims to _prevent unintended actions_ and _safeguard user data_ as mentioned here in this [OtherSide#25](https://github.com/OthersideAI/self-operating-computer/issues/25)


## Guidelines
This will primarily be a [Software 2.0](https://karpathy.medium.com/software-2-0-a64152b37c35) project. For this reason: 

- Let's try to hold off refactors into separate files until `main.py` is more than 1000 lines

