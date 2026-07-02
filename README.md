# SMS Scam / Smishing Detector

A competition-ready Streamlit demo for detecting **ham**, **spam**, and **smishing/scam** SMS messages with human-readable explanations.

## What it includes

- TF-IDF text model + Logistic Regression baseline
- Structural scam features: URL, phone, email, money, OTP/PIN words, urgency, reward/threat language, punctuation, length
- Explainability panel: shows why a message was flagged
- Cameroon-relevant English/French examples
- Evaluation snapshot with accuracy, precision, recall, F1, and confusion matrix
- Downloadable sample dataset

## Project structure

```text
sms_scam_detector/
├── app.py                    # Streamlit app
├── requirements.txt
├── data/sample_sms.csv        # starter dataset; replace with full competition data
├── models/                    # trained model + metrics are saved here
├── src/features.py            # feature extraction and explanations
├── src/train_model.py         # training script
└── docs/                      # sprint plan and demo script
```

## Quick start

```bash
cd sms_scam_detector
pip install -r requirements.txt
python src/train_model.py
streamlit run app.py
```

If `models/sms_detector.joblib` does not exist, the app trains it automatically on first launch.

## Replacing the dataset

Put your real dataset at:

```text
data/sample_sms.csv
```

Required columns:

- `text`: SMS content
- `label`: one of `ham`, `spam`, `smishing`

Then run:

```bash
python src/train_model.py
```

## Demo examples

Use these in the live pitch:

1. Safe: `Hi mum, I will be home by 6pm. Please keep dinner for me.`
2. Spam: `FREE airtime for all users this weekend. Text YES to 8080 for promo details.`
3. Smishing: `Orange Money account blocked. Verify immediately: https://om-secure-login.com`

## Important note

The included dataset is intentionally small so the project can run immediately. For a real competition submission, train and validate on a larger verified dataset such as the dataset referenced in the project brief, then test with local Cameroon English/French examples.

## Professional demo workflow

The app and deck now share the same generated analytics assets.

### 1. Train the model and regenerate plot assets

```bash
cd sms_scam_detector
python src/train_model.py
```

Training saves:

- `models/sms_detector.joblib`
- `models/metrics.json`
- latest plot images in `docs/assets/`

Generated plots include:

- `label_distribution.png`
- `risk_signal_prevalence.png`
- `confusion_matrix.png`
- `metrics_summary.png`
- `feature_profile.png`
- `risk_indicators.png`

### 2. Run the professional Streamlit interface

```bash
streamlit run app.py
```

The interface is responsive and includes:

- executive-style hero section;
- metric cards;
- polished prediction card;
- risk bar;
- class probabilities;
- explanation cards;
- latest training analytics tabs.

### 3. Regenerate the PowerPoint with the latest plots

```bash
python docs/make_winning_bilingual_deck.py
```

This updates:

```text
docs/CGIS_SMS_Scam_Detector_Winning_Bilingual.pptx
```

The deck embeds the newest images from `docs/assets`, so after retraining with a larger dataset, rerun the deck script before presenting.
