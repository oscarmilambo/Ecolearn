# 🤖 AI Assistant - Quick Start Guide

## Current Status: ⚠️ API Key Needed

The AI Assistant is **fully implemented** but needs a valid API key to work.

---

## 🚀 Quick Fix (2 minutes)

### Step 1: Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the new API key (starts with `AIzaSy...`)

### Step 2: Update .env File
Open your `.env` file and replace:
```env
GEMINI_API_KEY=your-new-api-key-here
```

With your actual key:
```env
GEMINI_API_KEY=AIzaSyYourActualKeyHere...
```

### Step 3: Test It Works
```bash
python test_ai_assistant_complete.py
```

### Step 4: Start Server & Test
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/ai-assistant/

---

## ✅ What's Already Working

### 🎯 Features Implemented:
- ✅ Real-time chat interface
- ✅ Chat history & sessions
- ✅ Multiple conversations
- ✅ Mobile responsive design
- ✅ User authentication
- ✅ Database storage
- ✅ Error handling

### 🧠 AI Capabilities:
- ✅ Navigation assistance
- ✅ Feature explanations
- ✅ Environmental tips
- ✅ Waste management advice
- ✅ Multi-language support (English, Bemba, Nyanja)
- ✅ Context-aware responses

### 🔗 Integration:
- ✅ Navbar button added
- ✅ User sessions linked
- ✅ Django admin integration
- ✅ URL routing configured

---

## 🎮 How to Use

### For Users:
1. Click **"AI Assistant"** in the navbar
2. Type questions like:
   - "How do I report illegal dumping?"
   - "What modules should I start with?"
   - "Ndefwaya ukufunda mu Bemba" (I want to learn in Bemba)
   - "How do I join a cleanup group?"

### For Admins:
- View chat logs in Django admin
- Monitor user feedback
- See popular questions

---

## 🔧 Technical Details

### Files Created:
- `ai_assistant/models.py` - Database models
- `ai_assistant/views.py` - Chat logic & Gemini integration
- `ai_assistant/urls.py` - URL routing
- `ai_assistant/templates/ai_assistant/chat.html` - Chat interface
- `ai_assistant/admin.py` - Admin interface

### Database Tables:
- `ChatSession` - User chat sessions
- `ChatMessage` - Individual messages
- `AssistantFeedback` - User ratings

### API Integration:
- Uses Google Gemini Pro model
- Maintains conversation context
- Handles errors gracefully
- Provides system context about EcoLearn

---

## 🐛 Troubleshooting

### "API Key not found"
- Check `.env` file has correct key
- Restart Django server after changes

### "Loading..." forever
- Invalid API key - get new one from Google AI Studio
- Check browser console for errors

### "Template not found"
- Template already created at `ai_assistant/templates/ai_assistant/chat.html`

### "Module not found"
- Package already installed: `google-generativeai`

---

## 🎯 Example Conversations

### Navigation Help:
**User:** "How do I find learning modules?"
**AI:** "To access learning modules on EcoLearn:
1. Click 'Learning' in the navigation menu
2. Or go directly to /elearning/modules/
3. Browse by category or search for topics
4. Modules are available in English, Bemba, and Nyanja!"

### Environmental Advice:
**User:** "Best practices for waste segregation?"
**AI:** "Here are key waste segregation practices:
1. Separate organic waste (food scraps, garden waste)
2. Sort recyclables (plastic, paper, glass, metal)
3. Keep hazardous waste separate (batteries, chemicals)
4. Use labeled bins for each category
5. Check our 'Waste Segregation' module for detailed guidance!"

### Multi-language:
**User:** "Ndefwaya ukufunda mu Bemba"
**AI:** "Ee! Twali na modules yonse mu Bemba. Pitani ku /elearning/modules/ elyo musankhe 'Bemba' mu language selector. Mwakwata modules ya waste segregation, recycling, ne community cleanup!"

---

## 🚀 Ready to Go!

Once you add the API key, your AI Assistant will be fully functional and ready to help users navigate EcoLearn and learn about environmental practices!

**Test URL:** http://127.0.0.1:8000/ai-assistant/