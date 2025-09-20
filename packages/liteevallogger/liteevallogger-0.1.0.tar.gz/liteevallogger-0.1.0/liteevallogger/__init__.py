import atexit
from weave import EvaluationLogger

class LiteEvalLogger:
    def __init__(self, model: str, dataset: str):
        self.ev = EvaluationLogger(model=model, dataset=dataset)
        self._done = False
        atexit.register(self._finalize)

    def log_example(self, inputs: dict, output: dict, scores: dict):
        if not isinstance(inputs, dict):
            raise TypeError("inputs must be a dict")
        if not isinstance(output, dict):
            raise TypeError("output must be a dict")
        if not isinstance(scores, dict):
            raise TypeError("scores must be a dict")

        pred = self.ev.log_prediction(inputs=inputs, output=output)
        for k, v in scores.items():
            pred.log_score(k, v)
        pred.finish()

    def _finalize(self):
        if self._done:
            return
        self._done = True
        self.ev.log_summary()
