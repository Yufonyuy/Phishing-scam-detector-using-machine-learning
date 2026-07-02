# 14-Day Competition Sprint Plan

## Team roles

- Data/preprocessing lead
- Modeling lead
- App/demo lead
- Pitch/visuals lead

## Day-by-day schedule

| Day | Focus | Deliverable |
|---:|---|---|
| 1 | Scope and planning | Decide 3-class vs 2-class, inspect dataset, assign roles, create folders |
| 2 | Data cleaning | Clean CSV while preserving URLs, phones, emails, message length |
| 3 | Baseline model | TF-IDF + Logistic Regression/SVM, metrics, saved pipeline |
| 4 | Feature engineering | Add URL/phone/email/length/punctuation/keyword features and compare |
| 5 | Explainability | Human-readable risk indicators for each prediction |
| 6 | App skeleton | Streamlit text box, submit button, result panel, saved model connection |
| 7 | App polish | Color cues, icons, warning panel, “why flagged” section |
| 8 | Local relevance | Cameroon English/French scam examples and failure analysis |
| 9 | Evaluation/testing | Structured test-set results and error review |
| 10 | Demo script | Three examples: safe, spam, smishing, under one minute each |
| 11 | Slide deck | Problem, data, model, demo, impact |
| 12 | Rehearsal | Full timed presentation and judge-question practice |
| 13 | Hardening | Freeze model, backup artifacts, clean-environment test, offline backup |
| 14 | Presentation | Short impact-focused pitch and live demo |

## Daily workflow

- Morning: review yesterday’s output and assign tasks
- Midday: build and integrate features
- Evening: test, document, and save artifacts

## Priority order if time is tight

1. Working model
2. Working Streamlit app
3. Explainability
4. Local examples
5. Slide polish
