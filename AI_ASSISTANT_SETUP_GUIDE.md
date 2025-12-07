# EcoLearn AI Assistant - Setup Guide

## ✅ What's Been Created

### 1. Models (`ai_assistant/models.py`)
- `ChatSession` - Stores user chat sessions
- `ChatMessage` - Individual messages (user & assistant)
- `AssistantFeedback` - User ratings and feedback

### 2. Views (`ai_assistant/views.py`)
- `chat_interface` - Main chat page
- `send_message` - Send message to Gemini AI
- `get_session_messages` - Load chat history
- `new_session` - Start new conversation
- `delete_session` - Delete chat history
- `submit_feedback` - Rate AI responses

### 3. URLs (`ai_assistant/urls.py`)
- `/ai-assistant/` - Chat interface
- `/ai-assistant/send/` - Send message API
- `/ai-assistant/session/<id>/` - Get session
- `/ai-assistant/session/new/` - New session
- `/ai-assistant/feedback/` - Submit feedback

### 4. Admin (`ai_assistant/admin.py`)
- Manage chat sessions
- View conversations
- Monitor feedback

---

## 🚀 Next Steps

### Step 1: Install Google Generative AI Package
```bash
pip install google-generativeai
```

### Step 2: Get Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your API key

### Step 3: Add API Key to .env
```env
GEMINI_API_KEY=your-actual-api-key-here
```

### Step 4: Run Migrations
```bash
python manage.py makemigrations ai_assistant
python manage.py migrate
```

### Step 5: Create the Chat Template
Create `ai_assistant/templates/ai_assistant/chat.html` (see template below)

### Step 6: Add AI Button to Navbar
Add this to `templates/base.html` in the navbar:
```html
<a href="{% url 'ai_assistant:chat' %}" class="text-gray-700 hover:text-eco-green transition-colors">
    <i class="fas fa-robot mr-1"></i> AI Assistant
</a>
```

---

## 📱 Features

### What the AI Can Help With:
1. **Navigation** - Guide users to different pages
2. **Feature Explanation** - Explain how to use features
3. **Waste Management Tips** - Environmental advice
4. **Module Recommendations** - Suggest learning paths
5. **Troubleshooting** - Help with common issues
6. **Multilingual Support** - Respond in English, Bemba, or Nyanja

### System Context Provided to AI:
- All platform features
- Navigation URLs
- User roles and permissions
- Community features
- Learning modules
- Reporting system

---

## 🎨 Chat Interface Features

### User Experience:
- ✅ Real-time chat interface
- ✅ Chat history saved
- ✅ Multiple sessions
- ✅ Delete conversations
- ✅ Rate responses
- ✅ Mobile responsive

### AI Capabilities:
- ✅ Context-aware responses
- ✅ Navigation assistance
- ✅ Feature explanations
- ✅ Environmental tips
- ✅ Personalized help

---

## 🔧 Configuration

### Gemini Model Settings
Currently using: `gemini-pro`

You can customize in `ai_assistant/views.py`:
```python
model = genai.GenerativeModel('gemini-pro')
```

### System Context
Edit `get_system_context()` in `views.py` to customize AI behavior

### Message History
Currently keeps last 20 messages for context
Adjust in `send_message()` view

---

## 📊 Admin Features

### Monitor Usage:
- View all chat sessions
- Read conversations
- Check user feedback
- Identify common questions

### Analytics:
- Most asked questions
- User satisfaction ratings
- Feature usage patterns
- Popular topics

---

## 🎯 Example Interactions

### User: "How do I report illegal dumping?"
**AI Response:**
"To report illegal dumping on EcoLearn:
1. Click 'Report' in the navigation menu
2. Or go directly to /reporting/report/
3. Upload photos of the site
4. Add GPS location (automatic)
5. Provide description
6. Submit anonymously if preferred

Your report will be forwarded to local authorities!"

### User: "What modules should I start with?"
**AI Response:**
"Great question! I recommend starting with:
1. Introduction to Waste Segregation
2. Recycling Basics
3. Sustainable Disposal Practices

Visit /elearning/modules/ to browse all modules. They're available in English, Bemba, and Nyanja!"

### User: "Ndefwaya ukufunda mu Bemba"
**AI Response:**
"Ee! Twali na modules yonse mu Bemba. Pitani ku /elearning/modules/ elyo musankhe 'Bemba' mu language selector. Mwakwata modules ya:
- Waste segregation
- Recycling
- Community cleanup

Mwatendeka!"

---

## 🔐 Security

### API Key Protection:
- ✅ Stored in .env file
- ✅ Never committed to git
- ✅ Loaded via django-decouple

### User Privacy:
- ✅ Chats linked to user accounts
- ✅ Users can delete their history
- ✅ No PII sent to Gemini
- ✅ Feedback is optional

---

## 🐛 Troubleshooting

### "API Key not found"
- Check `.env` file has `GEMINI_API_KEY=...`
- Restart Django server after adding key

### "Module not found: google.generativeai"
- Run: `pip install google-generativeai`

### "No response from AI"
- Check API key is valid
- Verify internet connection
- Check Gemini API status

### "Template not found"
- Create `ai_assistant/templates/ai_assistant/` directory
- Add `chat.html` template

---

## 📈 Future Enhancements

### Planned Features:
- [ ] Voice input/output
- [ ] Image analysis (identify waste types)
- [ ] Proactive suggestions
- [ ] Integration with user progress
- [ ] Scheduled tips and reminders
- [ ] Group chat support
- [ ] Export conversations

---

## 📞 Support

### For Users:
- Click feedback button in chat
- Rate responses (1-5 stars)
- Add comments for improvement

### For Admins:
- Monitor feedback in Django admin
- Review chat logs
- Adjust system context as needed

---

**Status**: ✅ Backend Complete - Template Needed
**Next**: Create chat.html template and add navbar button
**Access**: `/ai-assistant/` (after template creation)
