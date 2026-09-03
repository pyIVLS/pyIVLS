from LLM.LLM_Aalto import LLM_Aalto


class pyIVLS_LLM:
    """pyIVLS-specific LLM facade.

    ANT uses this class and does not need to know which LLM provider
    is used underneath.
    """

    def __init__(self, model=None):
        self.llm = LLM_Aalto(model=model)

    def send(self, messages):
        return self.llm.send(messages)

    def reset(self):
        return self.llm.reset()
