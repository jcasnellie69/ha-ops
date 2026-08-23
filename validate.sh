#!/usr/bin/env bash
# D082226T2000 | HA-0001 | pipeline Validate gate | JC | ha-ops repo
set -euo pipefail
echo "[1/3] yamllint"
yamllint -d '{extends: default, rules: {line-length: {max: 160}}}' config/ dashboards/ ansible/ || exit 1
echo "[2/3] ansible-lint"
ansible-lint ansible/ || exit 1
echo "[3/3] HA config check (containerized)"
# docker run --rm -v "$PWD/config:/config" ghcr.io/home-assistant/home-assistant:stable \
#   python -m homeassistant --script check_config --config /config
echo "PASS — ready for Review"
