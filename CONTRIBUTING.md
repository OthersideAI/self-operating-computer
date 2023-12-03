# Contributing
We appreciate your contributions!

## Process
1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

## Contribution ideas
- **Improve performance by finding optimal screenshot grid**: A primary element of the framework is that it overlays a percentage grid on the screenshot which GPT-4v uses to estimate click locations. If someone is able to find the optimal grid and some evaluation metrics to confirm it is an improvement on the current method then we will merge that PR. 
- **Improve the `SUMMARY_PROMPT`**
- **Create an evaluation system**
- **Improve Linux and Windows compatibility**: There are still some issues with Linux and Windows compatibility. PRs to fix the issues are encouraged. 
- **Enabling New Mouse Capabilities**: (drag, hover, etc.)
- **Adding New Multimodal Models**: Integration of new multimodal models is welcomed. If you have a specific model in mind that you believe would be a valuable addition, please feel free to integrate it and submit a PR.
- **Framework Architecture Improvements**: Think you can enhance the framework architecture described in the intro? We welcome suggestions and PRs.
- **Remove necessity for `pip install .`**: I think by uploading packages to PyPi we can reduce the installation code steps by consolidating `pip install -r requirements.txt` and `pip install .`. If that's possible that'd be great. 

## Guidelines
This will primarily be a [Software 2.0](https://karpathy.medium.com/software-2-0-a64152b37c35) project. For this reason: 

- Let's try to hold off refactors into separate files until `main.py` is more than 1000 lines

