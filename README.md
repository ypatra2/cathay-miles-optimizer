# ✈️ Cathay Miles ✨ AI Optimizer

An intelligent, meticulously designed web application that instantly determines the optimal credit card to use for any transaction to maximize your Cathay Asia Miles. 

Powered by **Google Gemini 1.5 Flash Vision API** and **Streamlit**, this app features a premium dark-mode, glassmorphism UI capable of automatically reading physical receipts, restaurant bills, and online checkout screenshots to bypass the tedious manual entry process.

## ✨ Features
- **AI Receipt Parsing:** Upload an image of your bill or checkout screen. The app securely interfaces with Gemini Vision AI to instantly parse the vendor, amount, and mapped spending category.
- **Deterministic Math Engine:** Ensures absolute mathematical accuracy by segregating the visual extraction (Gemini) from the miles calculation (Python Backend). Based on verified 2024–2025 reward earn rates.
- **Dynamic Override System:** Uses intelligent Streamlit Session State caching to allow seamless manual parameter tweaking safely without firing redundant or expensive API calls. 
- **Premium Interface:** A completely bespoke, responsive dual-pane UI mimicking modern dark-mode design with fluid layouts on both desktop and mobile views.

## 💳 Supported Cards (Hong Kong)
1. **Standard Chartered Cathay Mastercard**
2. **HSBC EveryMile VISA**
3. **HSBC Red Mastercard**
4. **HSBC VISA Signature**

## 🚀 Setup & Installation

### Standard Python Execution
1. Clone the repository:
   ```bash
   git clone https://github.com/ypatra2/cathay-miles-optimizer.git
   cd cathay-miles-optimizer
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your Google AI Studio API Key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
4. Run the Streamlit server:
   ```bash
   streamlit run app.py
   ```

## 🔐 Security & Privacy
This repository actively uses `.gitignore` to protect `.env` files. Your API keys are never tracked or uploaded. The AI Vision processing operates purely in-memory through strict `requests.post` REST arrays and does not permanently store your securely uploaded receipts on the disk.

## ⚠️ Notes for Regional Users
The Google AI API is natively geo-blocked in specific regions like Hong Kong. This application contains a robust, graceful 400 validation intercept. If you reside in a geoblocked region, ensure your device's global network (not just your browser) is tunneled through a supported VPN (such as ProtonVPN or Windscribe) prior to clicking analyze!
