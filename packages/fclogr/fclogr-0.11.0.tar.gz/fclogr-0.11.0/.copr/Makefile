# Copyright (C) 2025 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later OR MIT

outdir ::= results_fclogr

srpm:
	command -v pip || $(SUDO) dnf install -y python3-pip
	command -v fclogr || $(SUDO) dnf install -y python3-pygit2 python3-rpm
	command -v fclogr || pip install --user .
	command -v nox || $(SUDO) dnf install -y nox
	python3 -m nox --no-venv -e srpm -- -o $(outdir)
