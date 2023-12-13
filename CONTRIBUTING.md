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
3. Run `operate` to test your changes

## Contribution Ideas
- **Improve performance by finding optimal screenshot grid**: A primary element of the framework is that it overlays a percentage grid on the screenshot which GPT-4v uses to estimate click locations. If someone is able to find the optimal grid and some evaluation metrics to confirm it is an improvement on the current method then we will merge that PR. 
- **Improve the `SUMMARY_PROMPT`**
- **Improve Linux and Windows compatibility**: There are still some issues with Linux and Windows compatibility. PRs to fix the issues are encouraged. 
- **Adding New Multimodal Models**: Integration of new multimodal models is welcomed. If you have a specific model in mind that you believe would be a valuable addition, please feel free to integrate it and submit a PR.
- **Iterate `--accurate` flag functionality**: Look at https://github.com/OthersideAI/self-operating-computer/pull/57 for previous iteration

## Guidelines
This will primarily be a [Software 2.0](https://karpathy.medium.com/software-2-0-a64152b37c35) project. For this reason: 

- Let's try to hold off refactors into separate files until `main.py` is more than 1000 lines

