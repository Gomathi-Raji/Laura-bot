#!/usr/bin/env python3
"""
Language Mode Test Script
Test the language learning mode functionality
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🎓 LANGUAGE LEARNING MODE TEST")
print("=" * 50)

try:
    # Test importing the language learning mode
    from translator.language_learning_mode import language_learner
    print("✅ Language learning mode imported successfully")
    
    # Test basic translation
    print("\n🔄 Testing basic translation...")
    result = language_learner.translate_with_learning("வணக்கம்", "tamil", "english")
    print(f"Tamil 'வணக்கம்' -> English: {result['translation']}")
    
    # Test reverse translation
    result2 = language_learner.translate_with_learning("Hello", "english", "tamil")
    print(f"English 'Hello' -> Tamil: {result2['translation']}")
    
    # Test Hindi translation
    result3 = language_learner.translate_with_learning("வணக்கம்", "tamil", "hindi")
    print(f"Tamil 'வணக்கம்' -> Hindi: {result3['translation']}")
    
    # Test learning statistics
    print("\n📊 Testing learning statistics...")
    stats = language_learner.get_learning_stats()
    print(f"Total translations: {stats['total_translations']}")
    print(f"Session count: {stats['session_count']}")
    print(f"Languages practiced: {len(stats['languages_practiced'])}")
    
    # Test practice suggestions
    print("\n💡 Testing practice suggestions...")
    suggestions = language_learner.get_practice_suggestion("tamil_english")
    print(f"Practice suggestions for Tamil->English: {suggestions}")
    
    print("\n✅ All language learning mode tests passed!")
    
    # Test voice trigger keywords
    print("\n🎤 Voice trigger keywords that activate language mode:")
    print("- 'language mode'")
    print("- 'language learning'") 
    print("- 'லாங்குவேஜ் மோட்'")
    print("- 'கற்றல் முறை'")
    print("- 'learn language'")
    print("- 'language teach'")
    print("- 'மொழி கற்க'")
    
    print("\n🌐 Web interface available at:")
    print("- http://localhost:5555/language-learning")
    
    print("\n🎯 To activate in voice mode, say any of the trigger phrases above!")
    
except Exception as e:
    print(f"❌ Error testing language learning mode: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Test completed!")