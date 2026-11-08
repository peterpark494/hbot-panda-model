# Panda six-task model (20000 updates)

Download the model from [Releases](https://github.com/peterpark494/hbot-panda-model/releases/tag/panda-20k-v1).

The model is split into four assets; download all four parts plus `manifest.json`
and `merge_model_parts.py`, then run `python merge_model_parts.py`.

See [DEPLOYMENT.md](DEPLOYMENT.md) for Chinese download and deployment instructions.
The bundle includes weights and model resources, but no training dataset, simulator image or scene assets.

Training completed 20000 optimizer updates. One stack-cubes evaluation (seed 100000,
900 steps) completed without a process crash but scored **0**: task not completed.
No six-task success rate is claimed.

Third-party code and model resources retain their upstream license terms.
