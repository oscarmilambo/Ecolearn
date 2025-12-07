# 🤖 Gemini AI API Setup Guide

## Step 1: Get Your API Key

1. **Visit Google AI Studio:**
   - Go to: https://makersuite.google.com/app/apikey
   - Sign in with your Google account

2. **Create API Key:**
   - Click "Create API Key"
   - Choose "Create API key in new project" (recommended)
   - Copy the generated key (starts with `AIzaSy...`)

## Step 2: Update Your .env File

Replace the placeholder in your `.env` file:

```env
# Replace this line:
GEMINI_API_KEY=your-new-api-key-here

# With your actual key:
GEMINI_API_KEY=AIzaSyYourActualKeyHere...
```

## Step 3: Test the API

Run the test script:
```bash
python test_gemini_api.py
```

You should see:
```
✅ API Key loaded: AIzaSyYou...Here
✅ google.generativeai imported successfully
✅ Gemini configured with API key
✅ Gemini model initialized
✅ API Response: Hello from EcoLearn AI!
🎉 SUCCESS: Gemini API is working correctly!
```

## Step 4: Restart Django Server

After updating the API key:
```bash
python manage.py runserver
```

## Step 5: Test AI Assistant

1. Go to: http://localhost:8000/ai-assistant/
2. Try asking: "How do I start learning about waste management?"
3. You should get a helpful response!

## Troubleshooting

### ❌ "API key not valid"
- Double-check you copied the full key
- Make sure there are no extra spaces
- Verify the key is active in Google AI Studio

### ❌ "Module not found: google.generativeai"
```bash
pip install google-generativeai
```

### ❌ "GEMINI_API_KEY not found"
- Check your .env file exists in project root
- Restart Django server after changes
- Verify no typos in variable name

## API Key Security

✅ **DO:**
- Keep your API key in .env file
- Add .env to .gitignore
- Use environment variables in production

❌ **DON'T:**
- Commit API keys to git
- Share keys publicly
- Hardcode keys in source code

## Usage Limits

- **Free Tier:** 15 requests per minute
- **Rate Limits:** Automatically handled by the app
- **Quota:** Monitor usage in Google AI Studio

---

**Next:** Once working, your AI Assistant will help users with:
- Platform navigation
- Learning module recommendations  
- Waste management tips
- Community features
- Multilingual support (English, Bemba, Nyanja)