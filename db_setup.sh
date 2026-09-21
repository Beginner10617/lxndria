#!/bin/zsh
python -m flask db migrate -m "Initial migration"
python -m flask db upgrade
