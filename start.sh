#!/bin/bash
source `pwd`/front/venv/bin/activate
cd front && python3.12 -m streamlit run app.py