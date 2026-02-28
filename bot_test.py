# Project: Epic Games Notifier | Author: https://github.com/pavnxet/Epic-Free-Games-Telegram-Bot
import pytest
import asyncio
from bot import fetch_free_games, load_json_file, escape_markdown

@pytest.mark.asyncio
async def test_fetch_free_games():
    games = await fetch_free_games()
    assert isinstance(games, list)
    for game in games:
        assert 'id' in game
        assert 'title' in game
        assert 'url' in game
        assert 'image' in game

@pytest.mark.asyncio
async def test_load_json_file():
    data = await load_json_file("nonexistent.json")
    assert data == []

def test_escape_markdown():
    text = "Hello _World_ *[Link]* (here) ~strike~ `code` >quote #hash +add -sub =eq |pipe {brace} .dot !bang"
    escaped = escape_markdown(text)
    assert "\\_" in escaped
    assert "\\*" in escaped
    assert "\\[" in escaped
    assert "\\]" in escaped
    assert "\\(" in escaped
    assert "\\)" in escaped
    assert "\\~" in escaped
    assert "\\`" in escaped
    assert "\\>" in escaped
    assert "\\#" in escaped
    assert "\\+" in escaped
    assert "\\-" in escaped
    assert "\\=" in escaped
    assert "\\|" in escaped
    assert "\\{" in escaped
    assert "\\}" in escaped
    assert "\\." in escaped
    assert "\\!" in escaped
