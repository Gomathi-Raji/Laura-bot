# 🤖 Zara Voice Assistant - Web UI

A beautiful and intuitive Streamlit-based web interface for the Zara Voice Assistant.

## ✨ Features

### 🎛️ **Control Panel**
- **Real-time Status Display** - Shows current system status and mode
- **Voice Control Buttons** - Start/stop voice recognition with one click
- **Quick Action Buttons** - Direct access to all features
- **Manual Text Input** - Type commands when voice isn't available

### 💬 **Live Conversation**
- **Real-time Chat Interface** - See conversations as they happen
- **Message History** - Scrollable conversation log with timestamps
- **Live Transcription** - See what you're saying in real-time
- **Color-coded Messages** - Distinct styling for user and assistant messages

### 📊 **System Monitoring**
- **Feature Status** - Real-time status of all system components
- **Session Statistics** - Track usage and performance
- **System Controls** - Clear logs, export data, refresh interface

## 🚀 Quick Start

### Method 1: Using the Launcher
```bash
python launcher.py
```
Then select option 2 for Web UI.

### Method 2: Direct Launch  
```bash
streamlit run app_ui.py
```

### Method 3: One-Click Start
Double-click `start.bat` (Windows)

## 🎯 How to Use

### 1. **Voice Control**
- Click "🎙️ Start Listening" 
- Speak your command clearly
- Watch the live transcription
- See the response in the chat

### 2. **Quick Actions**
- **🎵 Play Music** - Search and play songs on Spotify
- **🤲 Gesture Recognition** - Launch gesture control window  
- **🌍 Translator** - Start Tamil-Hindi translation
- **🎬 GIF Display** - Show animated GIFs for words

### 3. **Text Input**
- Type commands in the text box
- Click "Send" to process
- Great for when microphone isn't available

### 4. **System Management**
- Monitor all system features in real-time
- Export conversation logs
- Clear chat history
- Refresh interface

## 🎨 Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│                   🤖 Zara Voice Assistant                │
├─────────────┬─────────────────────────┬─────────────────┤
│  🎛️ Controls │      💬 Conversation     │  📊 System Info │
│             │                         │                 │
│ • Status    │  ┌─ User: Hello        │ • Feature Status│
│ • Voice     │  └─ Zara: Hi there!    │ • Session Stats │  
│ • Features  │                         │ • Quick Actions│
│ • Text Input│  [Live Transcription]   │ • Export/Clear │
└─────────────┴─────────────────────────┴─────────────────┘
```

## 🎭 Available Commands

### Voice Commands
- **"play [song name]"** - Play music on Spotify
- **"translator"** - Start Tamil-Hindi translation  
- **"gesture"** - Open gesture recognition
- **"gif"** - Show GIF animations
- **"hello/yes/no/thank you"** - Trigger specific GIFs

### Tamil Commands  
- **"பாடல் இசை"** - Play music
- **"மொழிபெயர்ப்பு"** - Start translator
- **"கை சைகை"** - Gesture control
- **"GIF காட்டு"** - Show GIFs

## 🛠️ Technical Features

### Real-time Updates
- Auto-refresh every second during voice input
- Live status monitoring
- Instant message display

### Multi-threaded Processing
- Non-blocking voice recognition
- Background task processing  
- Responsive UI during operations

### Data Management
- Conversation logging to file
- JSON export functionality
- Session state persistence

### Error Handling
- Graceful error recovery
- User-friendly error messages
- System status indicators

## 📱 Responsive Design

- **Wide Layout** - Optimized for desktop use
- **Color-coded Status** - Visual feedback for all states
- **Intuitive Controls** - Large, clearly labeled buttons
- **Professional Styling** - Modern gradient design

## 🔧 Configuration

Edit `ui_config.json` to customize:
- Theme settings
- Refresh intervals  
- Display options
- Feature toggles

## 📊 System Requirements

- **Python 3.7+**
- **Streamlit 1.28+**
- **Web browser** (Chrome, Firefox, Edge)
- **Microphone** (for voice input)
- **Internet connection** (for AI and Spotify)

## 🎯 Pro Tips

1. **Use Chrome/Edge** for best microphone support
2. **Allow microphone access** when prompted
3. **Keep the window active** for real-time updates
4. **Export logs regularly** to save conversations
5. **Use text input** as backup for voice commands

## 🆘 Troubleshooting

### Voice Not Working?
- Check microphone permissions
- Try text input instead
- Refresh the page

### Commands Not Processing?
- Check system status indicator
- Look for error messages in red
- Try refreshing the interface

### Spotify Not Opening?
- Ensure internet connection
- Check if default browser is set
- Try manual search in Spotify

---

🤖 **Enjoy your enhanced Zara Voice Assistant experience!**
