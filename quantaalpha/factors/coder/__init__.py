import os

from quantaalpha.coder.costeer import CoSTEER
from quantaalpha.coder.costeer.evaluators import CoSTEERMultiEvaluator
from quantaalpha.factors.coder.config import FACTOR_COSTEER_SETTINGS
from quantaalpha.factors.coder.evaluators import FactorEvaluatorForCoder
from quantaalpha.factors.coder.evolving_strategy import (
    FactorMultiProcessEvolvingStrategy, FactorParsingStrategy, FactorRunningStrategy
)
from quantaalpha.core.scenario import Scenario


def _rag_disabled() -> bool:
    return os.environ.get("QA_DISABLE_COSTEER_RAG", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


class FactorCoSTEER(CoSTEER):
    def __init__(
        self,
        scen: Scenario,
        *args,
        **kwargs,
    ) -> None:
        setting = FACTOR_COSTEER_SETTINGS
        eva = CoSTEERMultiEvaluator(FactorEvaluatorForCoder(scen=scen), scen=scen)
        es = FactorMultiProcessEvolvingStrategy(scen=scen, settings=FACTOR_COSTEER_SETTINGS)

        if _rag_disabled():
            kwargs.setdefault("with_knowledge", False)
            kwargs.setdefault("knowledge_self_gen", False)
        super().__init__(*args, settings=setting, eva=eva, es=es, evolving_version=2, scen=scen, **kwargs)
        


class FactorParser(CoSTEER):
    def __init__(
        self,
        scen: Scenario,
        *args,
        **kwargs,
    ) -> None:
        setting = FACTOR_COSTEER_SETTINGS
        eva = CoSTEERMultiEvaluator(FactorEvaluatorForCoder(scen=scen), scen=scen)
        es = FactorParsingStrategy(scen=scen, settings=FACTOR_COSTEER_SETTINGS)

        if _rag_disabled():
            kwargs.setdefault("with_knowledge", False)
            kwargs.setdefault("knowledge_self_gen", False)
        super().__init__(*args, settings=setting, eva=eva, es=es, evolving_version=2, scen=scen, **kwargs)
        
        
class FactorCoder(CoSTEER):
    def __init__(
        self,
        scen: Scenario,
        *args,
        **kwargs,
    ) -> None:
        setting = FACTOR_COSTEER_SETTINGS
        eva = CoSTEERMultiEvaluator(FactorEvaluatorForCoder(scen=scen), scen=scen)
        es = FactorRunningStrategy(scen=scen, settings=FACTOR_COSTEER_SETTINGS)

        if _rag_disabled():
            kwargs.setdefault("with_knowledge", False)
            kwargs.setdefault("knowledge_self_gen", False)
        super().__init__(*args, settings=setting, eva=eva, es=es, evolving_version=2, scen=scen, **kwargs)
