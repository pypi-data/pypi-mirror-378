import logging
from typing import Any, Callable

from Mama.config import Configuration

# LangChain imports (updated for >= 0.2)
try:
    from langchain_openai import ChatOpenAI  # type: ignore
except Exception:  # pragma: no cover - allow tests without OpenAI
    ChatOpenAI = None  # type: ignore

try:
    from langchain.chains.combine_documents.stuff import StuffDocumentsChain  # type: ignore
    from langchain.chains.llm import LLMChain  # type: ignore
except Exception:  # Backward/optional compatibility
    StuffDocumentsChain = None  # type: ignore
    LLMChain = None  # type: ignore

try:
    from langchain_core.prompts import PromptTemplate  # type: ignore
except Exception:  # pragma: no cover
    from langchain.prompts import PromptTemplate  # type: ignore

try:
    from langchain_core.runnables import RunnableLambda  # type: ignore
except Exception:
    RunnableLambda = None  # type: ignore

class cbLLM:
    def __init__(self):
        self.llm = None
        try:
            self._load()
        except Exception as e:
            logging.info("Error Loading LLM from configuration")
    
    def get_llm(self) :
        return self.llm
    
    def load_QueryChain(self, prompt) -> Any:
        if not self.llm or not StuffDocumentsChain or not LLMChain:
            return None  # type: ignore
        
        # This controls how each document will be formatted. Specifically,
        # it will be passed to `format_document` - see that function for more
        # details.
        document_prompt = PromptTemplate(
            input_variables=["page_content"],
            template="{page_content}"
        )

        # The prompt here should take as an input variable the
        # `document_variable_name`
        prompt = PromptTemplate.from_template(
            "Summarize this content: {context}"
        )
        document_variable_name = "context"
        
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)

        chain = StuffDocumentsChain(
            llm_chain=llm_chain,
            document_prompt=document_prompt,
            document_variable_name=document_variable_name
        )
        return chain
    
    def _load(self) :
        # Supported models
        llms = {
            "OpenAi": ChatOpenAI,
            "Dummy": "Dummy",
        }
        config = Configuration()
        if not config:
            logging.info("Error Loading Configuration")
            return None
        
        model = config.get("model")
        if not model:
            logging.info("No LLM model found")
            return None

        llm_class = llms.get(model, None)
        if not llm_class:
            logging.info(f"model {model} not yet implemented!")
            return None
        
        params = config.get_llm_params(model)
        if model == "Dummy":
            # Fallback deterministic LLM for offline tests
            def _dummy_fn(prompt: Any) -> str:
                try:
                    # LangChain may pass a PromptValue
                    if hasattr(prompt, "to_string"):
                        prompt = prompt.to_string()  # type: ignore
                    prompt_str = str(prompt)

                    context = ""
                    question = ""

                    lower = prompt_str.lower()
                    ctx_key = "contesto:"
                    q_key = "domanda:"
                    if ctx_key in lower and q_key in lower:
                        start = lower.index(ctx_key) + len(ctx_key)
                        end = lower.index(q_key, start)
                        context = prompt_str[start:end].strip()
                        # Extract question after q_key
                        q_start = lower.index(q_key, end) + len(q_key)
                        question = prompt_str[q_start:].splitlines()[0].strip()

                    if not context:
                        context = prompt_str.strip()

                    summary = context.replace("\n", " ")
                    if len(summary) > 320:
                        summary = summary[:317].rsplit(" ", 1)[0] + "..."

                    if question:
                        return (
                            "[DUMMY-LLM] Risposta deterministica:\n"
                            f"Domanda: {question}\n"
                            f"Sintesi: {summary}"
                        )
                    return f"[DUMMY-LLM] Sintesi: {summary}"
                except Exception:
                    return "[DUMMY-LLM] Risposta generata."

            if RunnableLambda:
                self.llm = RunnableLambda(lambda x: _dummy_fn(x))  # type: ignore
            else:  # Very old LC versions
                self.llm = lambda x: _dummy_fn(x)  # type: ignore
        else:
            if ChatOpenAI is None:
                logging.info("OpenAI provider not available. Falling back to Dummy.")
                if RunnableLambda:
                    self.llm = RunnableLambda(lambda x: "[DUMMY-LLM] OpenAI not available")  # type: ignore
                else:
                    self.llm = lambda x: "[DUMMY-LLM] OpenAI not available"  # type: ignore
            else:
                self.llm = llm_class(**params)  # type: ignore

        self.prompt_template = config.get_prompt_template()
        self.input_variables = config.get_input_variables()

    def get_prompt_template(self):
        return self.prompt_template
    
    def get_input_variables(self):
        return self.input_variables
            
    '''model_name: str = Field("text-davinci-003", alias="model")
    """Model name to use."""
    temperature: float = 0.7
    """What sampling temperature to use."""
    max_tokens: int = 256
    """The maximum number of tokens to generate in the completion.
    -1 returns as many tokens as possible given the prompt and
    the models maximal context size."""
    top_p: float = 1
    """Total probability mass of tokens to consider at each step."""
    frequency_penalty: float = 0
    """Penalizes repeated tokens according to frequency."""
    presence_penalty: float = 0
    """Penalizes repeated tokens."""
    n: int = 1
    """How many completions to generate for each prompt."""
    best_of: int = 1
    """Generates best_of completions server-side and returns the "best"."""
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Holds any model parameters valid for `create` call not explicitly specified."""
    openai_api_key: Optional[str] = None
    openai_api_base: Optional[str] = None
    openai_organization: Optional[str] = None
    # to support explicit proxy for OpenAI
    openai_proxy: Optional[str] = None
    batch_size: int = 20
    """Batch size to use when passing multiple documents to generate."""
    request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    """Timeout for requests to OpenAI completion API. Default is 600 seconds."""
    logit_bias: Optional[Dict[str, float]] = Field(default_factory=dict)
    """Adjust the probability of specific tokens being generated."""
    max_retries: int = 6
    """Maximum number of retries to make when generating."""
    streaming: bool = False
    """Whether to stream the results or not."""
    allowed_special: Union[Literal["all"], AbstractSet[str]] = set()
    """Set of special tokens that are allowed。"""
    disallowed_special: Union[Literal["all"], Collection[str]] = "all"
    """Set of special tokens that are not allowed。"""
    tiktoken_model_name: Optional[str] = None'''
