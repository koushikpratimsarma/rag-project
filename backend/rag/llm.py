from backend.config import settings


def get_llm():
    if settings.llm_provider == "openai" and settings.openai_api_key:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.openai_model,
            openai_api_key=settings.openai_api_key,
            temperature=0.2,
        )

    from langchain_community.llms import HuggingFacePipeline
    from transformers import pipeline

    pipe = pipeline(
        "text2text-generation",
        model=settings.local_generation_model,
        max_length=256,
    )

    return HuggingFacePipeline(pipeline=pipe)