<p align="left">
  <img width="90%" src="https://gblobscdn.gitbook.com/assets%2F-MJDKltt3A57jhixTfmu%2F-MJZZeY9BhUCtGPyz6bm%2F-MJZiXHTjQnyVWs6YGPc%2Frasgo-logo-full-color-rgb%20(4).png?alt=media&token=64e56b18-4282-4140-836b-e19c8e2787dc" />
</p>

[![Downloads](https://pepy.tech/badge/pyrasgo)](https://pepy.tech/project/pyrasgo)
[![PyPI version](https://badge.fury.io/py/pyrasgo.svg)](https://badge.fury.io/py/pyrasgo)
[![Docs](https://img.shields.io/badge/PyRasgo-DOCS-GREEN.svg)](https://docs.rasgoml.com/)
[![Chat on Slack](https://img.shields.io/badge/chat-on%20Slack-brightgreen.svg)](https://join.slack.com/t/rasgousergroup/shared_invite/zt-nytkq6np-ANEJvbUSbT2Gkvc8JICp3g)
[![Chat on Discourse](https://img.shields.io/discourse/status?server=https%3A%2F%2Fforum.rasgoml.com)](https://forum.rasgoml.com/)


# PyRasgo
<i>Built for Data Scientists, by Data Scientists</i>

# Introduction
PyRasgo helps users build features faster, collaborate with team members, and serve features to models in production.

# Tutorial
<a href="https://github.com/rasgointelligence/PyRasgo/blob/main/tutorials/PyRasgo%20Tutorial.ipynb">Click Here</a> to try PyRasgo yourself on your own dataframe.

# Quick Start
```
    pip install pyrasgo[df]
    
    #register for and retrieve your rasgo api key
    pyrasgo.register(email="fred@flinstone.com", password="")
    rasgo = pyrasgo.login(email="fred@flinstone.com", password="")
    
    #activate an experiment and begin evaluating your features
    rasgo.activate_experiment('my_first_experiment')
    rasgo.evaluate.feature_importance(df, target_column='Name_of_target_column_in_df')

```
