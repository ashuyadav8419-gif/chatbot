from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class ChatPipeline:
    def __init__(self, system_prompt, model_name="gemini-3.8-flash", window=20):
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.window = window
        self._model = None  # built lazily, never pickled

    def __getstate__(self):
        state = self.__dict__.copy()
        state["_model"] = None
        return state

    @property
    def model(self):
        if self._model is None:
            self._model = ChatGoogleGenerativeAI(model=self.model_name)
        return self._model

    @staticmethod
    def _text(msg):
        c = msg.content
        if isinstance(c, str):
            return c
        return "".join(b.get("text", "") for b in c if isinstance(b, dict))

    def run(self, user_input, history=None):
        """history: list of {"role": "user"|"ai", "text": str}. Returns (reply, new_history)."""
        history = list(history or [])
        history.append({"role": "user", "text": user_input})

        msgs = [SystemMessage(self.system_prompt)]
        for m in history[-self.window:]:
            msgs.append(HumanMessage(m["text"]) if m["role"] == "user" else AIMessage(m["text"]))

        reply = self._text(self.model.invoke(msgs))
        history.append({"role": "ai", "text": reply})
        return reply, history
    