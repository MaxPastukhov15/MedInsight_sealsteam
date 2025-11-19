"""Smoke test for all requirements imports.

Этот тест проверяет, что все зависимости из requirements.txt действительно устанавливаются,
импортируются без ошибок и не имеют проблем с shared libraries (so/dll) на системе.
Можно запускать при любом изменении requirements.txt, пригодится для CI и локальной проверки.
"""


def test_imports_smoke():
    import asyncpg
    import black
    import chromadb
    import cmdstanpy
    import fastapi
    import flake8
    import hiredis
    import hnswlib
    import httpx
    import isort
    import langchain
    import langgraph
    import matplotlib
    import mypy
    import numpy
    import pandas
    import plotly
    import pre_commit
    import prometheus_client
    import prophet
    import pydantic
    import pydantic_settings
    import pytest
    import pythonjsonlogger
    import redis
    import scipy
    import sentence_transformers
    import sklearn
    import sqlalchemy
    import statsmodels
    import structlog
    import uvicorn
