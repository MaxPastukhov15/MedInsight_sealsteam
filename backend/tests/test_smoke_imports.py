"""Smoke test for all requirements imports.

Этот тест проверяет, что все зависимости из requirements.txt действительно устанавливаются,
импортируются без ошибок и не имеют проблем с shared libraries (so/dll) на системе.
Можно запускать при любом изменении requirements.txt, пригодится для CI и локальной проверки.
"""

def test_imports_smoke():
    import fastapi
    import uvicorn
    import sqlalchemy
    import asyncpg
    import langchain
    import langgraph
    import chromadb
    import sentence_transformers
    import hnswlib
    import pandas
    import numpy
    import scipy
    import sklearn
    import statsmodels
    import plotly
    import prometheus_client
    import structlog
    import httpx
    import pytest
    import mypy
    import black
    import isort
    import flake8
    import pre_commit
    import pythonjsonlogger
    import prometheus_client
    import pydantic
    import pydantic_settings
    import cmdstanpy
    import matplotlib
    import prophet
    import redis
    import hiredis
