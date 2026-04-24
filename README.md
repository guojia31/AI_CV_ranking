# 🤖 AI Resume Screening System

## Overview

An AI-powered system that ranks candidates based on a job description using:

* LLM-based information extraction
* Rule-based scoring engine
* Multi-format resume support (PDF / DOCX / CSV / TXT)

---

## Features

* 📄 Upload resumes (PDF / DOCX / CSV / TXT)
* 🧠 AI extracts skills, experience, domain
* ⚖️ Deterministic ranking (stable, no LLM scoring)
* 📊 Explainable results with scores

---

## Architecture

Frontend → Flask API → Parser → LLM Extractor → Ranking Engine → Results

---

## Tech Stack

* Flask + Gunicorn
* Python
* Doubao LLM API
* PyPDF2 / python-docx / pandas
* Vanilla JS frontend


