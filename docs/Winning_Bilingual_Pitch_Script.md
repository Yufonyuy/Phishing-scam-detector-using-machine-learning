# Winning Bilingual Pitch Script — SMS Scam Detector

**Recommended timing:** 4–5 minutes pitch + 1 minute live demo.  
**Langue principale:** English. French lines can be used for emphasis or if the jury asks.

---

## 0:00–0:30 — Opening hook

**English:**
Good morning everyone. Our project is called **SMS Scam Detector**. We built an AI-powered and explainable tool that helps people detect SMS scams before they click a link, send money, or share a secret code.

This matters because SMS fraud is not just a technical problem. It is a daily problem for students, parents, small businesses and Mobile Money users.

**French backup:**
Notre objectif est simple: aider les utilisateurs à reconnaître un SMS dangereux avant qu’il ne soit trop tard.

---

## 0:30–1:10 — Problem

**English:**
Scam messages work because they exploit human behavior. They create fear: “your account is blocked.” They create reward: “you won a prize.” They imitate authority: banks, telecom operators, tax services. And they ask for fast action: click, call, send PIN, send OTP.

So the challenge is not only to classify messages. The challenge is to give users a clear reason they can understand immediately.

**French backup:**
Le vrai danger, c’est l’urgence et la confiance. Les fraudeurs veulent que l’utilisateur agisse sans réfléchir.

---

## 1:10–1:50 — Solution

**English:**
Our solution is a Streamlit web app. The user pastes an SMS. The system predicts one of three classes: safe or ham, spam, or smishing. It also shows a confidence score and a “why this was flagged” section.

For example, if a message contains a suspicious link, urgency, money context and a PIN request, the app explains each of these risk indicators in plain language.

**French backup:**
L’application ne donne pas seulement une prédiction. Elle explique les signes de risque: lien, urgence, demande de PIN, argent, numéro de téléphone.

---

## 1:50–2:40 — Technical approach

**English:**
Technically, we used a lightweight machine learning pipeline. First, we clean the text while preserving important scam signals such as URLs, phone numbers and punctuation. Then we use TF-IDF word and bigram features. We combine them with structural features: URL presence, phone presence, email presence, money words, urgency words, threat words, reward words, PIN or OTP indicators, length and punctuation.

The classifier is Logistic Regression with balanced classes. We chose it because it is fast, explainable, easy to retrain, and reliable for a hackathon demo even offline.

**French backup:**
Nous avons choisi un modèle léger et explicable, pas une boîte noire difficile à justifier devant le jury.

---

## 2:40–3:20 — Analytics and evaluation

**English:**
Our prototype dataset contains the three target classes: ham, spam and smishing. In our exploratory analysis, smishing messages show stronger combinations of risk signals, especially links, money context, urgency and credential requests.

On the current offline prototype dataset, the model reaches about 75% accuracy and 72% macro F1. More importantly, in the test split, the smishing examples were correctly identified. For the next version, our priority is to maximize smishing recall, because missing a scam is more dangerous than creating a false alarm.

**French backup:**
Notre priorité d’amélioration est le rappel sur les arnaques: rater une arnaque est plus grave qu’un faux avertissement.

---

## 3:20–4:10 — Live demo

**English:**
Now let’s test three messages.

1. Safe message: “Hi mum, I will be home by 6pm.” The app marks it as safe because there are no suspicious cues.
2. Spam message: “FREE airtime…” The app marks it as spam because it is promotional and action-oriented.
3. Smishing message: “Orange Money account blocked. Verify immediately…” The app marks it as smishing and explains: link, urgency, account pressure and money context.

This is the core value: the user understands not only the result, but the reason.

**French backup:**
La valeur principale est l’explication. L’utilisateur apprend à reconnaître les arnaques.

---

## 4:10–4:50 — Impact and roadmap

**English:**
This project fits CGIS because it combines science, technology, engineering, arts and mathematics with social impact. It is data science, it is product design, and it is cybersecurity education.

After the hackathon, we want to add a larger verified dataset, include more Cameroon-specific examples, improve French and English evaluation, and pilot the tool in a school club or CGIS workshop.

**French backup:**
Ce projet montre que les jeunes filles peuvent construire des solutions concrètes pour la cybersécurité locale.

---

## 4:50–5:10 — Closing

**English:**
Our final message is: SMS safety should become a habit. With SMS Scam Detector, we help people pause, verify and avoid fraud. Thank you.

**French backup:**
La cybersécurité doit être simple, locale et compréhensible par toutes et tous. Merci.

---

# Difficult judge questions and strong answers

## Q1. Why Logistic Regression instead of deep learning?

**Answer:**
For this hackathon stage, we need a model that is fast, stable, explainable and easy to retrain. Logistic Regression with TF-IDF is a strong NLP baseline, especially for short text classification. It also works offline and lets us focus on user trust and product quality. Later, we can compare it with SVM, Naive Bayes and transformer models.

## Q2. How will this work in French or Cameroonian local expressions?

**Answer:**
The current prototype already includes French and English examples. The architecture is language-flexible because TF-IDF learns from the training text and the rule layer includes French/English risk words. The next step is to collect anonymized local examples and evaluate performance separately by language.

## Q3. What if a scam message has no link?

**Answer:**
That is why we do not rely only on links. We also detect phone numbers, urgency, threats, money context, PIN/OTP requests, rewards and suspicious action words. A message can still be risky without a link if it asks for money, PIN, OTP or urgent action.

## Q4. What is the biggest risk of your system?

**Answer:**
False negatives are the biggest risk — when the system misses a scam. Our improvement plan prioritizes smishing recall and high-risk threshold tuning. We also present the tool as an assistant, not as a replacement for human caution.

## Q5. How can this become a real product?

**Answer:**
There are three possible paths: a public education web app, a school/community awareness tool, or an API that can be integrated into messaging or telecom safety systems. The first step is a pilot with anonymized data and user feedback.

## Q6. How do you protect user privacy?

**Answer:**
The prototype runs locally and does not need to send messages to an external server. For future data collection, we would anonymize phone numbers, names and personal details before training. We also avoid storing live user messages unless consent is given.
